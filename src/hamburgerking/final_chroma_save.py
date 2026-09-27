import ollama
import chromadb
import json


# =========================
# 1. 讀取 Burger King JSON
# =========================

with open("hamburgerKing_final.json", "r", encoding="utf-8") as f:
    menus = json.load(f)


# =========================
# 2. 建立 ChromaDB
# =========================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="hamburger_king_final"
)

def items_to_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text-v2-moe",
        input=text
    )
    return response["embeddings"][0]

def menu_to_text(menu):

    # 將內容物轉換為文字敘述
    content_names = []

    for item in menu["content"]:
        content_items = item["name"] + f" ({item['quantity']})"
        content_names.append(content_items)

    content_text = "、".join(content_names)

    # 將替換內容轉換為文字敘述
    replace_text = ""

    if menu["replaceList"] is not None:

        for key, items in menu["replaceList"].items():

            replace_text += f"\n{" " * 5 }{key} 可以替換成："

            for item in items:
                replace_text += f'\n{" " * 6 }- {item["name"]}（+{item["price_diff"]} 元）'
    else:
        replace_text = "無可替換項目"

    # 組成最後文字
    text = f"""
        餐點名稱：{menu["name"]}
        分類：{menu["category"]}
        子分類：{menu["subCategory"]}
        價格：{menu["price"]} 元
        內容物：{content_text}
        可替換項目：{replace_text}
        卡路里：{menu["calories"]}
        過敏源資訊：{menu["allergens"]}
        描述：{menu["description"]}
        類型：{menu["type"]}
    """

    return text


#存進 ChromaDB
for index, menu in enumerate(menus):

    text = menu_to_text(menu)

    embedding = items_to_embedding(text)

    allergens = menu["allergens"].split("、")

    collection.add(
        ids=[str(index)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{
            "name": menu["name"],
            "price": menu["price"],
            "category": menu["category"],
            "subCategory": menu["subCategory"],
            "calories": menu["calories"],
            "content": json.dumps( menu["content"], ensure_ascii=False ),
            "allergens": json.dumps( allergens, ensure_ascii=False ),
            "replaceList": json.dumps( menu["replaceList"], ensure_ascii=False ),
            'type': menu["type"]
        }]
    )

    print(
        f"已加入：{menu['name']} "
        f"({len(embedding)} 維)"
    )


print("全部完成！")