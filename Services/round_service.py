from datetime import datetime
from Services.notion_service import fetch_db_properties,create_page,fetch_page,build_id_name_map,resolve_relation
from config import NOTION_DB_ROUNDS_ID,NOTION_DB_GAME_SETTINGS_ID,NOTION_DB_COURSES_ID,NOTION_DB_USERS_ID

# ---------------------------------
# ラウンド一覧取得
# ---------------------------------
def get_rounds():
    results = []

    try:
        rounds = fetch_db_properties(NOTION_DB_ROUNDS_ID)

        courses = fetch_db_properties(NOTION_DB_COURSES_ID, ["name"])
        course_map = build_id_name_map(courses, "name")
        for r in rounds:
            r["course_name"] = resolve_relation(
                r.get("course", []),
                course_map
            )

        users = fetch_db_properties(NOTION_DB_USERS_ID, ["name"])
        user_map = build_id_name_map(users, "name")
        for r in rounds:
            for key in ["member1", "member2", "member3", "member4"]:
                r[key] = resolve_relation(
                    r.get(key, []),
                    user_map
                )
                
        for r in rounds:
            members = []
            for key in ["member1","member2","member3","member4"]:
                members += r.get(key, [])
            r["members"] = members

        results = rounds

    except Exception as e:
        print("get_rounds error:", e)

    return results

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
# ゲーム設定新規登録
# ---------------------------------
def add_game_setting(data: dict) -> str:

    play_date = data["play_date"]
    round_page_id = data["round_page_id"]
    olympic_toggle = data["olympic_toggle"]
    snake_toggle = data["snake_toggle"]
    nearpin_toggle = data["nearpin_toggle"]

    # title 用 name（yymmdd-hhmm）
    now = datetime.now()
    name = f"game-{play_date.replace('-', '')[2:]}-{now.strftime('%H%M')}"

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
        notion_data["olympic_member"] = data["olympic_member"]
    
    if snake_toggle:
        notion_data["snake"] = data["snake"]
        notion_data["snake_member"] = data["snake_member"]

    if nearpin_toggle:
        notion_data["nearpin"] = bool(1)
        notion_data["nearpin_member"] = data["nearpin_member"]

    column_types = {
        "name": "title",
        "round": "relation",
    }

    if olympic_toggle:
        column_types["gold"] = "number"
        column_types["silver"] = "number"
        column_types["bronze"] = "number"
        column_types["iron"] = "number"
        column_types["diamond"] = "number"
        column_types["olympic_member"] = "relation"

    if snake_toggle:
        column_types["snake"] = "select"
        column_types["snake_member"] = "relation"

    if nearpin_toggle:
        column_types["nearpin"] = "checkbox"
        column_types["nearpin_member"] = "relation"

    # Notion 保存
    page = create_page(NOTION_DB_GAME_SETTINGS_ID, notion_data, column_types)

    # 作成された page_id を返す
    return page["id"]