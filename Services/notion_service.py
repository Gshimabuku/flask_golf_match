import os
from notion_client import Client
from config import NOTION_API_KEY

# Notion クライアント
notion = Client(auth=NOTION_API_KEY)

# --------------------------------------------------------
# Notion → Python（読み取り）
# --------------------------------------------------------
def get_property_value(prop):
    type_ = prop["type"]
    if type_ == "title":
        return prop["title"][0]["plain_text"] if prop["title"] else ""
    if type_ == "rich_text":
        return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
    if type_ == "number":
        return prop["number"]
    if type_ == "select":
        return prop["select"]["name"] if prop["select"] else None
    if type_ == "multi_select":
        return [v["name"] for v in prop["multi_select"]]
    if type_ == "checkbox":
        return prop["checkbox"]
    if type_ == "date":
        return prop["date"]["start"] if prop["date"] else None
    if type_ == "url":
        return prop["url"]
    if type_ == "email":
        return prop["email"]
    if type_ == "phone_number":
        return prop["phone_number"]
    if type_ == "files":
        return [f["file"]["url"] for f in prop["files"] if f["type"]=="file"]
    if type_ == "relation":
        return [r["id"] for r in prop["relation"]]
    if type_ == "rollup":
        roll_type = prop["rollup"]["type"]
        return prop["rollup"][roll_type]
    if type_ == "people":
        return [p["name"] for p in prop["people"]]
    if type_ == "formula":
        formula_type = prop["formula"]["type"]
        return prop["formula"][formula_type]
    if type_ == "created_time":
        return prop["created_time"]
    if type_ == "last_edited_time":
        return prop["last_edited_time"]
    return None


# --------------------------------------------------------
# Python → Notion（保存 共通コンバータ）
# --------------------------------------------------------
def to_notion_property(key, value, column_type="text"):
    """
    value から Notion 用のプロパティ構造に変換する
    column_type を指定すると select, number なども対応
    """

    if value is None:
        return None

    if column_type == "title":
        return {"title": [{"text": {"content": value}}]}

    if column_type == "rich_text":
        return {"rich_text": [{"text": {"content": value}}]}

    if column_type == "number":
        return {"number": value}

    if column_type == "select":
        return {"select": {"name": value}}

    if column_type == "multi_select":
        return {"multi_select": [{"name": v} for v in value]}

    if column_type == "checkbox":
        return {"checkbox": bool(value)}

    if column_type == "date":
        return {"date": {"start": value}}

    if column_type == "relation":
        # value は ID のリスト
        return {"relation": [{"id": v} for v in value]}

    # デフォルト: title と同じ扱い
    return {"rich_text": [{"text": {"content": str(value)}}]}


# --------------------------------------------------------
# 保存処理（新規作成）
# --------------------------------------------------------
def create_page(database_id: str, data: dict, column_types: dict):
    """
    data: { "column": value }
    column_types: { "column": "type" }
    """
    properties = {}

    for col, value in data.items():
        if col in column_types:
            properties[col] = to_notion_property(col, value, column_types[col])
        else:
            # タイプ未指定 → rich_text として保存
            properties[col] = to_notion_property(col, value, "rich_text")

    return notion.pages.create(
        parent={"database_id": database_id},
        properties=properties
    )


# --------------------------------------------------------
# 保存処理（更新）
# --------------------------------------------------------
def update_page(page_id: str, data: dict, column_types: dict):
    properties = {}

    for col, value in data.items():
        if col in column_types:
            properties[col] = to_notion_property(col, value, column_types[col])
        else:
            properties[col] = to_notion_property(col, value, "rich_text")

    return notion.pages.update(
        page_id=page_id,
        properties=properties
    )


# --------------------------------------------------------
# ページ削除（アーカイブ）
# --------------------------------------------------------
def delete_page(page_id: str):
    """
    Notionページをアーカイブ（削除）する
    
    Args:
        page_id: 削除するページのID
        
    Returns:
        削除されたページのレスポンス
    """
    return notion.pages.update(
        page_id=page_id,
        archived=True
    )


# --------------------------------------------------------
# DBから読み取り（全レコード）
# --------------------------------------------------------
def fetch_db_properties(database_id: str, column_names: list = None):
    results = notion.databases.query(database_id=database_id)["results"]
    data_list = []

    for page in results:
        props = page["properties"]

        item = {
            "page_id": page["id"]
        }

        if column_names is None:
            cols_to_fetch = list(props.keys())
        else:
            cols_to_fetch = column_names

        for col in cols_to_fetch:
            if col in props:
                item[col] = get_property_value(props[col])
            else:
                item[col] = None

        data_list.append(item)

    return data_list

# --------------------------------------------------------
# DBから読み取り（1レコード）
# --------------------------------------------------------
def fetch_page(database_id: str, page_id: str, column_names: list = None):
    page = notion.pages.retrieve(page_id=page_id)
    props = page["properties"]

    item = {
        "page_id": page_id
    }

    if column_names is None:
        cols_to_fetch = list(props.keys())
    else:
        cols_to_fetch = column_names

    for col in cols_to_fetch:
        if col in props:
            item[col] = get_property_value(props[col])
        else:
            item[col] = None

    return item

# --------------------------------------------------------
# name辞書作成
# --------------------------------------------------------
def build_id_name_map(items: list, name_column: str):
    return {
        item["page_id"]: item.get(name_column)
        for item in items
        if item.get("page_id")
    }

# --------------------------------------------------------
# relation の page_id リストを name のリストに変換
# --------------------------------------------------------
def resolve_relation(relation_ids: list, id_name_map: dict):
    if not relation_ids:
        return []

    return [
        id_name_map.get(rid)
        for rid in relation_ids
        if rid in id_name_map
    ]