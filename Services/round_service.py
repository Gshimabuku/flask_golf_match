from datetime import datetime
from Services.notion_service import fetch_db_properties,create_page,fetch_page,build_id_name_map,resolve_relation,update_page
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

        users = fetch_db_properties(NOTION_DB_USERS_ID, ["display_name"])
        user_map = build_id_name_map(users, "display_name")
        for r in rounds:
            # membersを直接取得
            r["members"] = resolve_relation(r.get("members", []), user_map)

        results = rounds

    except Exception as e:
        print("get_rounds error:", e)

    return results

# ---------------------------------
# ラウンド詳細取得
# ---------------------------------
def get_round_detail(round_id: str):
    """指定されたラウンドの詳細情報を取得"""
    try:
        rounds = fetch_db_properties(NOTION_DB_ROUNDS_ID, ["name", "play_date", "course", "layout_out", "layout_in", "members"])
        round_data = next((r for r in rounds if r["page_id"] == round_id), None)
        
        if not round_data:
            return None
        
        # コース名を取得
        courses = fetch_db_properties(NOTION_DB_COURSES_ID, ["name"])
        course_ids = round_data.get("course", [])
        if course_ids:
            course = next((c for c in courses if c["page_id"] == course_ids[0]), None)
            round_data["course_name"] = course.get("name", "") if course else ""
            round_data["course_id"] = course_ids[0]
        else:
            round_data["course_name"] = ""
            round_data["course_id"] = ""
        
        # メンバー情報を取得
        users = fetch_db_properties(NOTION_DB_USERS_ID, ["name", "display_name"])
        member_ids = round_data.get("members", [])
        members = []
        member_names = []
        for user in users:
            if user["page_id"] in member_ids:
                display_name = user.get("display_name") or user.get("name", "")
                members.append({
                    "page_id": user["page_id"],
                    "name": user.get("name", ""),
                    "display_name": display_name
                })
                member_names.append(display_name)
        
        round_data["member_list"] = members
        round_data["members"] = member_names  # テンプレート用に表示名リストを設定
        
        return round_data
    except Exception as e:
        print("get_round_detail error:", e)
        return None

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

    # membersを配列で格納
    members = []
    for i in range(1, member_count + 1):
        members.append(data[f"member{i}"])

    notion_data = {
        "name": name,
        "play_date": play_date,
        "course": [course],
        "layout_in": [layout_in],
        "layout_out": [layout_out],
        "members": members
    }

    column_types = {
        "name": "title",
        "play_date": "date",
        "course": "relation",
        "layout_in": "relation",
        "layout_out": "relation",
        "members": "relation"
    }

    # Notion 保存
    page = create_page(NOTION_DB_ROUNDS_ID, notion_data, column_types)

    # 作成された page_id を返す
    return page["id"]

# ---------------------------------
# ラウンド完了状態を更新
# ---------------------------------
def update_round_complete(round_id: str, is_complete: bool):
    """ラウンドのcompleteフラグを更新"""
    try:
        notion_data = {
            "complete": is_complete
        }
        
        column_types = {
            "complete": "checkbox"
        }
        
        update_page(round_id, notion_data, column_types)
        print(f"Round {round_id} complete status updated to {is_complete}")
        
    except Exception as e:
        print(f"update_round_complete error: {e}")

# ---------------------------------
# ラウンド削除
# ---------------------------------
def delete_round(round_id: str) -> bool:
    """
    ラウンドを削除（アーカイブ）
    
    Args:
        round_id: 削除するラウンドのpage_id
        
    Returns:
        成功: True, 失敗: False
    """
    try:
        from Services.notion_service import delete_page
        delete_page(round_id)
        print(f"Round {round_id} deleted successfully")
        return True
    except Exception as e:
        print(f"delete_round error: {e}")
        return False

# ---------------------------------
# ラウンド更新
# ---------------------------------
def update_round(round_id: str, data: dict) -> bool:
    """
    ラウンド情報を更新
    
    Args:
        round_id: 更新するラウンドのpage_id
        data: 更新データ（play_date, course, layout_out, layout_in, members）
        
    Returns:
        成功: True, 失敗: False
    """
    try:
        notion_data = {}
        column_types = {}
        
        if "play_date" in data:
            notion_data["play_date"] = data["play_date"]
            column_types["play_date"] = "date"
        
        if "course" in data:
            notion_data["course"] = [data["course"]]
            column_types["course"] = "relation"
        
        if "layout_out" in data:
            notion_data["layout_out"] = [data["layout_out"]]
            column_types["layout_out"] = "relation"
        
        if "layout_in" in data:
            notion_data["layout_in"] = [data["layout_in"]]
            column_types["layout_in"] = "relation"
        
        if "members" in data:
            notion_data["members"] = data["members"]
            column_types["members"] = "relation"
        
        update_page(round_id, notion_data, column_types)
        print(f"Round {round_id} updated successfully")
        return True
    except Exception as e:
        print(f"update_round error: {e}")
        return False
