# ai_layer.py
# BioInterface — AI Intelligence Layer
# Version 1.0 | Builder: Anu Kozhiyalam
#
# Companion file to field_01_biopharma_v2.py
# Adds 8 AI-powered functions using the Anthropic Claude API.
# Run history stored in Supabase.
#
# Setup:
#   1. Create .env file in this folder:
#      ANTHROPIC_API_KEY=your-key-here
#      SUPABASE_URL=your-supabase-project-url
#      SUPABASE_KEY=your-supabase-anon-key
#   2. Run: pip install anthropic supabase python-dotenv
#   3. Create the three Supabase tables (SQL below in comments)
#   4. Run: python ai_layer.py
#
# Supabase tables needed — run these in your Supabase SQL editor:
#
#   CREATE TABLE run_records (
#       id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#       run_id text NOT NULL,
#       assay_id text NOT NULL,
#       batch_id text,
#       sample_id text,
#       sample_type text,
#       protocol_version text DEFAULT '2.0',
#       timestamp timestamptz DEFAULT now(),
#       acceptance_outcomes jsonb,
#       raw_results jsonb,
#       status text CHECK (status IN ('pass','fail','partial','invalidated')),
#       notes text
#   );
#
#   CREATE TABLE sensor_logs (
#       id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#       run_id text NOT NULL,
#       assay_id text NOT NULL,
#       timestamp timestamptz DEFAULT now(),
#       readings jsonb NOT NULL
#   );
#
#   CREATE TABLE instrument_health (
#       id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#       instrument_id text NOT NULL,
#       assay_id text NOT NULL,
#       run_id text NOT NULL,
#       timestamp timestamptz DEFAULT now(),
#       health_metrics jsonb NOT NULL
#   );


import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import voyageai

VOYAGE_KEY = os.environ.get("VOYAGE_API_KEY")
if VOYAGE_KEY:
    _voyage_client = voyageai.Client(api_key=VOYAGE_KEY)
else:
    _voyage_client = None


def embed_query(text: str) -> list:
    """Generate embedding for a search query.

    Uses input_type='query' which is optimised for
    retrieval (vs 'document' used during ingestion).
    """
    if not _voyage_client:
        raise RuntimeError("VOYAGE_API_KEY not set in .env")
    result = _voyage_client.embed(
        [text],
        model="voyage-3",
        input_type="query",
    )
    return result.embeddings[0]


def search_corpus(
    query: str,
    top_k: int = 5,
    source_type: str = None,
    use_hybrid: bool = True,
    vector_weight: float = 0.7,
) -> list:
    """Search the knowledge corpus.

    Uses hybrid search (vector + keyword) by default.
    Set use_hybrid=False for pure vector search.
    """
    try:
        # Auto-tune vector_weight by query shape:
        # Short ID-token queries (e.g. "BIO_005", "HTS_002")
        # benefit from keyword-heavy weighting
        if len(query.split()) <= 2 and any(
            '_' in t for t in query.split()
        ):
            vector_weight = 0.3

        query_embedding = embed_query(query)
        sb = _get_supabase()

        if use_hybrid:
            result = sb.rpc(
                "hybrid_search_corpus",
                {
                    "query_text": query,
                    "query_embedding": query_embedding,
                    "match_count": top_k * 2,
                    "vector_weight": vector_weight,
                },
            ).execute()
            chunks = result.data or []

            # Apply source_type filter post-hoc
            if source_type:
                chunks = [c for c in chunks if c["source_type"] == source_type]

            chunks = chunks[:top_k]

            # Normalize the response shape — UI expects 'similarity'
            for c in chunks:
                c["similarity"] = c.get(
                    "hybrid_score", c.get("vector_similarity", 0)
                )

            return chunks
        else:
            result = sb.rpc(
                "match_corpus",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "filter_source_type": source_type,
                },
            ).execute()
            return result.data or []

    except Exception as e:
        print(f"search_corpus error: {e}")
        import traceback
        traceback.print_exc()
        return []


def search_corpus_reranked(
    query: str,
    top_k: int = 5,
    source_type: str = None,
) -> list:
    """Two-stage retrieval — hybrid search retrieves top 10
    candidates, then Claude re-ranks them by actual relevance.

    Returns top_k chunks ranked by Claude's judgement.
    """
    # Classify query intent for source weighting
    intent = classify_query_intent(query)

    # Auto-tune vector_weight for ID-token queries
    vector_weight = 0.7
    if len(query.split()) <= 2 and any('_' in t for t in query.split()):
        vector_weight = 0.3

    # Source-weighted retrieval (pgsql function source_weighted_search)
    try:
        query_embedding = embed_query(query)
        sb = _get_supabase()
        result = sb.rpc(
            "source_weighted_search",
            {
                "query_text": query,
                "query_embedding": query_embedding,
                "match_count": 10,
                "vector_weight": vector_weight,
                "regulatory_weight": intent["regulatory_weight"],
                "library_weight": intent["library_weight"],
            },
        ).execute()
        candidates = result.data or []
        for c in candidates:
            c["similarity"] = c.get("hybrid_score", 0)
            c["query_intent"] = intent["intent"]
    except Exception as e:
        print(f"Source-weighted search failed, falling back to hybrid: {e}")
        candidates = search_corpus(
            query, top_k=10, source_type=source_type, use_hybrid=True
        )

    if source_type:
        candidates = [c for c in candidates if c["source_type"] == source_type]

    if len(candidates) <= top_k:
        return candidates

    chunks_for_ranking = "\n\n".join([
        f"[Chunk {i}]\nSource: {c['source_file']}\nContent: {c['content'][:600]}"
        for i, c in enumerate(candidates)
    ])

    rerank_prompt = f"""Rate the relevance of each chunk to this query on a scale of 0-10.

Query: {query}

Chunks to rate:
{chunks_for_ranking}

Return JSON only — no markdown fences:
{{"rankings": [
  {{"chunk_index": 0, "score": 8.5, "reason": "..."}},
  {{"chunk_index": 1, "score": 7.0, "reason": "..."}}
]}}"""

    try:
        response = _call_claude(
            "You are a precision retrieval ranker. "
            "Rate relevance honestly — bad matches get low scores.",
            rerank_prompt,
            expect_json=True,
            max_tokens=2000,
            model="claude-sonnet-4-6",
        )
        import json
        rankings = json.loads(response)["rankings"]

        rankings.sort(key=lambda r: r["score"], reverse=True)
        top_rankings = rankings[:top_k]
        top_indices = [r["chunk_index"] for r in top_rankings]

        reranked = []
        for r in top_rankings:
            i = r["chunk_index"]
            if 0 <= i < len(candidates):
                chunk = candidates[i]
                chunk["rerank_score"] = r["score"]
                chunk["rerank_reason"] = r.get("reason", "")
                reranked.append(chunk)

        return reranked

    except Exception as e:
        print(f"Re-ranking failed, returning hybrid results: {e}")
        return candidates[:top_k]


def classify_query_intent(query: str) -> dict:
    """Classify query to determine source weighting.

    Returns:
        {
            "intent": "regulatory|protocol|validation|stability|general",
            "regulatory_weight": 0.0 to 1.0,
            "library_weight": 0.0 to 1.0,
            "reasoning": "..."
        }
    """
    import re
    query_lower = query.lower()

    # Fast path 0: comparison queries that reference both
    # an assay ID AND a regulatory document
    has_assay_id = bool(re.search(
        r'\b(BIO|HTS)_\d{3}\b', query, re.IGNORECASE
    ))
    has_reg = any(kw in query_lower for kw in [
        'ich q', 'ich q5', 'ich q6', 'ich q14', 'ich q2',
        'fda guidance', 'fda guideline', 'usp <',
        'bla module', 'regulatory submission', 'q6b', 'q5c',
        'q5e', 'q14', 'q2(r2)',
    ])
    is_comparison = any(w in query_lower for w in [
        'compare', ' vs ', ' versus ', 'difference between',
        'what does', 'how does', 'requirements for',
        'aligned with', 'consistent with',
    ])
    if has_assay_id and has_reg and is_comparison:
        return {
            "intent": "comparison",
            "regulatory_weight": 0.50,
            "library_weight": 0.50,
            "reasoning": "Comparison query — both assay and regulatory references",
        }

    # Fast path 1: Direct assay ID match
    if re.search(r'\b(BIO|HTS)_\d{3}\b', query, re.IGNORECASE):
        return {
            "intent": "protocol",
            "regulatory_weight": 0.05,
            "library_weight": 0.95,
            "reasoning": "Direct assay ID reference",
        }

    # Fast path 2: Direct ICH/FDA/USP reference
    regulatory_keywords = [
        'ich q', 'ich q5', 'ich q6', 'ich q14', 'ich q2',
        'fda guidance', 'fda guideline', 'usp <',
        'bla module', 'regulatory submission',
    ]
    if any(kw in query_lower for kw in regulatory_keywords):
        return {
            "intent": "regulatory",
            "regulatory_weight": 0.90,
            "library_weight": 0.10,
            "reasoning": "Direct regulatory document reference",
        }

    # Default: use Claude for nuanced classification
    system_prompt = """Classify this biopharma analytical science query to determine source weighting.

Available sources:
- regulatory: ICH guidelines (Q2, Q5C, Q5E, Q6B, Q14), FDA guidance documents
- library: 30 robot-executable assay protocols (BIO_001 through BIO_018, HTS_001 through HTS_012)

Classify intent and assign weights. Total must sum to 1.0.

Return JSON only — no markdown fences:
{
    "intent": "regulatory|protocol|validation|stability|general",
    "regulatory_weight": 0.0 to 1.0,
    "library_weight": 0.0 to 1.0,
    "reasoning": "brief explanation"
}"""

    try:
        response = _call_claude(
            system_prompt,
            query,
            expect_json=True,
            max_tokens=300,
            model="claude-sonnet-4-6",
        )
        import json
        return json.loads(response)
    except Exception as e:
        return {
            "intent": "general",
            "regulatory_weight": 0.5,
            "library_weight": 0.5,
            "reasoning": f"Classification failed: {e}",
        }


