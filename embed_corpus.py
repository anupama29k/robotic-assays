import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".env"
))

import voyageai
from supabase import create_client
from pypdf import PdfReader
from collections import Counter

VOYAGE_KEY = os.environ.get("VOYAGE_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not all([VOYAGE_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("ERROR: Missing keys in .env")
    exit(1)

vo = voyageai.Client(api_key=VOYAGE_KEY)
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CORPUS_DIR = "corpus/"
FORCE_REEMBED_REGULATORY = False


def chunk_text(text, size, overlap):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + size])
        if len(chunk.strip()) > 100:
            chunks.append(chunk)
        i += size - overlap
    return chunks


def chunk_text_with_sections(text: str, size: int = 500, overlap: int = 50) -> list:
    """Split text into chunks, tagging each with the nearest section
    heading found before it.

    Returns list of dicts: {"text": str, "section": str}
    """
    import re

    section_patterns = [
        r'^\s*(\d+\.\s+[A-Z][^.\n]{5,80})\s*$',         # "1. Introduction"
        r'^\s*(\d+\.\d+\.?\s+[A-Z][^.\n]{5,80})\s*$',   # "2.1 Scope"
        r'^\s*(\d+\.\d+\.\d+\.?\s+[A-Z][^.\n]{3,80})\s*$',  # "2.1.1"
        r'^\s*([IVX]+\.\s+[A-Z][^.\n]{5,80})\s*$',      # Roman numerals
        r'^\s*([A-Z][A-Z\s]{4,60}[A-Z])\s*$',           # ALL CAPS HEADERS
    ]

    lines = text.split('\n')
    line_sections = {}
    current_section = "Preamble"

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped:
            for pattern in section_patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    heading = match.group(1).strip()
                    # Strip trailing page numbers like "BACKGROUND 73"
                    heading = re.sub(r'\s+\d+$', '', heading).strip()
                    if 5 < len(heading) < 80:
                        current_section = heading
                        break
        # Always record running section for this line, even blank ones,
        # so chunks starting on blank lines still carry context.
        line_sections[i] = current_section

    full_text = '\n'.join(lines)
    words = full_text.split()

    # Build word-index → line mapping
    char_pos = 0
    word_to_line = []
    line_lengths = [len(line) + 1 for line in lines]

    for word in words:
        line_idx = 0
        cum = 0
        for li, llen in enumerate(line_lengths):
            cum += llen
            if char_pos < cum:
                line_idx = li
                break
        word_to_line.append(line_idx)
        char_pos += len(word) + 1

    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + size]
        chunk_text_str = " ".join(chunk_words)
        if len(chunk_text_str.strip()) > 100:
            line_idx = word_to_line[i] if i < len(word_to_line) else 0
            section = line_sections.get(line_idx, "Unspecified")
            chunks.append({"text": chunk_text_str, "section": section})
        i += size - overlap

    return chunks

def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text())
        except Exception as e:
            print(f"    page extract error: {e}")
    return "\n".join(parts)

def already_embedded(source_file):
    r = sb.table("knowledge_corpus").select("id").eq(
        "source_file", source_file
    ).limit(1).execute()
    return len(r.data) > 0

def get_embeddings_batch(texts):
    result = vo.embed(
        texts,
        model="voyage-3",
        input_type="document"
    )
    return result.embeddings

def embed_pdf(pdf_path, source_type="regulatory"):
    filename = os.path.basename(pdf_path)
    if already_embedded(filename) and not FORCE_REEMBED_REGULATORY:
        print(f"  SKIP (already embedded): {filename}")
        return 0

    if FORCE_REEMBED_REGULATORY and already_embedded(filename):
        print(f"  Re-embedding with sections: {filename}")
        sb.table("knowledge_corpus").delete().eq(
            "source_file", filename
        ).execute()

    print(f"  Processing: {filename}")
    text = extract_pdf_text(pdf_path)
    chunks_with_sections = chunk_text_with_sections(
        text, CHUNK_SIZE, CHUNK_OVERLAP
    )
    chunks = [c["text"] for c in chunks_with_sections]
    sections = [c["section"] for c in chunks_with_sections]
    print(f"    Extracted {len(text):,} chars -> {len(chunks)} chunks")

    inserted = 0
    BATCH = 32
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        try:
            embeddings = get_embeddings_batch(batch)
            for j, (chunk, emb) in enumerate(zip(batch, embeddings)):
                sb.table("knowledge_corpus").insert({
                    "source_file": filename,
                    "source_type": source_type,
                    "chunk_index": i + j,
                    "content": chunk,
                    "embedding": emb,
                    "metadata": {
                        "word_count": len(chunk.split()),
                        "char_count": len(chunk),
                        "section": sections[i + j],
                    },
                }).execute()
                inserted += 1
            print(f"    embedded {inserted}/{len(chunks)} chunks")
            time.sleep(0.3)
        except Exception as e:
            print(f"    BATCH FAIL i={i}: {e}")

    print(f"    DONE: {inserted} chunks stored")
    return inserted

