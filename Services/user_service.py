from Services.notion_service import fetch_db_properties
from config import NOTION_DB_USERS_ID

# ---------------------------------
# ユーザー一覧取得
# ---------------------------------
def get_users():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_COURSES_ID)

        results = data

    except Exception as e:
        print("get_users error:", e)

    return results