def decompose_query(query: str) -> dict:
    """Decompose a complex query into sub-questions.

    Returns:
        {
            "needs_decomposition": bool,
            "sub_questions": [list of strings],
            "reasoning": "why this was/wasn't decomposed",
            "synthesis_strategy": "compare|combine|sequential"
        }
    """
    word_count = len(query.split())
    if word_count <= 10:
        return {
            "needs_decomposition": False,
            "sub_questions": [query],
            "reasoning": "Short query, single retrieval sufficient",
            "synthesis_strategy": "combine",
        }

    system_prompt = """You are a query decomposition specialist for biopharma analytical science RAG.

Given a complex query, decide if it needs to be broken into sub-questions for separate retrieval rounds.

Decompose if the query:
- References multiple distinct topics or documents
- Asks for comparisons across sources
- Requires combining regulatory + protocol knowledge
- Has 'and' joining clearly separable concepts

Do NOT decompose if:
- Query is asking about a single topic in depth
- Sub-questions would lose context
- Single retrieval would surface relevant chunks

When decomposing:
- Generate 2-4 sub-questions max
- Each sub-question should be self-contained
- Each should target distinct knowledge

Synthesis strategies:
- compare: results will be contrasted (different requirements)
- combine: results will be merged (multiple aspects of one topic)
- sequential: results build on each other (step-by-step)

Return JSON only — no markdown fences:
{
    "needs_decomposition": true,
    "sub_questions": [
        "ICH Q2 accuracy validation requirements",
        "FDA bioanalytical accuracy requirements",
        "charge variant analysis methods"
    ],
    "reasoning": "Query asks for comparison across two regulatory frameworks for a specific analytical context",
    "synthesis_strategy": "compare"
}"""

    try:
        response = _call_claude(
            system_prompt,
            query,
            expect_json=True,
            max_tokens=500,
            model="claude-sonnet-4-6",
        )
        import json
        return json.loads(response)
    except Exception as e:
        return {
            "needs_decomposition": False,
            "sub_questions": [query],
            "reasoning": f"Decomposition failed, using original: {e}",
            "synthesis_strategy": "combine",
        }


def search_corpus_multihop(
    query: str,
    top_k: int = 5,
    source_type: str = None,
    chunks_per_subquery: int = 5,
) -> dict:
    """Multi-hop retrieval for complex queries.

    Decomposes query, retrieves for each sub-question, merges results,
    and reranks against the original query.

    Returns:
        {
            "chunks": [final reranked chunks],
            "decomposition": {
                "sub_questions": [...],
                "synthesis_strategy": "...",
                "was_decomposed": bool
            },
            "retrieval_log": [{"sub_q": "...", "n_retrieved": N}, ...]
        }
    """
    decomp = decompose_query(query)
    retrieval_log = []

    if not decomp["needs_decomposition"]:
        chunks = search_corpus_reranked(query, top_k=top_k, source_type=source_type)
        retrieval_log.append({"sub_q": query, "n_retrieved": len(chunks)})
        return {
            "chunks": chunks,
            "decomposition": {
                "sub_questions": [query],
                "synthesis_strategy": "combine",
                "was_decomposed": False,
                "reasoning": decomp.get("reasoning", ""),
            },
            "retrieval_log": retrieval_log,
        }

    all_chunks = []
    seen_ids = set()

    for sub_q in decomp["sub_questions"]:
        sub_chunks = search_corpus_reranked(
            sub_q, top_k=chunks_per_subquery, source_type=source_type
        )
        retrieval_log.append({"sub_q": sub_q, "n_retrieved": len(sub_chunks)})

        for chunk in sub_chunks:
            cid = chunk.get("id")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                chunk["sub_query_match"] = sub_q
                all_chunks.append(chunk)

    # Final rerank against the ORIGINAL query
    if len(all_chunks) <= top_k:
        final_chunks = all_chunks
    else:
        chunks_for_ranking = "\n\n".join([
            f"[Chunk {i}]\nSource: {c['source_file']}\n"
            f"Sub-query matched: {c.get('sub_query_match', '')}\n"
            f"Content: {c['content'][:600]}"
            for i, c in enumerate(all_chunks)
        ])

        rerank_prompt = f"""Rate the relevance of each chunk to the ORIGINAL query (not the sub-queries) on a scale of 0-10.

Original query: {query}

Synthesis strategy: {decomp['synthesis_strategy']}

Chunks to rate:
{chunks_for_ranking}

Return JSON only — no markdown fences:
{{"rankings": [
  {{"chunk_index": 0, "score": 8.5, "reason": "..."}}
]}}"""

        try:
            response = _call_claude(
                "You are a precision retrieval ranker. "
                "Rate against the original query, considering the synthesis strategy.",
                rerank_prompt,
                expect_json=True,
                max_tokens=2500,
                model="claude-sonnet-4-6",
            )
            import json
            rankings = json.loads(response)["rankings"]
            rankings.sort(key=lambda r: r["score"], reverse=True)
            top_rankings = rankings[:top_k]

            final_chunks = []
            for r in top_rankings:
                i = r["chunk_index"]
                if 0 <= i < len(all_chunks):
                    chunk = all_chunks[i]
                    chunk["multihop_rerank_score"] = r["score"]
                    chunk["multihop_rerank_reason"] = r.get("reason", "")
                    final_chunks.append(chunk)
        except Exception as e:
            print(f"Multi-hop rerank failed, returning unranked: {e}")
            final_chunks = all_chunks[:top_k]

    return {
        "chunks": final_chunks,
        "decomposition": {
            "sub_questions": decomp["sub_questions"],
            "synthesis_strategy": decomp["synthesis_strategy"],
            "was_decomposed": True,
            "reasoning": decomp.get("reasoning", ""),
        },
        "retrieval_log": retrieval_log,
    }


def retrieval_quality_check(
    chunks: list,
    similarity_threshold: float = 0.35,
    min_relevant_chunks: int = 2,
    relevant_threshold: float = 0.3,
) -> dict:
    """Check if retrieval is good enough to generate a grounded answer.

    Returns:
        {
            "passed": bool,
            "verdict": "in_corpus|borderline|out_of_corpus",
            "top_similarity": float,
            "n_relevant": int,
            "source_diversity": int,
            "reason": "...",
            "recommendation": "proceed|warn|refuse"
        }
    """
    if not chunks:
        return {
            "passed": False,
            "verdict": "out_of_corpus",
            "top_similarity": 0.0,
            "n_relevant": 0,
            "source_diversity": 0,
            "reason": "No chunks retrieved",
            "recommendation": "refuse",
        }

    def score_of(c):
        return c.get(
            "rerank_score",
            c.get("multihop_rerank_score", c.get("similarity", 0)),
        )

    scores = [score_of(c) for c in chunks]
    max_score = max(scores) if scores else 0
    if max_score > 1.0:
        # rerank_score is 0-10, normalize to 0-1
        scores = [s / 10.0 for s in scores]

    top_similarity = max(scores) if scores else 0
    n_relevant = sum(1 for s in scores if s >= relevant_threshold)
    sources = set(c.get("source_file", "") for c in chunks)
    source_diversity = len(sources)

    if top_similarity >= 0.6 and n_relevant >= min_relevant_chunks:
        verdict = "in_corpus"
        passed = True
        recommendation = "proceed"
        reason = (
            f"Strong retrieval: top score {top_similarity:.2f}, "
            f"{n_relevant} relevant chunks across {source_diversity} sources"
        )
    elif top_similarity >= similarity_threshold and n_relevant >= 1:
        verdict = "borderline"
        passed = True
        recommendation = "warn"
        reason = (
            f"Moderate retrieval: top score {top_similarity:.2f}, "
            f"{n_relevant} relevant chunks. Answer may be partial."
        )
    else:
        verdict = "out_of_corpus"
        passed = False
        recommendation = "refuse"
        reason = (
            f"Weak retrieval: top score {top_similarity:.2f}, "
            f"{n_relevant} relevant chunks. "
            f"Topic likely outside corpus coverage."
        )

    return {
        "passed": passed,
        "verdict": verdict,
        "top_similarity": round(top_similarity, 3),
        "n_relevant": n_relevant,
        "source_diversity": source_diversity,
        "reason": reason,
        "recommendation": recommendation,
    }


