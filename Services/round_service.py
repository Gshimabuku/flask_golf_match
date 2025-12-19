from datetime import datetime
from Services.notion_service import fetch_db_properties,create_page,fetch_page,build_id_name_map,resolve_relation
from Services.game_setting_service import add_game_setting
from config import NOTION_DB_ROUNDS_ID,NOTION_DB_COURSES_ID,NOTION_DB_USERS_ID

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
            r["course_name"] = ", ".join(
                resolve_relation(
                    r.get("course", []),
                    course_map
                )
            )

        users = fetch_db_properties(NOTION_DB_USERS_ID, ["name"])
        user_map = build_id_name_map(users, "name")
        for r in rounds:
            # member1-4を統合してmembersに格納
            member_ids = []
            for key in ["member1", "member2", "member3", "member4"]:
                member_ids.extend(r.get(key, []))
            r["members"] = resolve_relation(member_ids, user_map)

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
