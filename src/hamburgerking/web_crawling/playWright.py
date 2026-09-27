from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import os
import re


def remove_replace(text):
    # 移除「正常冰」
    text = re.sub(r"\s*\(正常冰\)", "", text)

    # 移除最後的「替換」
    text = re.sub(r"\s*\n替換$", "", text)

    return text

save_path = Path.home() / "Desktop" / "raw_menu.json"

def write_response_to_file(response):
    global save_path
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

def replace_append(replaceList, name, price):
    replaceList.append({
        'name': name,
        'quality': 1,
        'price_diff': price
    })

def menus_append(menus_items, title, content, price, category, subCategory, description, replaceList):
    menus_items.append({
        'name': title,
        'rowContent': content,
        'replaceList': replaceList,
        'price': price,
        'category': category,
        'subCategory': subCategory,
        'description': description
    })

def run_single_click():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            viewport={"width": 800, "height": 1080},
            permissions=[]
        )

        page = context.new_page()

        try:
            print("正在打開頁面...")

            page.goto(
                "https://www.burgerking.com.tw/category/6",
                wait_until="domcontentloaded",
                timeout=10000
            )

            print("頁面載入完成")
            page.wait_for_timeout(4000)

            page.get_by_label("Close interaction").click()

            page.wait_for_timeout(1500)
            page.locator('div.aiqua__button').click()

            page.wait_for_timeout(1000)

            #先進行開始點餐，取得資料
            page.get_by_role("button", name="開始點餐").click()
            page.wait_for_timeout(1000)

            page.locator("div select").nth(1).select_option(index=2)
            page.wait_for_timeout(1000)

            page.get_by_role("button", name="選擇門店").click()
            page.wait_for_timeout(1000)

            page.get_by_role("button", name="萬華西園店").click()
            page.wait_for_timeout(1000)

            page.locator("div select").nth(3).select_option(index=2)
            page.wait_for_timeout(1000)

            page.get_by_role("button", name="前往訂餐").click()
            page.wait_for_timeout(1000)

            item_section = page.locator("main.container section")

            page.wait_for_timeout(2000)

            menus_items = []

            #產品分類
            category = page.locator('div[class*="md:text-3xl"]').first.inner_text()

            #根據section區塊分別點擊產品
            for i in range(item_section.count() - 1):
                section = item_section.nth(i)
                subCategory = section.locator("h2").first.inner_text()
                links = section.locator("a:visible")

                ifReplace = False

                #遍歷區塊產品內容
                for link in range(links.count()):

                    #重製清單
                    replace_doument = {}

                    #進入產品內容
                    links.nth(link).click()
                    
                    #記住當前產品頁面內容
                    previous_url = page.url
                    page.wait_for_timeout(2000)

                    #產品名稱
                    title = page.locator("h1").first.inner_text()

                    #產品價格
                    price = page.locator("div.text-3xl.text-orange").inner_text()

                    #產品描述
                    description = page.locator("div#ub-oneproduct").inner_text()

                    items = page.locator("div.bg-white.border:visible")

                    content = ''

                    print(items.count())
                    
                    #只有單點
                    if items.count() == 0:
                        print("單點商品")
                        menus_append(menus_items, title, title, price, category, subCategory, description, None)
                        print(menus_items)
                        page.go_back() 
                        continue

                    #產品為套餐，出現多個品項
                    for j in range(items.count()):

                        item = items.nth(j)
                        item_text = item.inner_text()


                        #如果產品能夠替換
                        if "替換" in item_text:

                            item_text = remove_replace(item_text)
                            content += item_text
                            
                            ifReplace = True
                            #點擊替換按鈕
                            item.get_by_role("button", name="替換").click()

                            page.wait_for_timeout(1000)

                            replace_items = page.locator("div.mt-3 div.bg-white.border:visible")

                            replace_items.locator("button").first.click()

                            replaceList = []
                            for k in range(replace_items.count()):

                                replace_name = replace_items.nth(k).locator("div").first.inner_text()
                                replace_price = replace_items.nth(k).locator("div.text-orange").first.inner_text()
                                replace_append(replaceList, replace_name, replace_price)

                            replace_doument[remove_replace(item_text)] = replaceList

                            page.goto(previous_url)
                        else:
                            content += item_text


                    if ifReplace:
                        menus_append(menus_items, title, content, price, category, subCategory, description, replace_doument)
                    else:
                        menus_append(menus_items, title, content, price, category, subCategory, description, None)
                    print(menus_items)

                    # 所有品項的頁面重新查詢
                    page.go_back() 
        
        
            return menus_items

        except Exception as e:
            print("發生錯誤：")
            print(type(e).__name__)
            print(e)
            raise


if __name__ == "__main__":
    menus_items = run_single_click()

    print("run_single_click 回傳：", menus_items)
    print("型態：", type(menus_items))

    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)

        old_data.extend(menus_items)
    else:
        old_data = menus_items

    write_response_to_file(old_data)