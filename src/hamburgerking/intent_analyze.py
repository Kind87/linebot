import ollama

def intent_analyze_with_llm(user_query):

    prompt = f"""
        你是一個「餐廳聊天機器人的意圖分析器」。

        你的唯一任務是：
        分析使用者輸入的內容，判斷使用者想要執行哪一種功能，
        並且「只能回傳指定的意圖字串」，不要回答使用者的問題，
        不要解釋原因，也不要加入任何其他文字。

        【可判斷的意圖】

        1. 如果使用者只是打招呼、感謝或簡單閒聊，像是hi、你好、嗨、哈囉，沒有提到餐點， 
        判斷為 casual_chat。

        2. 如果使用者詢問「你是誰」、「你能做什麼」或「怎麼使用」，
        判斷為 bot_function。

        3. 如果使用者的內容與餐點需求有關，即使包含多個條件，
        判斷為 food_query。

        4. 如果使用者詢問餐點價格、卡路里、過敏源、內容物、
        替換項目或餐點比較，且目的是取得餐點資訊，判斷為 food_query。

        5. 如果使用者同時包含打招呼與餐點需求，
        以餐點需求為主要目的， 判斷為 food_query。
        
        不要因為出現「你好」、「嗨」、「哈囉」等打招呼文字，
        就判斷為 casual_chat。

        例如：
        「你好，我想吃牛肉漢堡」 → food_query
        「嗨，可以幫我推薦雞肉漢堡嗎？」 → food_query
        「你好，我想找300元以下的套餐」 → food_query
        「哈囉，我對奶類過敏，有推薦的餐點嗎？」 → food_query

        6. 如果一句話同時包含餐點需求與其他無關問題，
        只要主要目的仍然是餐點需求，
        判斷為 food_query。

        7. 如果使用者的問題與餐廳餐點及本聊天機器人的功能完全無關，
        判斷為 out_of_scope。

        【分類優先原則】

        如果一句話同時符合多個分類，
        請以「主要目的」為準。

        餐點需求 > 打招呼/閒聊

        例如：
        「你好，我想吃牛肉漢堡套餐，價格不要超過300元」
        → food_query

        【最終輸出】
        你現在不是客服，也不是問答機器人。
        你不需要回答使用者的問題。

        你只能從以下四個字串中選擇一個：
        food_query
        bot_function
        casual_chat
        out_of_scope

        請不要輸出：
        - JSON
        - Markdown
        - 解釋
        - 原因
        - 其他文字

        只回傳其中一個意圖字串。

        【使用者輸入】
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

    print("解析後：")
    print(result)

    return result

if __name__ == "__main__":
    query = "你好阿，今天天氣真好，我想吃牛肉漢堡套餐，價格不要超過300元，卡路里也要低一點，最好不要有奶類過敏源。"
    print("使用者輸入：", query)

    llm_text = analyze_with_llm(query)

    print("\n解析後：")
    print(llm_text)