def compute_retrieval_confidence(chunks: list, intent: dict = None) -> dict:
    """Compute calibrated confidence based on retrieval signals.

    Confidence factors:
    - Top chunk relevance score
    - Score gap between top chunk and second chunk
    - Number of high-relevance chunks
    - Source diversity
    - Intent classification certainty

    Returns:
        {
            "confidence": "high|medium|low",
            "score": 0-100,
            "factors": {
                "top_relevance": float,
                "score_gap": float,
                "n_high_relevance": int,
                "source_diversity": int,
                "intent_clear": bool
            },
            "reasoning": "..."
        }
    """
    if not chunks:
        return {
            "confidence": "low",
            "score": 0,
            "factors": {
                "top_relevance": 0,
                "score_gap": 0,
                "n_high_relevance": 0,
                "source_diversity": 0,
                "intent_clear": False,
            },
            "reasoning": "No chunks retrieved",
        }

    def score_of(c):
        # Anchor on raw cosine similarity — it's calibrated
        # against the full corpus. Rerank scores are relative
        # to the 10-candidate pool and can be misleading for
        # out-of-corpus queries (the "least bad" chunk gets
        # rated 10/10 even if absolutely irrelevant).
        return c.get("similarity", c.get("rerank_score", 0))

    scores = [score_of(c) for c in chunks]

    top_relevance = scores[0] if scores else 0
    second_relevance = scores[1] if len(scores) > 1 else 0
    score_gap = top_relevance - second_relevance
    n_high_relevance = sum(1 for s in scores if s >= 0.5)

    sources = set(c.get("source_file", "") for c in chunks)
    source_diversity = len(sources)

    # Intent clarity — balanced weights (~0.5/0.5) suggest unclear intent
    intent_clear = True
    if intent:
        reg_w = intent.get("regulatory_weight", 0.5)
        if 0.4 <= reg_w <= 0.6:
            intent_clear = False

    factors_score = (
        min(top_relevance * 40, 40)       # 0-40 pts (capped — hybrid_score can exceed 1.0)
        + min(score_gap * 100, 20)        # 0-20 pts
        + min(n_high_relevance * 10, 25)  # 0-25 pts
        + min(source_diversity * 5, 10)   # 0-10 pts
        + (5 if intent_clear else 0)      # 0-5 pts
    )
    factors_score = min(int(factors_score), 100)

    if factors_score >= 70:
        confidence = "high"
        reasoning = (
            f"Strong retrieval — top score {top_relevance:.2f}, "
            f"{n_high_relevance} highly relevant chunks across "
            f"{source_diversity} sources"
        )
    elif factors_score >= 45:
        confidence = "medium"
        reasoning = (
            f"Moderate retrieval — top score {top_relevance:.2f}, "
            f"{n_high_relevance} relevant chunks. "
            f"Answer is grounded but verify specifics."
        )
    else:
        confidence = "low"
        reasoning = (
            f"Weak retrieval — top score {top_relevance:.2f}. "
            f"Answer may be partial or imprecise."
        )

    return {
        "confidence": confidence,
        "score": factors_score,
        "factors": {
            "top_relevance": round(top_relevance, 3),
            "score_gap": round(score_gap, 3),
            "n_high_relevance": n_high_relevance,
            "source_diversity": source_diversity,
            "intent_clear": intent_clear,
        },
        "reasoning": reasoning,
    }


def suggest_related_topics(query: str, top_k: int = 5) -> list:
    """When a query falls out of corpus, suggest related topics
    that ARE covered. Returns a list of topic suggestions based
    on available source documents.
    """
    try:
        sb = _get_supabase()
        result = sb.table("knowledge_corpus").select(
            "source_file, source_type, metadata"
        ).execute()
        sources = result.data or []
    except Exception:
        return []

    source_summary = {}
    for s in sources:
        sf = s.get("source_file", "")
        if sf not in source_summary:
            source_summary[sf] = {
                "source_file": sf,
                "source_type": s.get("source_type", ""),
                "topics": set(),
            }
        meta = s.get("metadata") or {}
        if meta.get("assay_id"):
            source_summary[sf]["topics"].add(meta["assay_id"])

    corpus_map = []
    for sf, info in source_summary.items():
        if info["source_type"] == "regulatory":
            label = sf.replace(".pdf", "").replace("_", " ")
            corpus_map.append(f"- {label}")
        elif info["source_type"] == "assay_library":
            for topic in info["topics"]:
                corpus_map.append(f"- Assay {topic}")

    corpus_summary = "\n".join(corpus_map[:50])

    system_prompt = """The user asked a question that falls outside the BioInterface corpus. Suggest related topics that ARE covered in the corpus.

Be honest — if no related topics exist, return an empty list. Suggest 3-5 topics maximum.

Return JSON only — no markdown fences:
{
    "suggestions": [
        {
            "topic": "ICH Q2 method validation",
            "why_related": "covers validation framework that applies to your question"
        }
    ]
}"""

    user_msg = f"""Query: {query}

Corpus contains:
{corpus_summary}

Suggest related topics from the corpus that might help the user."""

    try:
        response = _call_claude(
            system_prompt,
            user_msg,
            expect_json=True,
            max_tokens=500,
            model="claude-sonnet-4-6",
        )
        import json
        return json.loads(response).get("suggestions", [])
    except Exception:
        return []


def expand_query_with_context(
    current_query: str,
    conversation_history: list,
) -> dict:
    """Expand a follow-up query using conversation history.

    Args:
        current_query: The new question
        conversation_history: List of prior turns:
            [{"query": "...", "answer_summary": "..."}]

    Returns:
        {
            "expanded_query": "self-contained query",
            "is_followup": bool,
            "reasoning": "..."
        }
    """
    if not conversation_history:
        return {
            "expanded_query": current_query,
            "is_followup": False,
            "reasoning": "First turn",
        }

    follow_up_indicators = [
        'what about', 'and for', 'what if', 'how about',
        'can you also', 'tell me more', 'similarly',
        'compared to', 'in contrast', 'instead',
    ]
    query_lower = current_query.lower()
    likely_followup = (
        any(ind in query_lower for ind in follow_up_indicators)
        or len(current_query.split()) <= 6
    )

    if not likely_followup:
        return {
            "expanded_query": current_query,
            "is_followup": False,
            "reasoning": "Self-contained query",
        }

    history_text = "\n".join([
        f"Turn {i+1}:\n  Q: {h['query']}\n  A summary: {h.get('answer_summary', '')[:200]}"
        for i, h in enumerate(conversation_history[-3:])
    ])

    system_prompt = """Expand this follow-up question into a self-contained query using the conversation history. The expanded query will be used for retrieval, so it must contain enough context to match relevant chunks without seeing the prior turns.

If the current query is already self-contained, return it unchanged.

Return JSON only — no markdown fences:
{
    "expanded_query": "self-contained version",
    "is_followup": true,
    "reasoning": "what context was added and why"
}"""

    user_msg = f"""Conversation history:
{history_text}

Current query: {current_query}

Expand this query if it relies on prior context."""

    try:
        response = _call_claude(
            system_prompt,
            user_msg,
            expect_json=True,
            max_tokens=400,
            model="claude-sonnet-4-6",
        )
        import json
        return json.loads(response)
    except Exception as e:
        return {
            "expanded_query": current_query,
            "is_followup": False,
            "reasoning": f"Expansion failed: {e}",
        }


def search_corpus_formatted(query: str, top_k: int = 5) -> str:
    """Search corpus and return formatted text for feeding into
    Claude as context. Returns one string with all top_k chunks
    formatted with source attribution.
    """
    chunks = search_corpus(query, top_k=top_k)
    if not chunks:
        return "No relevant chunks found in corpus."

    formatted = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["source_file"]
        sim = chunk["similarity"]
        content = chunk["content"]
        formatted.append(
            f"[Source {i} — {source} (relevance: {sim:.3f})]\n{content}\n"
        )
    return "\n---\n".join(formatted)


# ── Lazy imports — only fail if actually called, not on import ───────────
def _get_anthropic():
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("Run: pip install anthropic")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found. "
            "Add it to your .env file: ANTHROPIC_API_KEY=your-key-here"
        )
    return Anthropic(api_key=key)


def _get_supabase():
    try:
        from supabase import create_client
    except ImportError:
        raise ImportError("Run: pip install supabase")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL or SUPABASE_KEY not found in .env file."
        )
    return create_client(url, key)


# Import assay library — must be in the same folder
from field_01_biopharma_v2 import BIOPHARMA_ASSAYS, get_assay_by_id, get_all_assays
try:
    from field_04_drug_discovery_hts_v2 import HTS_ASSAYS
except ImportError:
    HTS_ASSAYS = []


def _find_assay(assay_id):
    """Look up an assay across every loaded field library."""
    for a in BIOPHARMA_ASSAYS + HTS_ASSAYS:
        if a.get("assay_id") == assay_id:
            return a
    return None


CLAUDE_MODEL = "claude-sonnet-4-6"


def _call_claude(system_prompt: str, user_prompt: str, expect_json: bool = True, max_tokens: int = 1500, model: str = None) -> str:
    """Internal helper. One call to Claude, returns response text."""
    claude = _get_anthropic()
    system = system_prompt
    if expect_json:
        system += (
            "\n\nCRITICAL: Respond ONLY with valid JSON. "
            "No preamble, no explanation, no markdown code fences."
        )
    response = claude.messages.create(
        model=model or CLAUDE_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user_prompt}],
        system=system,
    )
    text = response.content[0].text.strip()
    if expect_json and text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


# ─────────────────────────────────────────────────────────────
# SUPABASE HELPERS
# ─────────────────────────────────────────────────────────────

def store_run_record(
    run_id: str,
    assay_id: str,
    batch_id: str,
    sample_id: str,
    sample_type: str,
    acceptance_outcomes: dict,
    raw_results: dict,
    status: str,
    notes: str = "",
    protocol_version: str = "2.0"
) -> dict:
    """
    Save a completed assay run to Supabase.
    status: 'pass', 'fail', 'partial', or 'invalidated'

    Example:
        store_run_record(
            run_id="RUN-2024-001",
            assay_id="BIO_001",
            batch_id="CHO-047-DS-031",
            sample_id="CHO-047-S01",
            sample_type="post_protein_a_eluate",
            acceptance_outcomes={"standard_curve_r2": "PASS 0.9991",
                                 "qc_recovery": "FAIL 78%"},
            raw_results={"titer_mg_mL": 4.2, "r2": 0.9991},
            status="fail",
            notes="QC recovery below spec."
        )
    """
    sb = _get_supabase()
    record = {
        "run_id": run_id,
        "assay_id": assay_id,
        "batch_id": batch_id,
        "sample_id": sample_id,
        "sample_type": sample_type,
        "protocol_version": protocol_version,
        "timestamp": datetime.utcnow().isoformat(),
        "acceptance_outcomes": acceptance_outcomes,
        "raw_results": raw_results,
        "status": status,
        "notes": notes,
    }
    response = sb.table("run_records").insert(record).execute()
    print(f"[Supabase] Stored: {run_id} | {assay_id} | {status.upper()}")
    return response.data[0] if response.data else {}


