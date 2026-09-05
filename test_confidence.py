from ai_layer import (
    search_corpus_reranked,
    classify_query_intent,
    compute_retrieval_confidence,
)

queries = [
    ('Strong retrieval expected',
     'How do I detect aggregation in my mAb'),
    ('Strong regulatory query',
     'What does ICH Q14 say about analytical procedure development'),
    ('Likely medium confidence',
     'How do I calibrate my pH meter and what are the acceptance criteria'),
    ('Likely low confidence',
     'How do I do a viral clearance study'),
    ('Comparison query',
     'Compare ICH Q2 and FDA bioanalytical validation requirements'),
]

for label, q in queries:
    print()
    print('=' * 60)
    print(label)
    print(f'Q: {q}')
    print('=' * 60)

    chunks = search_corpus_reranked(q, top_k=5)
    intent = classify_query_intent(q)
    conf = compute_retrieval_confidence(chunks, intent)

    print(f'Confidence: {conf["confidence"]} ({conf["score"]}/100)')
    print(f'Reasoning: {conf["reasoning"]}')
    print(f'Factors:')
    for k, v in conf['factors'].items():
        print(f'   {k}: {v}')
