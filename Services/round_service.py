from datetime import datetime
from Services.notion_service import fetch_db_properties,create_page,fetch_page
from config import NOTION_DB_ROUNDS_ID,NOTION_DB_GAME_SETTINGS_ID

# ---------------------------------
# ラウンド新規登録
# ---------------------------------
def add_round(data: dict) -> str:
    
    play_date = data["play_date"]
    course = data["course"]
    layout_in = data["layout_in"]
    layout_out = data["layout_out"]
    member_count = int(data["member_count"])

    # title 用 name（yymmdd-hhmm）
    now = datetime.now()
    name = f"{play_date.replace('-', '')[2:]}-{now.strftime('%H%M')}"

    notion_data = {
        "name": name,
        "play_date": play_date,
        "course": [course],
        "layout_in": [layout_in],
        "layout_out": [layout_out],
    }

    for i in range(1, member_count + 1):
        notion_data[f"member{i}"] = [data[f"member{i}"]]

    column_types = {
        "name": "title",
        "play_date": "date",
        "course": "relation",
        "layout_in": "relation",
        "layout_out": "relation",
    }

    for i in range(1, member_count + 1):
        column_types[f"member{i}"] = "relation"

    # Notion 保存
    page = create_page(NOTION_DB_ROUNDS_ID, notion_data, column_types)

    # 作成された page_id を返す
    return page["id"]

# ---------------------------------
# ラウンド新規登録
# ---------------------------------
def add_game_setting(data: dict) -> str:

    round_page_id = data["round_page_id"]
    olympic_toggle = data["olympic_toggle"]
    snake_toggle = data["snake_toggle"]
    nearpin_toggle = data["nearpin_toggle"]

    name = "aaa"

    notion_data = {
        "name": name,
        "round": [round_page_id],
    }

    if olympic_toggle:
        notion_data["gold"] = int(data["gold"])
        notion_data["silver"] = int(data["silver"])
        notion_data["bronze"] = int(data["bronze"])
        notion_data["iron"] = int(data["iron"])
        notion_data["diamond"] = int(data["diamond"])
    
    if snake_toggle:
        notion_data["snake"] = data["snake"]

    if nearpin_toggle:
        notion_data["nearpin"] = bool(1)

    column_types = {
        "name": "title",
        "round": "relation",
    }

    if olympic_toggle:
        notion_data["gold"] = "number"
        notion_data["silver"] = "number"
        notion_data["bronze"] = "number"
        notion_data["iron"] = "number"
        notion_data["diamond"] = "number"

    if snake_toggle:
        notion_data["snake"] = "select"

    if nearpin_toggle:
        notion_data["nearpin"] = "checkbox"

    # Notion 保存
    page = create_page(NOTION_DB_GAME_SETTINGS_ID, notion_data, column_types)

    # 作成された page_id を返す
    return page["id"]