def get_run_history(
    assay_id: str = None,
    batch_id: str = None,
    sample_type: str = None,
    limit: int = 50
) -> list:
    """Retrieve run records from Supabase. Filter by assay, batch, or sample type."""
    sb = _get_supabase()
    query = (
        sb.table("run_records")
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
    )
    if assay_id:
        query = query.eq("assay_id", assay_id)
    if batch_id:
        query = query.eq("batch_id", batch_id)
    if sample_type:
        query = query.eq("sample_type", sample_type)
    return query.execute().data or []


def store_sensor_log(run_id: str, assay_id: str, readings: dict) -> dict:
    """
    Save a live sensor reading during a robot run.
    Call every 60 seconds during a run for anomaly detection to work.

    Example readings:
        {"hplc_pressure_bar": 187, "uv_baseline_mau": 2.1, "column_temp_c": 25}
    """
    sb = _get_supabase()
    record = {
        "run_id": run_id,
        "assay_id": assay_id,
        "timestamp": datetime.utcnow().isoformat(),
        "readings": readings,
    }
    response = sb.table("sensor_logs").insert(record).execute()
    return response.data[0] if response.data else {}


def get_sensor_history(run_id: str, assay_id: str) -> list:
    """Retrieve all sensor readings for a specific run."""
    sb = _get_supabase()
    return (
        sb.table("sensor_logs")
        .select("*")
        .eq("run_id", run_id)
        .eq("assay_id", assay_id)
        .order("timestamp", desc=False)
        .execute()
        .data or []
    )


def store_instrument_health(
    instrument_id: str,
    assay_id: str,
    run_id: str,
    health_metrics: dict
) -> dict:
    """
    Log instrument health metrics after each run.

    Example health_metrics for HPLC:
        {"back_pressure_bar": 187, "retention_time_min": 3.42,
         "system_suitability_cv": 0.4, "injection_count": 412}
    """
    sb = _get_supabase()
    record = {
        "instrument_id": instrument_id,
        "assay_id": assay_id,
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "health_metrics": health_metrics,
    }
    response = sb.table("instrument_health").insert(record).execute()
    return response.data[0] if response.data else {}


