from text_to_llm import parse_user_query
from search_vector import search_final_menu
from llm_analyze import analyze_with_llm
from textwrap import dedent
import json

def parse_item_content(content_list):
    content_names = []

    for item in content_list:

        content_items = item["name"] + f" ({item['quantity']})"
        content_names.append(content_items)

    return "、".join(content_names)

def parse_item_replace(replace_list):
    replace_text = ""

    if replace_list is not None:
        count = 0
        for key, _ in replace_list.items():
            if(count > 0):
                replace_text += f"、"
            replace_text += f"{key}"
            count += 1
    else:
        replace_text = "無可替換項目"

    return replace_text

def hamburgerking_chat(user_query):

    #1.LLM 解析使用者需求，同時了解使用者需求，推薦餐點亦或是找特點餐點資料
    conditions = parse_user_query(user_query)

    categoryQuery = conditions["semantic_query"]

    print("解析後的條件：", conditions)

    #2.RAG 搜尋
    items = search_final_menu(
        conditions["semantic_query"],
        conditions["price_max"],
        conditions["calories_max"],
        conditions["type"],
        conditions["exclude_allergens"]
    )

    items_list = []

    #3.尋找使用者提供的資訊，經過RAG後取得候選值
    for index, category_item in enumerate(items):

        for category_index, category in enumerate(category_item):

            #拿metadata
            item = category[1]

            text = f"""
                使用者查詢類別：{categoryQuery[index]}
                索引：{category_index}
                餐點名稱：{item["name"]}
                分類：{item["category"]}
                子分類：{item["subCategory"]}
                內容物：{item["content"]}
                分數：{category[2]}
                """

            items_list.append(text)

    #4.根據意圖，決定要推薦餐點還是找特定餐點資訊
    if conditions["food_itent"] == "recommendation":

        #5.為推薦餐點，所以再交給LLM 分析，已得到使用者想要的得結果
        #analyze_index是items的索引值
        analyze_index = analyze_with_llm(
            user_query,
            categoryQuery,
            items_list,
            "recommendation"
        )

        analyze_index = json.loads(analyze_index)

        analyze_result = []

        #假如analyze_index = [[1, 2], [3, 4]] ， len就等於2，代表有兩個查詢類別

        for i in range(len(analyze_index)):

            if (analyze_index[i] == ["None"]):
                analyze_result.append(f"{categoryQuery[i]}，為查無符合條件的餐點描述，請嘗試重新描述需求\n")
                continue

            analyze_result.append(f"為你推薦{categoryQuery[i]}相關的餐點：\n")

            for index in analyze_index[i]:
                item_prototype = items[i][index][1]

                # 取得內容物
                content_text = parse_item_content(json.loads(item_prototype["content"]))

                # 取得可替換項目
                replace_list = (
                    json.loads(item_prototype["replaceList"])
                    if item_prototype["replaceList"] is not None
                    else None
                )

                replace_text = parse_item_replace(replace_list)

                #組成最終傳給使用者文字
                text = dedent(f"""
                    餐點名稱：{item_prototype["name"]}
                    價格：{item_prototype["price"]} 元
                    內容物：{content_text}
                    卡路里：{item_prototype["calories"]} 大卡
                    可替換項目：{replace_text}
                    過敏源：{"、".join(json.loads(item_prototype["allergens"]))}
                """).strip()

                text += "\n"

                analyze_result.append(text)

        return analyze_result
    else:
        #6.為查詢特定餐點資訊，所以直接經過LLM分析，找出使用者想要的資訊
        analyze_filter = analyze_with_llm(
            user_query,
            categoryQuery,
            items_list,
            "detail"
        )

        print("analyze_filter: ", analyze_filter)
        analyze_filter = json.loads(analyze_filter)

        result = []

        for i,filter in enumerate(analyze_filter):
            
            fields = filter["fields"]

            if(len(filter["indices"]) > 1):
                result.append(f"{categoryQuery[i]}，為查無符合條件的餐點，以下為相關類似的餐點資訊：\n")

            for index in filter["indices"]:

                item = items[i][index][1]

                temp_result = ""

                # 取得內容物
                content_text = parse_item_content(json.loads(item["content"]))


                # 取得可替換項目
                replace_list = (
                    json.loads(item["replaceList"])
                    if item["replaceList"] is not None
                    else None
                )

                replace_text = parse_item_replace(replace_list)

                temp_result += f"餐點名稱：{item['name']}\n"

                if "price" in fields:
                    temp_result += f"價格：{item['price']} 元\n"

                if "content" in fields:
                    temp_result += f"內容物：{content_text}\n"

                if "calories" in fields:
                    temp_result += f"卡路里：{item['calories']} 大卡\n"

                if "replace" in fields:
                    temp_result += f"可替換項目：{replace_text}\n"

                if "allergens" in fields:
                    temp_result += f"過敏源：{'、'.join(json.loads(item['allergens']))}\n"

                result.append(temp_result)

        print(result)

        return result

if __name__ == "__main__":

    user_query = "我想要吃牛肉漢堡"

    result = hamburgerking_chat(user_query)

    for item in result:
        print(item)