def embed_markdown(md_path: str) -> int:
    """Embed a markdown knowledge file. Sections (H2/H3 headers) are used
    as section metadata. Source type is 'knowledge_primer'.
    """
    filename = os.path.basename(md_path)
    if already_embedded(filename) and not FORCE_REEMBED_REGULATORY:
        print(f"  SKIP markdown: {filename}")
        return 0

    if FORCE_REEMBED_REGULATORY and already_embedded(filename):
        print(f"  Re-embedding markdown: {filename}")
        sb.table("knowledge_corpus").delete().eq("source_file", filename).execute()

    print(f"  Processing markdown: {filename}")
    with open(md_path, "r", encoding="utf-8") as fh:
        text = fh.read()

    chunks_with_sections = chunk_text_with_sections(text, CHUNK_SIZE, CHUNK_OVERLAP)
    chunks = [c["text"] for c in chunks_with_sections]
    sections = [c["section"] for c in chunks_with_sections]
    print(f"    {len(text):,} chars -> {len(chunks)} chunks")

    inserted = 0
    BATCH = 32
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        try:
            embeddings = get_embeddings_batch(batch)
            for j, (chunk, emb) in enumerate(zip(batch, embeddings)):
                sb.table("knowledge_corpus").insert({
                    "source_file": filename,
                    "source_type": "knowledge_primer",
                    "chunk_index": i + j,
                    "content": chunk,
                    "embedding": emb,
                    "metadata": {
                        "word_count": len(chunk.split()),
                        "char_count": len(chunk),
                        "section": sections[i + j],
                    },
                }).execute()
                inserted += 1
            print(f"    embedded {inserted}/{len(chunks)}")
            time.sleep(0.3)
        except Exception as e:
            print(f"    BATCH FAIL i={i}: {e}")

    print(f"    DONE: {inserted} chunks stored")
    return inserted


def embed_assay_dicts():
    from field_01_biopharma_v2 import BIOPHARMA_ASSAYS
    from field_04_drug_discovery_hts_v2 import HTS_ASSAYS
    try:
        from field_03_genomics_ngs import GENOMICS_ASSAYS
    except ImportError:
        GENOMICS_ASSAYS = []

    all_assays = BIOPHARMA_ASSAYS + GENOMICS_ASSAYS + HTS_ASSAYS
    inserted = 0

    for assay in all_assays:
        source_id = f"assay_{assay['assay_id']}"
        if already_embedded(source_id):
            continue

        text = f"""Assay: {assay['name']} ({assay['assay_id']})
Field: {assay['field']}
Purpose: {assay['purpose']}
Product types: {', '.join(assay['product_types'])}
First key steps: {' '.join(assay['robot_steps'][:8])}
Acceptance criteria: {json.dumps(assay['acceptance_criteria'])}
Regulatory: {', '.join(assay['regulatory'])}
Difficulty: {assay['automation_difficulty']}
Throughput: {assay['throughput_samples_per_run']} samples per run
Robot active time: {assay['robot_active_minutes']} minutes
Detection: {assay['detection']}
Notes: {assay.get('notes', '')[:500]}"""

        try:
            embedding = get_embeddings_batch([text])[0]
            sb.table("knowledge_corpus").insert({
                "source_file": source_id,
                "source_type": "assay_library",
                "chunk_index": 0,
                "content": text,
                "embedding": embedding,
                "metadata": {
                    "assay_id": assay["assay_id"],
                    "field": assay["field"],
                    "difficulty": assay["automation_difficulty"]
                }
            }).execute()
            inserted += 1
            print(f"  Embedded: {assay['assay_id']}")
            time.sleep(0.2)
        except Exception as e:
            print(f"  FAIL {assay['assay_id']}: {e}")

    return inserted

def main():
    print("=" * 60)
    print("BIOINTERFACE - RAG CORPUS INGESTION")
    print("=" * 60)

    print("\n[1/2] Embedding regulatory documents...")
    if not os.path.exists(CORPUS_DIR):
        print(f"  ERROR: {CORPUS_DIR} folder does not exist")
        return

    pdf_files = list(Path(CORPUS_DIR).glob("*.pdf"))
    if not pdf_files:
        print(f"  No PDFs found in {CORPUS_DIR}")
    else:
        total_pdf_chunks = 0
        for pdf in pdf_files:
            chunks = embed_pdf(str(pdf), "regulatory")
            total_pdf_chunks += chunks
        print(f"\n  Regulatory total: {total_pdf_chunks} chunks")

    # Markdown knowledge files (e.g. curated NGS / domain primers)
    md_files = list(Path(CORPUS_DIR).glob("*.md"))
    if md_files:
        print(f"\n  Markdown files: {len(md_files)}")
        total_md_chunks = 0
        for md in md_files:
            chunks = embed_markdown(str(md))
            total_md_chunks += chunks
        print(f"  Markdown total: {total_md_chunks} chunks")

    print("\n[2/2] Embedding assay library...")
    assay_count = embed_assay_dicts()
    print(f"  Assay total: {assay_count}")

    print("\n" + "=" * 60)
    print("CORPUS STATUS")
    print("=" * 60)

    all_records = sb.table("knowledge_corpus").select(
        "source_type"
    ).execute()
    type_counts = Counter(
        r["source_type"] for r in all_records.data
    )
    for st, cnt in type_counts.items():
        print(f"  {st:20s}: {cnt:4d} chunks")
    print(f"  {'TOTAL':20s}: {len(all_records.data):4d} chunks")
    print("=" * 60)

if __name__ == "__main__":
    main()