def get_instrument_history(
    instrument_id: str, assay_id: str, limit: int = 30
) -> list:
    """Retrieve recent health metric history for an instrument."""
    sb = _get_supabase()
    data = (
        sb.table("instrument_health")
        .select("*")
        .eq("instrument_id", instrument_id)
        .eq("assay_id", assay_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
        .data or []
    )
    return list(reversed(data))  # chronological order


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 1 — REAL-TIME ANOMALY DETECTION
# ─────────────────────────────────────────────────────────────

def detect_run_anomaly(
    assay_id: str,
    run_id: str,
    current_readings: dict
) -> dict:
    """
    Monitor live sensor data during a robot run.
    Call every 60 seconds, passing the latest sensor readings.
    Returns PASS / WARN / STOP before a criterion is formally breached.

    Returns:
        {
            "status": "PASS" | "WARN" | "STOP",
            "reason": "one sentence",
            "recommendation": "what to do right now",
            "metrics_flagged": ["list of metric names"]
        }

    Example:
        result = detect_run_anomaly(
            assay_id="BIO_001",
            run_id="RUN-2024-001",
            current_readings={"hplc_pressure_bar": 284, "uv_baseline_mau": 2.1}
        )
    """
    assay = get_assay_by_id(assay_id)
    if not assay:
        return {
            "status": "ERROR",
            "reason": f"Assay {assay_id} not found.",
            "recommendation": "Check assay ID.",
            "metrics_flagged": []
        }

    recent_history = get_sensor_history(run_id, assay_id)
    history_summary = [r["readings"] for r in recent_history[-5:]]

    system_prompt = f"""You are a real-time quality monitor for a pharmaceutical robot automation system.
You monitor sensor readings during robot-executed assay runs and flag anomalies
before they cause acceptance criterion failures. Output conservative signals.
When in doubt, WARN rather than PASS.

Assay: {assay_id} — {assay['name']}
Acceptance criteria: {json.dumps(assay['acceptance_criteria'], indent=2)}
Platform: {assay['platform_compatibility']}"""

    user_prompt = f"""Current readings at {datetime.utcnow().strftime('%H:%M:%S')} UTC:
{json.dumps(current_readings, indent=2)}

Recent history (last 5 snapshots, oldest first):
{json.dumps(history_summary, indent=2) if history_summary else "No prior readings for this run."}

Return this exact JSON:
{{
  "status": "PASS" or "WARN" or "STOP",
  "reason": "one sentence explaining the status",
  "recommendation": "one sentence — what the operator should do right now",
  "metrics_flagged": ["list of concerning metric names, empty if PASS"]
}}"""

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))
        store_sensor_log(run_id, assay_id, current_readings)
        return result
    except Exception as e:
        return {
            "status": "ERROR",
            "reason": f"AI monitoring failed: {e}",
            "recommendation": "Review readings manually.",
            "metrics_flagged": []
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 2 — ROOT CAUSE ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────

def analyze_run_failure(
    assay_id: str,
    run_record: dict,
    failed_criteria: list
) -> dict:
    """
    When acceptance criteria fail, AI diagnoses why and recommends action.
    Replaces the 1-2 hour analyst investigation for common failure modes.

    Returns:
        {
            "most_likely_root_cause": "str",
            "contributing_factors": ["list"],
            "corrective_action": "str",
            "preventive_action": "str",
            "confidence": "high" | "medium" | "low",
            "requires_investigation": true | false
        }

    Example:
        result = analyze_run_failure(
            assay_id="BIO_006",
            run_record={"raw_results": {"ppc_recovery_pct": 38}, "notes": ""},
            failed_criteria=["ppc_recovery_percent"]
        )
    """
    assay = get_assay_by_id(assay_id)
    if not assay:
        return {
            "most_likely_root_cause": f"Assay {assay_id} not found.",
            "contributing_factors": [],
            "corrective_action": "Check assay ID.",
            "preventive_action": "",
            "confidence": "low",
            "requires_investigation": True
        }

    history = get_run_history(assay_id=assay_id, limit=20)
    recent_failures = [
        {
            "timestamp": r["timestamp"],
            "outcomes": r.get("acceptance_outcomes", {}),
            "notes": r.get("notes", "")
        }
        for r in history if r.get("status") in ("fail", "partial")
    ][-5:]

    system_prompt = f"""You are a GMP analytical scientist performing root cause analysis
for a failed biopharmaceutical assay run. Be specific, prioritised, and directly actionable.

Assay: {assay['name']} ({assay_id})
Purpose: {assay['purpose']}
Instruments: {', '.join(assay['instruments_needed'])}
Reagents: {', '.join(assay['reagents'])}
Acceptance criteria: {json.dumps(assay['acceptance_criteria'], indent=2)}
Known failure modes: {assay['notes']}"""

    rca_examples = """Examples of correct root cause analyses:

EXAMPLE 1 — clear root cause:
INPUT: BIO_001 Protein A titer; failed criteria = qc_recovery 76% (spec 85-115%); column_pressure_bar 291 (warn). Recent history shows 3 prior runs with rising column pressure (210→240→270 bar).
OUTPUT:
{
  "most_likely_root_cause": "Column aging (cumulative back-pressure increase) compromises QC recovery; column has reached end of qualified service life.",
  "contributing_factors": ["Column injection count near 500-injection limit", "Rising back-pressure trend over last 3 runs", "Sample matrix is consistent with prior runs, ruling out matrix effect"],
  "corrective_action": "Replace Protein A column and re-qualify with calibration standards before next run.",
  "preventive_action": "Implement automated injection-count tracking with hard stop at 480 injections.",
  "confidence": "high",
  "requires_investigation": false
}

EXAMPLE 2 — ambiguous cause:
INPUT: BIO_005 Sandwich ELISA; failed criteria = standard_curve_r2 0.987 (spec >= 0.995); intraplate_cv 18%. Recent history shows two prior runs passing, no equipment changes logged.
OUTPUT:
{
  "most_likely_root_cause": "Curve fit and CV degradation without equipment changes suggests a reagent lot effect, but plate handling cannot be ruled out.",
  "contributing_factors": ["Standard curve R^2 just below spec — borderline", "Elevated intraplate CV indicates non-uniform dispense or coating", "No change in equipment or operator logged"],
  "corrective_action": "Repeat run with fresh aliquot of capture antibody and tracking new substrate vial; rotate plate sealer.",
  "preventive_action": "Add a per-lot ELISA qualification control before deploying new reagent lots.",
  "confidence": "medium",
  "requires_investigation": true
}

Now analyze this run:

"""

    user_prompt = rca_examples + f"""Failed criteria: {json.dumps(failed_criteria, indent=2)}

Run record: {json.dumps(run_record, indent=2)}

Recent failure history (last 5):
{json.dumps(recent_failures, indent=2) if recent_failures else "No prior failures on record."}

Return this exact JSON:
{{
  "most_likely_root_cause": "one clear sentence",
  "contributing_factors": ["factor 1", "factor 2", "factor 3"],
  "corrective_action": "specific action before the next run",
  "preventive_action": "systemic change to prevent recurrence",
  "confidence": "high or medium or low",
  "requires_investigation": true or false
}}"""

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))
        print(f"[RCA] {assay_id} | {result.get('most_likely_root_cause', '')[:80]}")
        return result
    except Exception as e:
        return {
            "most_likely_root_cause": f"AI RCA failed: {e}",
            "contributing_factors": [],
            "corrective_action": "Manual review required.",
            "preventive_action": "",
            "confidence": "low",
            "requires_investigation": True
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 3 — INTELLIGENT DILUTION PREDICTOR
# ─────────────────────────────────────────────────────────────

def predict_optimal_dilution(
    assay_id: str,
    sample_type: str,
    sample_metadata: dict = None
) -> dict:
    """
    Recommend the best starting dilution before running a sample.
    Eliminates out-of-range re-runs — the most common lab time-waster.

    Returns:
        {
            "recommended_starting_dilution": "1:10",
            "dilution_range_to_prepare": "1:5 to 1:50",
            "basis": "str",
            "confidence": "high | medium | low",
            "historical_sample_count": int,
            "watch_out_for": "str"
        }

    Example:
        result = predict_optimal_dilution(
            assay_id="BIO_002",
            sample_type="post_protein_a_eluate",
            sample_metadata={"process_day": 14}
        )
    """
    assay = get_assay_by_id(assay_id)
    if not assay:
        return {
            "recommended_starting_dilution": "1:10",
            "confidence": "low",
            "basis": f"Assay {assay_id} not found — using default.",
            "historical_sample_count": 0
        }

    history = get_run_history(assay_id=assay_id, sample_type=sample_type, limit=30)
    historical_results = [
        {"raw_results": r.get("raw_results", {}), "status": r.get("status")}
        for r in history
    ]

    system_prompt = f"""You are an expert analytical scientist optimising dilution strategies
for {assay['name']}. Recommend the single best starting dilution so sample readings
land within the linear range on the first attempt.

Detection: {assay['detection']}
Sample volume: {assay['sample_volume_uL']} uL
Notes: {assay['notes']}
Acceptance criteria: {json.dumps(assay['acceptance_criteria'], indent=2)}"""

    user_prompt = f"""Sample type: {sample_type}
Metadata: {json.dumps(sample_metadata or {}, indent=2)}

Historical data ({len(historical_results)} records):
{json.dumps(historical_results[:10], indent=2) if historical_results
 else "No history yet — base recommendation on sample type and assay parameters only."}

Return this exact JSON:
{{
  "recommended_starting_dilution": "e.g. 1:10 or neat or 1:100",
  "dilution_range_to_prepare": "e.g. 1:5 to 1:50",
  "basis": "one sentence explaining the recommendation",
  "confidence": "high (>10 records) or medium (2-9) or low (0-1)",
  "historical_sample_count": {len(historical_results)},
  "watch_out_for": "one sentence about edge cases"
}}"""

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))
        print(f"[Dilution] {assay_id} | {sample_type} | "
              f"{result.get('recommended_starting_dilution')} ({result.get('confidence')})")
        return result
    except Exception as e:
        return {
            "recommended_starting_dilution": "1:10",
            "dilution_range_to_prepare": "1:5 to 1:50",
            "basis": f"AI call failed: {e} — using default.",
            "confidence": "low",
            "historical_sample_count": len(history)
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 4 — NATURAL LANGUAGE PROTOCOL SEARCH
# ─────────────────────────────────────────────────────────────

def search_protocols(query: str, top_n: int = 5) -> list:
    """
    Search the assay library using plain English.
    Returns ranked results with reasoning — no need to know field names.

    Example queries:
        "which assays cover mAb quality attributes under 30 min robot time?"
        "find fully automated assays for CHO cell culture monitoring"
        "what can I run on WB3 for sterility?"

    Returns:
        [
            {
                "assay_id": "BIO_001",
                "name": "...",
                "rank": 1,
                "rationale": "...",
                "match_score": "high | medium | low"
            },
            ...
        ]
    """
    assay_summaries = [
        {
            "assay_id": a["assay_id"],
            "name": a["name"],
            "product_types": a["product_types"],
            "purpose": a["purpose"],
            "robot_active_minutes": a.get("robot_active_minutes", 0),
            "total_assay_duration_hours": a.get("total_assay_duration_hours", 0),
            "throughput_samples_per_run": a.get("throughput_samples_per_run", 0),
            "automation_difficulty": a["automation_difficulty"],
            "workbench_id": a.get("workbench_id", "N/A"),
            "platform_compatibility": a.get("platform_compatibility", ""),
            "environment_requirement": a.get("environment_requirement", ""),
            "detection": a.get("detection", ""),
            "regulatory": a.get("regulatory", []),
            "instruments_needed": a.get("instruments_needed", []),
        }
        for a in BIOPHARMA_ASSAYS
    ]

    system_prompt = """You are a search assistant for a biopharmaceutical robot automation assay library.
Return the most relevant assays from the library ranked by genuine match quality.
If fewer than the requested number match well, return fewer.
Return ONLY a JSON array, no preamble."""

    user_prompt = f"""Query: "{query}"

Library ({len(assay_summaries)} assays):
{json.dumps(assay_summaries, indent=2)}

Return top {top_n} as a JSON array:
[
  {{
    "assay_id": "BIO_XXX",
    "name": "assay name",
    "rank": 1,
    "rationale": "one sentence explaining why this matches",
    "match_score": "high or medium or low"
  }}
]"""

    try:
        results = json.loads(_call_claude(system_prompt, user_prompt))
        if results:
            print(f"[Search] '{query[:50]}' | Top: {results[0]['assay_id']}")
        return results
    except Exception as e:
        print(f"[Search] Failed: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 5 — PREDICTIVE INSTRUMENT MAINTENANCE
# ─────────────────────────────────────────────────────────────

def analyze_instrument_health(
    instrument_id: str,
    assay_id: str,
    current_metrics: dict
) -> dict:
    """
    Track instrument health over time and predict failure before it happens.
    Stores current metrics and analyses the trend.

    instrument_id examples: "HPLC_ProteinA_01", "pH_Meter_WB2", "MFI_Unit_01"

    current_metrics examples:
        HPLC: {"back_pressure_bar": 215, "retention_time_min": 3.44,
                "suitability_cv_pct": 0.5, "injection_count": 350}
        pH:   {"calibration_slope_pct": 97.8, "buffer_error_ph": 0.02}
        MFI:  {"background_particles_per_mL": 7, "bead_recovery_pct": 97}

    Returns:
        {
            "health_status": "good | degrading | critical",
            "risk_level": "low | medium | high",
            "trend_description": "str",
            "predicted_runs_to_failure": int or null,
            "maintenance_recommendation": "str",
            "urgency": "routine | soon | immediate"
        }
    """
    assay = get_assay_by_id(assay_id)
    if not assay:
        return {
            "health_status": "unknown",
            "risk_level": "medium",
            "maintenance_recommendation": f"Assay {assay_id} not found.",
            "urgency": "soon"
        }

    store_instrument_health(
        instrument_id, assay_id,
        f"HEALTH-{datetime.utcnow().strftime('%Y%m%d%H%M')}",
        current_metrics
    )

    history = get_instrument_history(instrument_id, assay_id, limit=30)
    metrics_history = [
        {"timestamp": r["timestamp"], "metrics": r["health_metrics"]}
        for r in history
    ]

    system_prompt = f"""You are a precision instrument reliability engineer for a GMP
pharmaceutical analytical laboratory. Analyse health metric trends and predict
maintenance needs before instrument failure causes a failed run.

Assay supported: {assay['name']} ({assay_id})
Acceptance criteria: {json.dumps(assay['acceptance_criteria'], indent=2)}"""

    health_examples = """Examples of correct instrument health analyses:

EXAMPLE 1 — healthy/stable:
INPUT: HPLC pressure history (bar): 168, 172, 170, 169, 171, 168. Retention time CV 0.3%. Injection count 95.
OUTPUT:
{
  "health_status": "good",
  "risk_level": "low",
  "trend_description": "Back-pressure stable around 170 bar with low retention time variability; instrument is performing within nominal range.",
  "predicted_runs_to_failure": null,
  "maintenance_recommendation": "Continue routine PM schedule; no action required.",
  "urgency": "routine"
}

EXAMPLE 2 — degrading trend:
INPUT: HPLC pressure history (bar): 168, 198, 231, 247, 268. Retention time CV climbed 0.3% -> 0.7%. Injection count 455.
OUTPUT:
{
  "health_status": "degrading",
  "risk_level": "high",
  "trend_description": "Back-pressure has climbed monotonically from 168 to 268 bar (+60%) over recent runs; rising retention time CV reinforces column-aging signal at injection count 455.",
  "predicted_runs_to_failure": 25,
  "maintenance_recommendation": "Schedule column replacement and re-qualification within next 3 runs.",
  "urgency": "soon"
}

Now analyze this instrument:

"""

    user_prompt = health_examples + f"""Instrument: {instrument_id}
Current metrics: {json.dumps(current_metrics, indent=2)}

Historical trend ({len(metrics_history)} records, chronological):
{json.dumps(metrics_history[-15:], indent=2) if metrics_history
 else "No prior history — first health record for this instrument."}

Return this exact JSON:
{{
  "health_status": "good or degrading or critical",
  "risk_level": "low or medium or high",
  "trend_description": "one sentence on what you observe",
  "predicted_runs_to_failure": null or integer,
  "maintenance_recommendation": "specific action required",
  "urgency": "routine or soon or immediate"
}}"""

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))
        print(f"[Instrument] {instrument_id} | {result.get('health_status','').upper()} "
              f"| {result.get('urgency','')}")
        return result
    except Exception as e:
        return {
            "health_status": "unknown",
            "risk_level": "medium",
            "trend_description": f"AI health analysis failed: {e}",
            "predicted_runs_to_failure": None,
            "maintenance_recommendation": "Manual inspection required.",
            "urgency": "soon"
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 6 — CROSS-RUN CORRELATION INTELLIGENCE
# ─────────────────────────────────────────────────────────────

def validate_correlation_output(output: dict, batch_data: dict) -> tuple:
    """Validate that correlation output is internally consistent
    with the batch data. Returns (is_valid, reason).
    """
    if (output.get("correlation_detected")
            and output.get("signal_strength") == "weak"):
        return False, "Contradiction: correlation detected but signal weak"

    if (output.get("escalate_to_qa")
            and output.get("signal_strength") == "weak"):
        return False, "Contradiction: QA escalation requested but signal weak"

    narrative = (output.get("narrative") or "").lower()
    batch_id = (batch_data.get("batch_id") or "").lower()
    if batch_id and batch_id not in narrative:
        return False, f"Narrative does not reference batch {batch_id}"

    return True, "Valid"


def call_with_validation(ai_function, args: dict, validator, max_retries: int = 2):
    """Call an AI function and validate its output.
    Retry once if validation fails.
    """
    last_reason = None
    for attempt in range(max_retries):
        try:
            # Pop any retry feedback before invoking — AI functions don't accept it
            call_args = {k: v for k, v in args.items() if not k.startswith("_")}
            result = ai_function(**call_args)
            is_valid, reason = validator(result, args)
            if is_valid:
                return result
            last_reason = reason
            if attempt == max_retries - 1:
                if isinstance(result, dict):
                    result["_validation_warning"] = reason
                return result
            args["_retry_reason"] = (
                f"Previous response was invalid: {reason}. "
                "Generate a corrected response."
            )
        except Exception as e:
            if attempt == max_retries - 1:
                raise
    return {"_validation_warning": last_reason} if last_reason else None


def correlate_batch_quality(
    batch_id: str,
    assay_ids: list = None
) -> dict:
    """
    The most powerful function in this layer.

    Queries ALL run records for a batch across multiple assays.
    AI identifies coordinated signals no individual assay would reveal —
    e.g. titer dropping + charge variants shifting + aggregation rising
    across three assays = process drift signal.

    assay_ids: optional filter. If None, pulls all assays for this batch.

    Returns:
        {
            "correlation_detected": true | false,
            "signal_strength": "strong | moderate | weak | none",
            "narrative": "what the AI found",
            "affected_assays": ["BIO_001", ...],
            "process_hypothesis": "str",
            "recommended_action": "str",
            "escalate_to_qa": true | false
        }

    Example:
        result = correlate_batch_quality("CHO-047-DS-031")
    """
    all_runs = get_run_history(batch_id=batch_id, limit=100)

    if not all_runs:
        return {
            "correlation_detected": False,
            "signal_strength": "none",
            "narrative": (
                f"No run records found for batch {batch_id}. "
                "Store run records using store_run_record() first."
            ),
            "affected_assays": [],
            "process_hypothesis": "",
            "recommended_action": "Populate run records for this batch.",
            "escalate_to_qa": False
        }

    if assay_ids:
        all_runs = [r for r in all_runs if r.get("assay_id") in assay_ids]

    batch_summary = []
    for run in all_runs:
        assay = get_assay_by_id(run.get("assay_id", ""))
        batch_summary.append({
            "assay_id": run.get("assay_id"),
            "assay_name": assay["name"] if assay else run.get("assay_id"),
            "status": run.get("status"),
            "acceptance_outcomes": run.get("acceptance_outcomes", {}),
            "raw_results": run.get("raw_results", {}),
            "timestamp": run.get("timestamp"),
            "notes": run.get("notes", "")
        })

    system_prompt = """You are a senior bioprocess quality scientist identifying COORDINATED
quality signals across multiple assays for a single manufacturing batch.

A single failing assay is an incident.
Multiple assays showing correlated trends is a process signal.

Focus on: quality attributes moving in the same direction, patterns consistent
with known failure modes (fermentation drift, purification problems, formulation issues),
combinations warranting a manufacturing process investigation.

Be specific and analytical. Do not flag unrelated individual failures as a correlation."""

    example_block = """Here is an example of a correct correlation analysis from a different batch:

INPUT BATCH: CHO-2025-115
  - Titer: 4.2 mg/mL (historical 4.5, -7%)
  - HMWS: 0.9% (historical 0.8%, normal)
  - Charge variants: 25.1% acidic (historical 24.5%, normal)

OUTPUT:
{
  "correlation_detected": false,
  "signal_strength": "weak",
  "process_hypothesis": "Single attribute drift within normal variability; no coordinated signal",
  "escalate_to_qa": false,
  "narrative": "Batch CHO-2025-115 titer reduction is within normal batch-to-batch variability. HMWS and charge variants are stable, suggesting no upstream process drift. No action required beyond standard release testing."
}

Now analyze this batch:

"""

    user_prompt = example_block + f"""Batch: {batch_id}
Total assay runs: {len(batch_summary)}

Cross-assay results:
{json.dumps(batch_summary, indent=2)}

Return this exact JSON:
{{
  "correlation_detected": true or false,
  "signal_strength": "strong or moderate or weak or none",
  "narrative": "2-3 sentences — specific assays and results, must reference batch {batch_id}",
  "affected_assays": ["list of assay IDs"],
  "process_hypothesis": "one sentence on upstream cause",
  "recommended_action": "one sentence on next step",
  "escalate_to_qa": true or false
}}"""

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))

        # Validate output; retry once if invalid
        is_valid, reason = validate_correlation_output(result, {"batch_id": batch_id})
        if not is_valid:
            try:
                result2 = json.loads(_call_claude(system_prompt, user_prompt))
                is_valid2, reason2 = validate_correlation_output(result2, {"batch_id": batch_id})
                if is_valid2:
                    result = result2
                else:
                    result["_validation_warning"] = reason
            except Exception:
                result["_validation_warning"] = reason

        status = "CORRELATION FOUND" if result.get("correlation_detected") else "No correlation"
        print(f"[Correlation] {batch_id} | {status} | "
              f"Signal: {result.get('signal_strength')} | "
              f"QA: {result.get('escalate_to_qa')}")
        return result
    except Exception as e:
        return {
            "correlation_detected": False,
            "signal_strength": "none",
            "narrative": f"AI correlation failed: {e}",
            "affected_assays": [],
            "process_hypothesis": "",
            "recommended_action": "Manual cross-assay review required.",
            "escalate_to_qa": False
        }


