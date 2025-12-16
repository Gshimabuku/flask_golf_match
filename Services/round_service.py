from datetime import datetime
from Services.notion_service import fetch_db_properties,create_page
from config import NOTION_DB_ROUNDS_ID

# ---------------------------------
# ラウンド新規登録
# ---------------------------------
def add_round(data: dict) -> str:
    
    play_date = data["play_date"]
    course = data["course"]
    layout_in = data["layout_in"]
    layout_out = data["layout_out"]
    rate = data["rate"]

    # title 用 name（yymmdd-hhmm）
    now = datetime.now()
    name = f"{play_date.replace('-', '')[2:]}-{now.strftime('%H%M')}"

    notion_data = {
        "name": name,
        "play_date": play_date,
        "course": [course],
        "layout_in": [layout_in],
        "layout_out": [layout_out],
        "rate": rate,
    }

    column_types = {
        "name": "title",
        "play_date": "date",
        "course": "relation",
        "layout_in": "relation",
        "layout_out": "relation",
        "rate": "number",
    }

    # Notion 保存（ここでのみ API を呼ぶ）
    page = create_page(NOTION_DB_ROUNDS_ID, notion_data, column_types)

    # 作成された page_id を返す
    return page["id"]