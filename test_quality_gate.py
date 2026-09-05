from ai_layer import (
    search_corpus_multihop,
    retrieval_quality_check,
    suggest_related_topics,
)

queries = [
    ('In-corpus query',
     'How do I detect aggregation in my mAb'),
    ('Out-of-corpus query — synthetic biology',
     'How do I clone a gene into E. coli using Golden Gate assembly'),
    ('Out-of-corpus query — cell therapy',
     'What is the protocol for CAR-T cell expansion'),
    ('Borderline query',
     'How do I calibrate my pH meter'),
    ('In-corpus regulatory',
     'What does ICH Q14 say about analytical procedure development'),
]

for label, q in queries:
    print()
    print('=' * 60)
    print(f'{label}')
    print(f'Q: {q}')
    print('=' * 60)

    result = search_corpus_multihop(q, top_k=5)
    chunks = result['chunks']
    quality = retrieval_quality_check(chunks)

    print(f'Verdict: {quality["verdict"]}')
    print(f'Recommendation: {quality["recommendation"]}')
    print(f'Top similarity: {quality["top_similarity"]}')
    print(f'Relevant chunks: {quality["n_relevant"]}')
    print(f'Source diversity: {quality["source_diversity"]}')
    print(f'Reason: {quality["reason"]}')

    if quality['recommendation'] == 'refuse':
        print('   Suggesting related topics...')
        suggestions = suggest_related_topics(q)
        for s in suggestions[:3]:
            print(f'   • {s["topic"]} — {s.get("why_related", "")[:80]}')