def check_batch_analysis_consistency(batch_id: str) -> dict:
    """Run multiple AI functions on the same batch and check
    for contradictions across their outputs.

    Returns:
        {
            "consistent": bool,
            "conflicts": [list of conflict descriptions],
            "correlation": {...},
            "rca": {...},
            "summary": "..."
        }
    """
    correlation = correlate_batch_quality(batch_id)

    sb = _get_supabase()
    sb_result = sb.table("run_records").select("*").eq(
        "batch_id", batch_id
    ).execute()

    failed_runs = [
        r for r in (sb_result.data or [])
        if r.get("status") in ("fail", "partial")
    ]

    if not failed_runs:
        return {
            "consistent": True,
            "conflicts": [],
            "correlation": correlation,
            "rca": None,
            "summary": "No failed runs to analyze",
        }

    # RCA on the worst-performing failed run
    failed_runs.sort(key=lambda r: 0 if r.get("status") == "fail" else 1)
    target = failed_runs[0]

    failed_criteria = list((target.get("acceptance_outcomes") or {}).keys())
    rca = analyze_run_failure(
        target["assay_id"],
        target,
        failed_criteria=failed_criteria,
    )

    conflicts = []

    # Check 1: strong correlation but low RCA confidence
    if (correlation.get("signal_strength") == "strong"
            and rca.get("confidence", "low") == "low"):
        conflicts.append(
            "Strong correlation signal but RCA confidence is low — "
            "investigate further"
        )

    # Check 2: RCA flags critical but correlation says don't escalate
    if (not correlation.get("escalate_to_qa")
            and rca.get("severity", "") == "critical"):
        conflicts.append(
            "RCA identifies critical issue but correlation does not flag for QA"
        )

    # Check 3: correlation flags QA escalation but RCA says no investigation needed
    if (correlation.get("escalate_to_qa")
            and rca.get("requires_investigation") is False):
        conflicts.append(
            "Correlation flags QA escalation but RCA marks investigation unnecessary"
        )

    return {
        "consistent": len(conflicts) == 0,
        "conflicts": conflicts,
        "correlation": correlation,
        "rca": rca,
        "summary": (
            "Analyses agree" if not conflicts
            else f"{len(conflicts)} contradiction(s) found"
        ),
    }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 7 — AUTO BATCH RECORD NARRATIVE
# ─────────────────────────────────────────────────────────────

