import ollama
import json


def parse_user_query(user_query):

    prompt = f"""
        你是一個餐廳搜尋條件解析器。

        請分析使用者的需求，並且根據需求填上合適的JSON格式，最後輸出 JSON。

        JSON 格式：

        {{
            "semantic_query": "",
            "price_max": null,
            "calories_max": null,
            "type": null,
            "exclude_allergens": []
            "food_itent": ""
        }}

        規則：

        1. semantic_query：
        - 放使用者想找的餐點語意
        - 必須是一個陣列
        - 如果使用者只輸入漢堡，就放 ["漢堡"]
        - 如果使用者輸入「套餐」，就放 ["漢堡套餐"]
        - 如果使用者輸入「單點」，就放 ["漢堡"]
        - 如果使用者只有一個餐點需求，就放一個元素
        - 只有當「和」、「及」、「或」明確表示兩個以上獨立的餐點需求時才拆分，如果連接詞只是餐點名稱或內容物的一部分，不要拆分。
        - 不要把連接詞前後的需求合併成一個字串
        - 不要放價格、卡路里、過敏原等條件

        例如：
        「我想吃雞肉漢堡」
        → ["雞肉漢堡"]

        「我想吃牛肉漢堡或雞肉漢堡」
        → ["牛肉漢堡", "雞肉漢堡"]

        「牛肉套餐漢堡和雞肉漢堡套餐」
        → ["牛肉漢堡套餐", "雞肉漢堡套餐"]

        「牛肉套餐及雞肉套餐」
        → ["牛肉漢堡套餐", "雞肉漢堡套餐"]        

        2. price_max：
        - 使用者說「200元以下」就填 200，以此類推
        - 沒有提到價格就填 null

        3. calories_max：
        - 使用者說「600大卡以下」就填 600，以此類推
        - 沒有提到卡路里就填 null

        4. type：
        - 使用者明確說「套餐」就填 "meal"
        - 使用者明確說「單點」就填 "single"
        - 沒有提到就填 null

        5. exclude_allergens：
        - 使用者說「不要奶」就填 ["奶"]，以此類推
        - 使用者說「不要乳製品」就填 ["奶"]，以此類推
        - 使用者說「不要奶、花生、'蛋'」就填 ["奶", "花生", "蛋"]，以此類推
        - 使用者說「不要小麥或麥」，只要出現有關麥的話，就填 ["麩質之穀物"]
        - 麻煩把有關過敏來源的像似資訊，都去對比有沒有跟 ['甲殼類'、'魚'、'蛋'、'奶'、'麩質之穀物'、'大豆'、'花生'、'芝麻'、'堅果'、'芒果'] 這些過敏原有關聯，有的話就放進去
        - 麻煩把使用者說的過敏原都整理成一個陣列，並且去除重複
        - 沒有提到就填 []

        6. food_itent：
        - 如果使用者沒有指定要特定餐點的資訊或意圖，就填 "recommendation"
        - 如果使用者說「我想吃牛肉漢堡套餐，價格不要超過300元，卡路里大概800卡左右，最好不要有奶類過敏源。」就填 "recommendation"
        - 如果使用者說「推薦我一個套餐」就填 "recommendation"
        - 如果使用者有指定特定想了解的餐點資訊，就填 "detail"
        - 如果使用者說「我想要知道華堡的價格和卡路里是多少？」就填 "detail"
        - 如果使用者說「我要找名字叫牛肉漢堡的產品」就填 "detail"
        - 如果使用者說「請問華堡有什麼內容？」就填 "detail"
        - 如果使用者說「華堡的價格是多少？」就填 "detail"
        
        7. 最後只能輸出合法的 JSON。
           不要輸出 ```json、```、說明文字或其他任何內容。
           JSON 必須可以直接交給 Python 的 json.loads() 解析。

        使用者問題：

        {user_query}
    """

    response = ollama.chat(
        model="smtek/Qwen3.8-27B:Q3_K_M",
        think=False,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response["message"]["content"]

    return json.loads(result)

if __name__ == "__main__":
    query = "我想吃牛肉漢堡套餐或雞肉漢堡套餐，我對奶類過敏和魚類過敏，價格不要超過300元"

    conditions = parse_user_query(query)

    print("\n解析後：")
    print(conditions)