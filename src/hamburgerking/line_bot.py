from fastapi import FastAPI, Request
from linebot.v3 import WebhookParser
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from dotenv import load_dotenv
from textwrap import dedent
from main_hamburgerking import hamburgerking_chat
from intent_analyze import intent_analyze_with_llm
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

load_dotenv()

CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)

parser = WebhookParser(CHANNEL_SECRET)

def reply_message(reply_token, text):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    TextMessage(text=text)
                ]
            )
        )

def push_message(user_id, text):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[
                    TextMessage(text=text)
                ]
            )
        )

llm_processing = False #設定一個全域變數來追蹤 LLM 是否正在處理請求

@app.post("/webhook")
async def webhook(request: Request):

    global llm_processing

    # 取得 LINE Webhook 資料
    body = await request.body()

    signature = request.headers.get("x-line-signature")

    events = parser.parse(
        body.decode("utf-8"),
        signature
    )

    # 處理每一個 LINE Event
    for event in events:

        # 只處理訊息事件
        if isinstance(event, MessageEvent):

            # 只處理文字訊息
            if isinstance(event.message, TextMessageContent):

                user_message = event.message.text
                print("使用者：", user_message)

                # 檢查目前是否有 LLM 正在處理
                print("目前 llm_processing =", llm_processing)

                if llm_processing:

                    print("⚠️ LLM 正在處理，擋住這次訊息")

                    push_message(
                        event.source.user_id,
                        "請稍等，我處理您前一次的問題。"
                    )

                    return "OK"

                # 開始 LLM 處理
                llm_processing = True
                try:
                    # push_message(
                    #         event.source.user_id,
                    #         "我正在分析您的需求，請稍等一下"
                    # )
                    # 意圖分析
                    user_intent = intent_analyze_with_llm(user_message)
                    
                    print("使用者意圖：", user_intent)

                    # 超出機器人服務範圍
                    if user_intent == "out_of_scope":

                        reply_message(
                            event.reply_token,
                            "不好意思，我主要提供漢堡王餐點相關資訊喔！"
                        )
                    # 詢問機器人功能
                    elif user_intent == "bot_function":

                        reply_message(
                            event.reply_token,
                            dedent(""" 
                                我可以幫你：
                                ・推薦餐點
                                ・查詢餐點價格
                                ・查詢套餐內容
                                ・查詢卡路里
                                ・查詢內容物
                                ・查詢過敏源

                                例子：
                                「我想吃牛肉漢堡套餐，價格不要超過300元，卡路里大概800卡左右，最好不要有奶類過敏源。」
                                「華堡的價格跟卡路里是多少啊？」
                                """
                            ).strip()
                        )
                    # 一般聊天
                    elif user_intent == "casual_chat":

                        reply_message(
                            event.reply_token,
                            dedent("""
                                嗨！你好阿！我是漢堡王小助手

                                今天想吃點什麼樣的漢堡呢？
                                請打下你想吃的餐點條件，我會幫你推薦適合的餐點。

                                例如：

                                「我想吃牛肉漢堡套餐，價格不要超過300元，
                                卡路里大概800卡左右，最好不要有奶類過敏源。」

                                直接告訴我你想吃什麼就可以囉！
                            """).strip()
                        )
                    # 餐點查詢
                    elif user_intent == "food_query":
                        # 先使用 reply_token 回覆一次，告訴使用者目前正在處理

                        reply_message(
                            event.reply_token,
                            "正在幫您查詢漢堡王的餐點資訊，請稍等一下"
                        )

                        # 開始查詢，等待非同步的結果，避免阻塞主線程
                        result = await run_in_threadpool(
                            hamburgerking_chat,
                            user_message
                        )

                        print("推薦結果：", result)
                        # 將結果組合成 LINE 可以顯示的文字
                        reply_text = "\n".join(result)

                        # reply_token 已經使用過，所以這裡改使用 Push Message
                        push_message(
                            event.source.user_id,
                            dedent(reply_text).strip()
                        )
                    # 未知意圖
                    else:
                        reply_message(
                            event.reply_token,
                            "不好意思，我目前無法理解您的需求"
                        )
                # 錯誤處理
                except Exception as e:
                    print("處理請求時發生錯誤：", str(e))
                    push_message(
                        event.source.user_id,
                        "抱歉，我在處理您的請求時發生錯誤，請嘗試重新輸入或將描述得更清楚一點。"
                    )

                # 無論成功或失敗，都一定解除 LLM 處理狀態
                finally:

                    llm_processing = False

                return "OK"