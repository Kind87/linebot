import json

with open("hamburgerKing_final_mix.json", "r", encoding="utf-8") as f:
    menus = json.load(f)

final_menus = []

for menu in menus:

    if len(menu["content"]) == 1:
        menu['type'] = 'single'
    else :
        menu['type'] = 'meal'
    
    final_menus.append(menu)


with open("hamburgerKing_final.json", "w", encoding="utf-8") as f:
    json.dump(final_menus, f, ensure_ascii=False, indent=4)