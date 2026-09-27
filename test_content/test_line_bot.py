from main_hamburgerking import hamburgerking_chat
from intent_analyze import intent_analyze_with_llm

def user_intent_analysis(user_it):

    result = None

    if user_intent == "food_query":
        # result = hamburgerking_chat(user_query)
        result = "最終推薦餐點："
    elif user_intent == "bot_function":
        result = f""" 
        我是漢堡王小助手 🍔
        我可以幫你：
        ・推薦餐點
        ・查詢餐點價格
        ・查詢套餐內容
        ・查詢卡路里
        ・查詢內容物
        ・查詢過敏源
        ・查詢餐點替換選項

        例子：
        「我想吃牛肉漢堡套餐，價格不要超過300元，卡路里大概800卡左右，最好不要有奶類過敏源。」
        直接告訴我你想吃什麼就可以囉！"""
    elif user_intent == "casual_chat":
        result = f"""
        嗨!你好阿!我是漢堡王小助手 🍔，
        今天想吃點什麼樣的漢堡呢，請打下你想吃的餐點條件，我會幫你推薦最適合的餐點。"""
    elif user_intent == "out_of_scope":
        result = f"""
        不好意思，我主要提供漢堡王餐點相關資訊喔 🍔"""

    return result

if __name__ == "__main__":
    query = "你可以做些什麼事啊"
    user_intent = intent_analyze_with_llm(query)

    result = user_intent_analysis(user_intent)
    print(result)
