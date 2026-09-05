from ai_layer import search_corpus_reranked

print('=' * 60)
print('CITATION GROUNDING TEST')
print('=' * 60)

queries = [
    'What does ICH Q14 say about multivariate methods',
    'How do I validate accuracy for an analytical method',
    'What are stability testing requirements for biotech products',
]

for q in queries:
    print()
    print(f'Q: {q}')
    print('-' * 60)
    results = search_corpus_reranked(q, top_k=3)
    for r in results:
        section = (r.get('metadata') or {}).get('section', 'No section')
        score = r.get('rerank_score', '-')
        print(f'  [{score}] {r["source_file"]}')
        print(f'        section: {section}')
