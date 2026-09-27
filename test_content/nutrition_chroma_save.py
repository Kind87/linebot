import ollama
import chromadb
import json


# =========================
# 1. 讀取 Burger King JSON
# =========================

with open("hamburgerKing_nutrition.json", "r", encoding="utf-8") as f:
    menus = json.load(f)

#=========================
#2. 建立 ChromaDB
#=========================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="burger_king_nutrition"
)

def items_to_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text-v2-moe",
        input=text
    )
    return response["embeddings"][0]

def menu_to_text(menu):

    if menu["allergens"] == []:
        menu["allergens"] = "不含過敏內容"
    else:
        menu['allergens'] = ('、').join(menu['allergens'])

    # 組成最後文字
    text = f"""
    餐點名稱：{menu["name"]}
    卡路里：{menu["calories"]}
    過敏源資訊：{menu["allergens"]}
    """
    return text


#存進 ChromaDB
for index, menu in enumerate(menus):

    text = menu_to_text(menu)

    print(text)

    embedding = items_to_embedding(text)

    collection.add(
        ids=[str(index)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{
            "name": menu["name"],
            "calories": menu["calories"],
            "allergens": menu["allergens"],
        }]
    )

    print(
        f"已加入：{menu['name']} "
        f"({len(embedding)} 維)"
    )


print("全部完成！")