def generate_batch_record(
    batch_id: str,
    product_name: str,
    lot_number: str,
    analyst_name: str,
    assay_ids: list = None
) -> dict:
    """
    Draft the GMP batch record narrative from structured run data.
    Saves 30-45 minutes of documentation per batch.
    Uses claude-opus-4-6 for maximum writing quality.

    Returns:
        {
            "narrative": "full GMP-style narrative text",
            "disposition_recommendation": "RELEASE | REJECT | FURTHER TESTING REQUIRED",
            "disposition_rationale": "str",
            "deviations_flagged": [...],
            "word_count": int
        }

    Example:
        record = generate_batch_record(
            batch_id="CHO-047-DS-031",
            product_name="Anti-CD20 mAb",
            lot_number="DS-2024-031",
            analyst_name="A. Smith"
        )
        print(record["narrative"])
    """
    all_runs = get_run_history(batch_id=batch_id, limit=100)
    if assay_ids:
        all_runs = [r for r in all_runs if r.get("assay_id") in assay_ids]

    if not all_runs:
        return {
            "narrative": f"No run records found for batch {batch_id}.",
            "disposition_recommendation": "FURTHER TESTING REQUIRED",
            "disposition_rationale": "No analytical data available.",
            "deviations_flagged": [],
            "word_count": 0
        }

    runs_summary = []
    for run in all_runs:
        assay = get_assay_by_id(run.get("assay_id", ""))
        runs_summary.append({
            "assay_id": run.get("assay_id"),
            "assay_name": assay["name"] if assay else run.get("assay_id"),
            "regulatory_refs": assay["regulatory"] if assay else [],
            "status": run.get("status"),
            "acceptance_outcomes": run.get("acceptance_outcomes", {}),
            "raw_results": run.get("raw_results", {}),
            "timestamp": run.get("timestamp"),
            "notes": run.get("notes", "")
        })

    date_str = datetime.utcnow().strftime("%d %B %Y")

    system_prompt = """You are a GMP documentation specialist writing the analytical testing
narrative section of a pharmaceutical batch record.

Writing rules (mandatory):
- Past tense throughout
- Third person passive voice for procedural steps
- No contractions
- Precise numerical results with units
- Each assay referenced by compendial method number where available
- Deviations described factually without speculation
- Disposition recommendation clearly stated and supported

The narrative must be suitable for regulatory review without further editing."""

    record_examples = """Examples of correct batch record narratives:

EXAMPLE 1 — RELEASE (all-pass batch):
INPUT: Product mAb-X, Lot 2025-001, all 5 release assays passed. Titer 4.5 mg/mL (spec >=3.5). HMWS 0.7% (spec <2%). Endotoxin 0.04 EU/mL (spec <0.5).
OUTPUT:
{
  "narrative": "Batch 2025-001 was tested per release specifications.\\n\\nQuantitative results:\\n- Protein A titer: 4.5 mg/mL (spec >= 3.5 mg/mL, PASS).\\n- SEC-HPLC HMWS: 0.7% (spec < 2%, PASS).\\n- Kinetic LAL endotoxin: 0.04 EU/mL (spec < 0.5 EU/mL, PASS).\\n\\nAll results meet established release criteria. No deviations were observed.",
  "disposition_recommendation": "RELEASE",
  "disposition_rationale": "All quality attributes meet release specifications with no deviations.",
  "deviations_flagged": [],
  "word_count": 78
}

EXAMPLE 2 — FURTHER TESTING (with deviation language):
INPUT: Product mAb-X, Lot 2025-007. Titer 3.8 mg/mL (PASS but -17% vs historical 4.6). HMWS 3.1% (FAIL spec <2%). Charge variant main peak 64.2% vs historical 68.1% (-3.9%).
OUTPUT:
{
  "narrative": "Batch 2025-007 was tested per release specifications.\\n\\nQuantitative results:\\n- Protein A titer: 3.8 mg/mL (spec >= 3.5 mg/mL, PASS but 17% below historical mean).\\n- SEC-HPLC HMWS: 3.1% (spec < 2%, FAIL — deviation DEV-2025-007-01).\\n- IEX charge variant main peak: 64.2% (historical 68.1%; -3.9% drift, partial).\\n\\nA correlated quality signal is observed across three assays consistent with an upstream cell-culture stress event. Per ICH Q6B and internal SOPs, batch is held pending bioprocess investigation and confirmatory retest.",
  "disposition_recommendation": "FURTHER TESTING REQUIRED",
  "disposition_rationale": "HMWS exceeds 2% investigation threshold and correlated drift in titer and charge variants warrants upstream root-cause review prior to disposition.",
  "deviations_flagged": [
    {"assay_id": "BIO_003", "deviation": "HMWS 3.1% exceeds 2% investigation threshold", "impact": "major"},
    {"assay_id": "BIO_001", "deviation": "Titer 17% below historical mean (within spec)", "impact": "minor"},
    {"assay_id": "BIO_013", "deviation": "Main peak drift -3.9% from historical", "impact": "minor"}
  ],
  "word_count": 120
}

Now generate the batch record:

"""

    user_prompt = record_examples + f"""Product: {product_name}
Lot: {lot_number}
Batch: {batch_id}
Date: {date_str}
Analyst: {analyst_name}

Assay results:
{json.dumps(runs_summary, indent=2)}

Return this exact JSON:
{{
  "narrative": "full GMP narrative as a single string with newlines as \\n",
  "disposition_recommendation": "RELEASE or REJECT or FURTHER TESTING REQUIRED",
  "disposition_rationale": "one sentence justification",
  "deviations_flagged": [
    {{"assay_id": "BIO_XXX", "deviation": "description", "impact": "none or minor or major"}}
  ],
  "word_count": integer
}}"""

    try:
        # Opus for batch records — highest quality for regulatory documents
        claude = _get_anthropic()
        response = claude.messages.create(
            model="claude-opus-4-6",
            max_tokens=2500,
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt + (
                "\n\nCRITICAL: Respond ONLY with valid JSON. "
                "No preamble, no markdown fences."
            ),
        )
        result = json.loads(response.content[0].text)
        print(f"[BatchRecord] {batch_id} | {result.get('disposition_recommendation')} "
              f"| {result.get('word_count', 0)} words")
        return result
    except Exception as e:
        return {
            "narrative": f"AI narrative generation failed: {e}",
            "disposition_recommendation": "FURTHER TESTING REQUIRED",
            "disposition_rationale": "Generation failed — manual review required.",
            "deviations_flagged": [],
            "word_count": 0
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 8 — PROTOCOL OPTIMIZATION ENGINE
# ─────────────────────────────────────────────────────────────

def optimize_protocol(
    assay_id: str,
    timing_logs: list = None
) -> dict:
    """
    Analyse step timing data to find optimisations.
    Protocol improves automatically as run data accumulates.

    timing_logs: list of dicts with per-step timing data. If None,
    AI analyses the protocol structure alone for hypothetical optimisations.

    Returns:
        {
            "optimizations_found": int,
            "estimated_time_saving_minutes": int,
            "proposed_changes": [...],
            "parallelisation_opportunities": ["str"],
            "overall_assessment": "str"
        }
    """
    assay = get_assay_by_id(assay_id)
    if not assay:
        return {
            "optimizations_found": 0,
            "overall_assessment": f"Assay {assay_id} not found."
        }

    system_prompt = f"""You are a lean manufacturing engineer and robotics workflow specialist
for pharmaceutical laboratory automation.

Constraints (never violate):
- Compendial method requirements cannot be removed
- GMP documentation steps cannot be removed
- Safety steps cannot be removed
- All proposed changes must maintain regulatory compliance"""

    user_prompt = f"""Assay: {assay['name']} ({assay_id})
Current robot active time: {assay.get('robot_active_minutes', 0)} minutes
Regulatory refs: {', '.join(assay.get('regulatory', []))}

Robot steps:
{json.dumps([f"Step {i+1:02d}: {s}" for i, s in enumerate(assay['robot_steps'])], indent=2)}

Timing data:
{json.dumps(timing_logs, indent=2) if timing_logs
 else "No timing data. Suggest hypothetical optimisations from protocol structure alone."}

Return this exact JSON:
{{
  "optimizations_found": integer,
  "estimated_time_saving_minutes": integer,
  "proposed_changes": [
    {{
      "step_number": "Step XX",
      "current_specification": "abbreviated current step text",
      "issue": "slower_than_expected or parallelisable or redundant or can_be_combined",
      "proposed_change": "specific rewrite",
      "estimated_saving_minutes": integer,
      "regulatory_safe": true or false
    }}
  ],
  "parallelisation_opportunities": ["Step X can run while Step Y incubates"],
  "overall_assessment": "one sentence summary"
}}"""

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))
        print(f"[Optimize] {assay_id} | "
              f"{result.get('optimizations_found')} optimisations | "
              f"{result.get('estimated_time_saving_minutes')} min saving")
        return result
    except Exception as e:
        return {
            "optimizations_found": 0,
            "estimated_time_saving_minutes": 0,
            "proposed_changes": [],
            "parallelisation_opportunities": [],
            "overall_assessment": f"AI optimisation failed: {e}"
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 9 — ASSIGN INSTRUMENT STEPS
# ─────────────────────────────────────────────────────────────

def assign_instrument_steps(assay_id: str) -> dict:
    """
    AI recommends which steps should run on Rail robot vs AutoMATE 96,
    with reasoning per step.

    Returns:
        {
            "assignments": [
                {"step_num": 1, "step_text": "...",
                 "instrument": "automate_96" | "rail_robot" | "analyst",
                 "reasoning": "..."}
            ],
            "automate_96_count": int,
            "rail_robot_count": int,
            "summary": "..."
        }
    """
    assay = _find_assay(assay_id)
    if not assay:
        return {
            "assignments": [],
            "automate_96_count": 0,
            "rail_robot_count": 0,
            "summary": f"Assay {assay_id} not found in any loaded field library.",
        }

    system_prompt = (
        "You are a lab automation specialist. Given a list of robot protocol steps "
        "and the capabilities of the Accuris AutoMATE 96 liquid handler, assign each "
        "step to either 'automate_96', 'rail_robot', or 'analyst'.\n\n"
        "AutoMATE 96 capabilities:\n"
        "- 96-channel simultaneous dispense (1-1000 uL with correct head)\n"
        "- Serial dilution across plate columns\n"
        "- Multi-dispensing from single reservoir\n"
        "- Mixing in microplate wells\n"
        "- Three heads: 1-20uL, 5-200uL, 100-1000uL\n\n"
        "Rail robot handles: transport, instrument loading, incubation transfers, "
        "centrifugation, non-plate liquid transfers (tubes, conicals, HPLC vials).\n\n"
        "Analyst handles: microscope checks, instrument parameter verification, "
        "visual inspection. Any step starting with '[ANALYST STEP' is analyst.\n\n"
        "Return JSON only — no markdown fences, no prose preamble:\n"
        "{\n"
        '  "assignments": [\n'
        '    {"step_num": 1, "step_text": "first 120 chars of step", '
        '"instrument": "automate_96", "reasoning": "brief — volume, channel count, or why"}\n'
        "  ],\n"
        '  "automate_96_count": 5,\n'
        '  "rail_robot_count": 8,\n'
        '  "summary": "one sentence on how the assay splits across instruments"\n'
        "}"
    )

    user_prompt = (
        f"Assay: {assay['name']} ({assay_id})\n\n"
        f"Robot steps (numbered 1-indexed):\n"
        f"{json.dumps([{'step_num': i, 'step_text': s} for i, s in enumerate(assay.get('robot_steps', []), 1)], indent=2)}"
    )

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt, max_tokens=4000))
        return result
    except Exception as e:
        return {
            "assignments": [],
            "automate_96_count": 0,
            "rail_robot_count": 0,
            "summary": f"AI assignment failed: {e}",
        }


