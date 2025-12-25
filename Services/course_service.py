from Services.notion_service import fetch_db_properties, create_page, delete_page
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
# コース詳細取得
# ---------------------------------
def get_course_detail(course_id: str):
    """
    コースIDから詳細情報を取得（レイアウトとホール情報を含む）
    
    Args:
        course_id: コースのpage_id
        
    Returns:
        course: Courseモデル
        layouts: レイアウトとホール情報のリスト
    """
    try:
        # コース情報取得
        course_data = fetch_db_properties(NOTION_DB_COURSES_ID)
        course = None
        for c in course_data:
            if c.get("page_id") == course_id:
                course = Course.from_notion(c)
                break
        
        if not course:
            return None, []
        
        # レイアウト情報取得
        layouts_data = fetch_db_properties(NOTION_DB_LAYOUTS_ID)
        layouts = []
        
        for layout_data in layouts_data:
            # このコースに関連するレイアウトのみ
            if course_id in layout_data.get("course", []):
                layout = Layout.from_notion(layout_data)
                
                # ホール情報取得
                holes_data = fetch_db_properties(NOTION_DB_HOLES_ID)
                holes = []
                
                for hole_data in holes_data:
                    # このレイアウトに関連するホールのみ
                    if layout.page_id in hole_data.get("layout", []):
                        hole = Hole.from_notion(hole_data)
                        holes.append(hole)
                
                # ホール番号でソート
                holes.sort(key=lambda h: h.hole_number or 0)
                layout.holes = holes
                layouts.append(layout)
        
        return course, layouts
        
    except Exception as e:
        print("get_course_detail error:", e)
        return None, []

# ---------------------------------
# コース新規作成
# ---------------------------------
def add_course(course_data: dict, layouts_data: list) -> str:
    """
    コース、レイアウト、ホールを一括作成
    
    Args:
        course_data: コース情報 (name, type, par, address)
        layouts_data: レイアウト情報のリスト [{'layout_name': str, 'pars': [int]}]
        
    Returns:
        作成されたコースのpage_id
    """
    try:
        # 1. コース作成
        course_column_types = {
            "name": "title",
            "course_type": "select",
            "par": "number",
            "address": "rich_text"
        }
        
        course_props = {
            "name": course_data["name"],
            "course_type": course_data["course_type"],
            "par": course_data.get("par"),
            "address": course_data.get("address")
        }
        
        course_response = create_page(NOTION_DB_COURSES_ID, course_props, course_column_types)
        course_page_id = course_response["id"]
        
        # 2. 各レイアウトとホールを作成
        for layout_data in layouts_data:
            layout_name = layout_data["layout_name"]
            pars = layout_data["pars"]
            
            # レイアウトのPAR合計を計算
            layout_par = sum(pars)
            
            # レイアウト作成
            layout_column_types = {
                "name": "title",
                "course": "relation",
                "layout_name": "rich_text",
                "par": "number"
            }
            
            layout_props = {
                "name": f"{course_data['name']}-{layout_name}",
                "course": [course_page_id],
                "layout_name": layout_name,
                "par": layout_par
            }
            
            layout_response = create_page(NOTION_DB_LAYOUTS_ID, layout_props, layout_column_types)
            layout_page_id = layout_response["id"]
            
            # 各ホールを作成
            hole_column_types = {
                "name": "title",
                "layout": "relation",
                "hole_number": "number",
                "par": "number"
            }
            
            for hole_num, hole_par in enumerate(pars, start=1):
                hole_props = {
                    "name": f"{course_data['name']}-{layout_name}-{hole_num}",
                    "layout": [layout_page_id],
                    "hole_number": hole_num,
                    "par": hole_par
                }
                
                create_page(NOTION_DB_HOLES_ID, hole_props, hole_column_types)
        
        return course_page_id
        
    except Exception as e:
        print("add_course error:", e)
        raise e
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

# ---------------------------------
# コース削除
# ---------------------------------
def delete_course(course_id: str) -> bool:
    """
    コースとそれに関連するレイアウト・ホールを削除（アーカイブ）
    
    Args:
        course_id: 削除するコースのpage_id
        
    Returns:
        成功: True, 失敗: False
    """
    try:
        # 1. このコースに関連するレイアウトを取得
        layouts_data = fetch_db_properties(NOTION_DB_LAYOUTS_ID)
        layout_ids = []
        
        for layout_data in layouts_data:
            if course_id in layout_data.get("course", []):
                layout_ids.append(layout_data["page_id"])
        
        # 2. 各レイアウトに関連するホールを削除
        if layout_ids:
            holes_data = fetch_db_properties(NOTION_DB_HOLES_ID)
            
            for hole_data in holes_data:
                hole_layout_ids = hole_data.get("layout", [])
                # このホールが削除対象のレイアウトに属している場合
                if any(layout_id in hole_layout_ids for layout_id in layout_ids):
                    delete_page(hole_data["page_id"])
        
        # 3. レイアウトを削除
        for layout_id in layout_ids:
            delete_page(layout_id)
        
        # 4. コースを削除
        delete_page(course_id)
        
        return True
        
    except Exception as e:
        print("delete_course error:", e)
        return False
