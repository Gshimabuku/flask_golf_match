from Services.notion_service import fetch_db_properties
from config import NOTION_DB_COURSES_ID,NOTION_DB_LAYOUTS_ID,NOTION_DB_HOLES_ID
from Const.course_type import DISPLAY

# ---------------------------------
# コース一覧取得（coursesテーブルのみ）
# ---------------------------------
def get_courses():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_COURSES_ID)

        for course in data:
            course["type_display"] = DISPLAY.get(course["type"], "不明")

        results = data

    except Exception as e:
        print("get_courses error:", e)

    return results

def get_layouts():
    results = []

    try:
        data = fetch_db_properties(NOTION_DB_LAYOUTS_ID)

        results = data

    except Exception as e:
        print("get_layouts error:", e)

    return results