import chromadb
import ollama
from sentence_transformers import CrossEncoder
import json

client = chromadb.PersistentClient(
    path="./chroma_db"
)

final_menu_collection = client.get_collection(
    name="hamburger_king_final"
)

reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3"
)

def items_to_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text-v2-moe",
        input=text
    )
    return response["embeddings"][0]

def search_final_menu(query_text, price, calories, type, allergens):

    where_conditions = []

    if price is not None:
        where_conditions.append({"price": {"$lte": price}})

    if calories is not None:
        where_conditions.append({"calories": {"$lte": calories}})

    if type is not None:
        where_conditions.append({"type": {"$eq": type}})

     # and要至少兩個才能用
    if len(where_conditions) >= 2:
        where = {"$and": where_conditions}
    elif len(where_conditions) == 1:
        where = where_conditions[0]
    else:
        where = None
    
    results_ranked = []

    for query in query_text:

        #用30怕免得過濾後沒有資料
        retrieval_results = final_menu_collection.query(
            query_embeddings=[items_to_embedding(query)],
            n_results=30,
            where = where
        )

        # 排除過敏源
        filtered_results = []

        for document, metadata in zip(
            retrieval_results["documents"][0],
            retrieval_results["metadatas"][0]
        ):

            allergens_list = json.loads(metadata["allergens"])

            if allergens:
                if any(allergen in allergens_list for allergen in allergens):
                    continue

            filtered_results.append(
                (document, metadata)
            )

        # 沒有符合條件的資料
        if not filtered_results:
            continue

        pairs = [
            [query, document]  for document, metadata in filtered_results
        ]

        scores = reranker.predict(pairs)

        reranked = sorted(
            zip(
                [document for document, metadata in filtered_results],
                [metadata for document, metadata in filtered_results],
                scores
            ),
            key=lambda x: x[2],
            reverse=True
        )[:10]

        results_ranked.append(reranked)

    #取得內容物
    return results_ranked

if __name__ == "__main__":

    items = search_final_menu(
        ["雞肉漢堡", "牛肉漢堡"],
        200,
        None,
        None,
        []
    )

    for category in items:
        for item in category:
            print("產品資訊：",item[1]["name"])
            print("卡路里：",item[1]["calories"])