# ─────────────────────────────────────────────────────────────
# AI FUNCTION 10 — CHECK VOLUME COMPATIBILITY
# ─────────────────────────────────────────────────────────────

def check_volume_compatibility(assay_id: str) -> dict:
    """
    Check if all AutoMATE 96 steps are within head ranges.

    Returns:
        {
            "compatible": bool,
            "flags": [{"step_num": int, "volume": "...", "issue": "...",
                       "suggestion": "..."}],
            "head_changes_required": bool,
            "recommendation": "..."
        }
    """
    assay = _find_assay(assay_id)
    if not assay:
        return {
            "compatible": False,
            "flags": [],
            "head_changes_required": False,
            "recommendation": f"Assay {assay_id} not found in any loaded field library.",
        }

    system_prompt = (
        "You are a liquid handling specialist. Review these assay steps and identify "
        "any volume incompatibilities with the Accuris AutoMATE 96 head ranges:\n"
        "- Head 1: 1-20 uL\n"
        "- Head 2: 5-200 uL\n"
        "- Head 3: 100-1000 uL\n\n"
        "Flag any step where the dispensing volume:\n"
        "1. Falls below 1 uL (below all heads — use acoustic dispenser instead)\n"
        "2. Falls in a gap between heads (e.g. 21-24 uL — needs head change)\n"
        "3. Requires a head change mid-run (costly in time)\n\n"
        "For each flag suggest: adjust volume to nearest head range, use alternative "
        "head, or keep on rail robot liquid handler.\n\n"
        "Return JSON only — no markdown fences, no prose preamble:\n"
        "{\n"
        '  "compatible": true or false,\n'
        '  "flags": [\n'
        '    {"step_num": 3, "volume": "100 nL", "issue": "below 1 uL minimum", '
        '"suggestion": "Use Echo acoustic dispenser"}\n'
        "  ],\n"
        '  "head_changes_required": true or false,\n'
        '  "recommendation": "one or two sentences on the overall workflow"\n'
        "}"
    )

    automate_steps = assay.get("automate_96_steps", [])
    tagged = [
        {"step_num": i, "step_text": s}
        for i, s in enumerate(assay.get("robot_steps", []), 1)
        if i in automate_steps
    ]

    user_prompt = (
        f"Assay: {assay['name']} ({assay_id})\n"
        f"Current recommended head: {assay.get('automate_96_head', 'not applicable')}\n"
        f"Head note: {assay.get('automate_96_head_note', '')}\n"
        f"Sample volume: {assay.get('sample_volume_uL', 'n/a')} uL\n\n"
        f"AutoMATE 96 steps (only these need volume checking):\n"
        f"{json.dumps(tagged, indent=2) if tagged else '[] — no AutoMATE 96 steps in this assay'}"
    )

    try:
        result = json.loads(_call_claude(system_prompt, user_prompt))
        return result
    except Exception as e:
        return {
            "compatible": False,
            "flags": [],
            "head_changes_required": False,
            "recommendation": f"AI compatibility check failed: {e}",
        }


def parse_custom_protocol(natural_language_steps: str) -> dict:
    """Parse natural-language protocol steps into structured actions
    for robot execution.

    Returns:
        {
            "parsed_steps": [
                {
                    "step_number": 1,
                    "action": "dispense|mix|incubate|centrifuge|read|pause|other",
                    "description": "...",
                    "parameters": {...},
                    "duration_minutes": float,
                    "instrument": "liquid_handler|centrifuge|plate_reader|incubator|analyst",
                    "warnings": [...]
                }
            ],
            "total_duration_minutes": float,
            "instruments_needed": [...],
            "warnings": [...],
            "summary": "..."
        }
    """
    system_prompt = '''You are a biopharma robot protocol parser. Convert natural-language laboratory steps into structured machine-executable instructions.

For each step:
- Identify the action type (dispense, mix, incubate, centrifuge, read, pause, other)
- Extract parameters with units (volume in uL, time in minutes, temperature in C, RPM)
- Identify which instrument handles it
- Estimate duration in minutes
- Flag warnings for unusual or impossible parameters

For "Mix at 800 rpm for 30 seconds":
{
    "step_number": 3,
    "action": "mix",
    "description": "Mix at 800 rpm for 30 seconds",
    "parameters": {"rpm": 800, "duration_seconds": 30},
    "duration_minutes": 0.5,
    "instrument": "liquid_handler",
    "warnings": []
}

For "Incubate at 37C for 15 minutes":
{
    "step_number": 4,
    "action": "incubate",
    "description": "Incubate at 37 degrees C for 15 minutes",
    "parameters": {"temperature_C": 37, "duration_minutes": 15},
    "duration_minutes": 15,
    "instrument": "incubator",
    "warnings": []
}

For ambiguous steps, use sensible defaults but include warnings:
- "room temperature" defaults to 22C
- "gentle mixing" defaults to 400 rpm
- Missing volumes flagged as warning

Return JSON only — no markdown fences. Schema:
{
    "parsed_steps": [...as above...],
    "total_duration_minutes": float,
    "instruments_needed": [list of unique instrument strings],
    "warnings": [protocol-level warnings],
    "summary": "one-sentence summary"
}'''

    user_message = f"""Parse these natural-language protocol steps:

{natural_language_steps}

Return structured representation."""

    try:
        response = _call_claude(
            system_prompt,
            user_message,
            expect_json=True,
            max_tokens=2000,
            model="claude-sonnet-4-6",
        )
        import json
        return json.loads(response)
    except Exception as e:
        return {
            "parsed_steps": [],
            "total_duration_minutes": 0,
            "instruments_needed": [],
            "warnings": [f"Parsing failed: {e}"],
            "summary": "Could not parse the input.",
        }


def generate_custom_protocol_code(parsed_steps: list) -> str:
    """Generate PyLabRobot code from parsed step list."""
    system_prompt = '''You generate PyLabRobot Python code that executes a list of laboratory steps on a robot.

Use the existing PyLabRobot patterns:
- from pylabrobot.liquid_handling import LiquidHandler
- from pylabrobot.resources import HamiltonDeck, Plate, Reservoir
- async functions with await for each operation
- await lh.aspirate(...), await lh.dispense(...), await lh.move(...)

For non-liquid-handling steps (centrifuge, plate reader, incubator), include them as comments with [ANALYST STEP] markers indicating manual transfer:
    # [ANALYST STEP] Centrifuge at 4000 rpm for 5 minutes

Generate clean, runnable PyLabRobot code with proper imports, deck setup, and async function structure.

Return only the Python code, no markdown fences.'''

    import json
    user_message = f"""Generate PyLabRobot code for these parsed steps:

{json.dumps(parsed_steps, indent=2)}

Output complete .py file content."""

    try:
        response = _call_claude(
            system_prompt,
            user_message,
            expect_json=False,
            max_tokens=3000,
            model="claude-sonnet-4-6",
        )
        response = response.strip()
        if response.startswith("```python"):
            response = response[9:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return response.strip()
    except Exception as e:
        return f"# Code generation failed: {e}"


# ─────────────────────────────────────────────────────────────
# DEMO — run with: python ai_layer.py
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RAIL SYSTEM — AI LAYER DEMO")
    print("=" * 70)

    print("\n[1] NATURAL LANGUAGE SEARCH")
    results = search_protocols(
        "which assays cover mAb quality for release testing under 30 min robot time?",
        top_n=3
    )
    for r in results:
        print(f"  {r.get('rank')}. {r.get('assay_id')} — {r.get('name')} "
              f"[{r.get('match_score')}]")
        print(f"     {r.get('rationale')}")

    print("\n[2] PROTOCOL OPTIMISATION — BIO_005 ELISA")
    opt = optimize_protocol("BIO_005")
    print(f"  Found: {opt.get('optimizations_found')} optimisations")
    print(f"  Saving: {opt.get('estimated_time_saving_minutes')} minutes")
    print(f"  {opt.get('overall_assessment')}")

    print("\n[3] DILUTION PREDICTION")
    dil = predict_optimal_dilution(
        assay_id="BIO_002",
        sample_type="post_protein_a_eluate",
        sample_metadata={"approximate_titer_mg_mL": 4.0, "process_day": 14}
    )
    print(f"  Recommended: {dil.get('recommended_starting_dilution')}")
    print(f"  Range: {dil.get('dilution_range_to_prepare')}")
    print(f"  Basis: {dil.get('basis')}")

    print("\n[4-8] RCA, ANOMALY, INSTRUMENT, CORRELATION, BATCH RECORD")
    print("  These require run records stored in Supabase.")
    print("  Call store_run_record() after real runs, then re-run these functions.")

    print("\n" + "=" * 70)
    print("AI Layer ready. Add your .env file and run: python ai_layer.py")
    print("=" * 70)
