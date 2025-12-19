from Services.notion_service import fetch_db_properties
from config import NOTION_DB_USERS_ID
from Models.user import User

# ---------------------------------
# ユーザー一覧取得
# ---------------------------------
def get_users():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_USERS_ID, ["name", "display_name"])
        
        # Userモデルに変換
        for item in data:
            user = User.from_notion(item)
            results.append({
                "page_id": user.page_id,
                "name": user.name,
                "display_name": user.display_name or user.name  # display_nameがなければnameを使用
            })

    except Exception as e:
        print("get_users error:", e)

    return results