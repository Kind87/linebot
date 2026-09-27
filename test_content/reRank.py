from sentence_transformers import CrossEncoder

reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3"
)

query = "我想吃雞肉漢堡"

documents = [
    "川椒辣雞腿堡，價格169元",
    "經典脆雞堡，價格104元",
    "雙層牛肉堡，價格149元",
    "雞塊分享餐，價格199元"
]

pairs = [
    [query, document] for document in documents
]

scores = reranker.predict(pairs)

reranked = sorted(
    zip(documents, scores),
    key=lambda x: x[1],
    reverse=True
)

for document, score in reranked:
    print(f"{score:.4f} | {document}")