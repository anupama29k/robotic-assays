from ai_layer import search_corpus_reranked

print('=' * 60)
print('TEST 1 — Stability testing (Q5C)')
print('=' * 60)
results = search_corpus_reranked(
    'How long should I store mAb samples for accelerated stability testing',
    top_k=3
)
for r in results:
    src = r['source_file']
    score = r.get('rerank_score', '-')
    print(f'  [{score}] {src}')

print()
print('=' * 60)
print('TEST 2 — AQbD method development (Q14)')
print('=' * 60)
results = search_corpus_reranked(
    'What is analytical quality by design and how do I apply it to method development',
    top_k=3
)
for r in results:
    src = r['source_file']
    score = r.get('rerank_score', '-')
    print(f'  [{score}] {src}')

print()
print('=' * 60)
print('TEST 3 — Comparability (Q5E)')
print('=' * 60)
results = search_corpus_reranked(
    'My CDMO changed the production process. What comparability studies do I need',
    top_k=3
)
for r in results:
    src = r['source_file']
    score = r.get('rerank_score', '-')
    print(f'  [{score}] {src}')
