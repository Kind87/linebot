import ollama
import json

with open("hamburgerKing_menu.json", "r", encoding="utf-8") as f:
    menus = json.load(f)

def items_to_embedding(text):
    return ollama.embed(
        model="nomic-embed-text-v2-moe",
        input=text
    )

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
    描述：{menu["description"]}
    """

    return text


for menu in menus:
    text = menu_to_text(menu)
    response = items_to_embedding(text)


    embedding = response["embeddings"][0]

    print("餐點：", menu["name"])
    print("Embedding 維度：", len(embedding))
    print("前 10 個數值：", embedding[:10])