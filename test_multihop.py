from ai_layer import decompose_query, search_corpus_multihop

# Test 1: Simple query — should NOT decompose
print('=' * 60)
print('TEST 1 — Simple query')
print('=' * 60)
q1 = 'How do I detect aggregation in my mAb'
d1 = decompose_query(q1)
print(f'Q: {q1}')
print(f'   needs_decomposition: {d1["needs_decomposition"]}')
print(f'   sub_questions: {len(d1["sub_questions"])}')

# Test 2: Complex compare — should decompose
print()
print('=' * 60)
print('TEST 2 — Complex comparison query')
print('=' * 60)
q2 = ('Compare ICH Q2 and FDA bioanalytical validation '
      'requirements for charge variants in mAb release testing')
d2 = decompose_query(q2)
print(f'Q: {q2}')
print(f'   needs_decomposition: {d2["needs_decomposition"]}')
print(f'   strategy: {d2.get("synthesis_strategy", "")}')
print(f'   sub_questions:')
for sq in d2['sub_questions']:
    print(f'     - {sq}')

# Test 3: Full multi-hop retrieval
print()
print('=' * 60)
print('TEST 3 — Full multi-hop retrieval')
print('=' * 60)
result = search_corpus_multihop(q2, top_k=5)
print(f'Decomposed: {result["decomposition"]["was_decomposed"]}')
print(f'Sub-queries run: {len(result["retrieval_log"])}')
for log in result['retrieval_log']:
    print(f'   - {log["sub_q"][:60]}: {log["n_retrieved"]} chunks')
print()
print('Final top-5 (after merge + rerank):')
for r in result['chunks']:
    src = r['source_file']
    score = r.get('multihop_rerank_score', '-')
    sub_q = r.get('sub_query_match', '-')[:50]
    src_type = r.get('source_type', '?')
    print(f'  [{score}] [{src_type}] {src}')
    print(f'    matched sub-q: {sub_q}')
