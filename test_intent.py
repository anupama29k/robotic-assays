from ai_layer import classify_query_intent, search_corpus_reranked

queries = [
    'What does ICH Q14 say about analytical procedure development',
    'How do I run BIO_005 ELISA',
    'What is Z-factor and what threshold should I accept',
    'How long should mAb samples be stored for accelerated stability',
    'Compare HMWS levels between BIO_003 and what Q6B requires',
]

for q in queries:
    intent = classify_query_intent(q)
    print()
    print(f'Q: {q}')
    print(f'   intent: {intent["intent"]}')
    print(f'   reg/lib: {intent["regulatory_weight"]:.2f} / {intent["library_weight"]:.2f}')
    print(f'   reason: {intent.get("reasoning", "")[:80]}')

print()
print('=' * 60)
print('FULL RETRIEVAL TEST')
print('=' * 60)
results = search_corpus_reranked(
    'Compare HMWS levels between BIO_003 and what Q6B requires',
    top_k=5,
)
for r in results:
    src = r['source_file']
    score = r.get('rerank_score', '-')
    src_type = r.get('source_type', '?')
    print(f'  [{score}] [{src_type}] {src}')
