from Services.notion_service import fetch_db_properties
from config import NOTION_DB_COURSES_ID,NOTION_DB_LAYOUTS_ID,NOTION_DB_HOLES_ID
from Models.course import Course
from Models.layout import Layout
from Models.hole import Hole

# ---------------------------------
# コース一覧取得
# ---------------------------------
def get_courses():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_COURSES_ID)
        results = [Course.from_notion(d) for d in data]

    except Exception as e:
        print("get_courses error:", e)

    return results

# ---------------------------------
# レイアウト一覧取得
# ---------------------------------
def get_layouts():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_LAYOUTS_ID)
        results = [Layout.from_notion(d) for d in data]

    except Exception as e:
        print("get_layouts error:", e)

    return results

# ---------------------------------
# ホール一覧取得
# ---------------------------------
def get_holes():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_HOLES_ID)
        results = [Hole.from_notion(d) for d in data]

    except Exception as e:
        print("get_holes error:", e)

    return results