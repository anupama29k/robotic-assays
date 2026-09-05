from ai_layer import search_corpus_reranked

print('=' * 60)
print('TEST 1 — Quality risk management (Q9)')
print('=' * 60)
results = search_corpus_reranked(
    'How do I do a risk assessment for an analytical method',
    top_k=3
)
for r in results:
    src = r['source_file']
    score = r.get('rerank_score', '-')
    print(f'  [{score}] {src}')

print()
print('=' * 60)
print('TEST 2 — PQS deviation management (Q10)')
print('=' * 60)
results = search_corpus_reranked(
    'What does the pharmaceutical quality system require for handling deviations',
    top_k=3
)
for r in results:
    src = r['source_file']
    score = r.get('rerank_score', '-')
    print(f'  [{score}] {src}')
