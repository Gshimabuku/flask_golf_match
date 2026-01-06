from datetime import datetime
from Services.notion_service import fetch_db_properties, create_page, build_id_name_map, resolve_relation
from config import NOTION_DB_GAME_SETTINGS_ID, NOTION_DB_ROUNDS_ID, NOTION_DB_USERS_ID
from Models.game_setting import GameSetting

# ---------------------------------
# ゲーム設定一覧取得
# ---------------------------------
def get_game_settings(round_id=None):
    results = []

    try:
        settings = fetch_db_properties(NOTION_DB_GAME_SETTINGS_ID)
        
        # フィルタリング
        if round_id:
            settings = [s for s in settings if round_id in s.get("round", [])]
        
        # リレーション解決
        rounds = fetch_db_properties(NOTION_DB_ROUNDS_ID, ["name"])
        round_map = build_id_name_map(rounds, "name")
        
        users = fetch_db_properties(NOTION_DB_USERS_ID, ["name"])
        user_map = build_id_name_map(users, "name")
        
        for s in settings:
            setting = GameSetting.from_notion(s)
            results.append({
                "page_id": setting.page_id,
                "name": setting.name,
                "round": resolve_relation(setting.round or [], round_map),
                "gold": setting.gold,
                "silver": setting.silver,
                "bronze": setting.bronze,
                "iron": setting.iron,
                "diamond": setting.diamond,
                "snake": setting.snake,
                "snake_rate": setting.snake_rate,
                "nearpin": setting.nearpin,
                "nearpin_rate": setting.nearpin_rate,
                "olympic_member": resolve_relation(setting.olympic_member or [], user_map),
                "snake_member": resolve_relation(setting.snake_member or [], user_map),
                "nearpin_member": resolve_relation(setting.nearpin_member or [], user_map)
            })

    except Exception as e:
        print("get_game_settings error:", e)

    return results

# ---------------------------------
# ゲーム設定取得（ラウンド指定）
# ---------------------------------
def get_game_setting_by_round(round_id: str):
    """指定されたラウンドのゲーム設定を取得（モデル形式で返す）"""
    try:
        settings = fetch_db_properties(NOTION_DB_GAME_SETTINGS_ID)
        # round_idに一致する設定を取得
        setting_data = next((s for s in settings if round_id in s.get("round", [])), None)
        
        if not setting_data:
            # ゲーム設定が存在しない場合はNoneを返す
            return None
        
        # GameSettingモデルに変換して返す
        return GameSetting.from_notion(setting_data)
    except Exception as e:
        print("get_game_setting_by_round error:", e)
        return None

# ---------------------------------
# ゲーム設定登録
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
        notion_data["snake_rate"] = int(data.get("snake_rate", 1))  # デフォルト1
        notion_data["snake_member"] = data["snake_member"]

    if nearpin_toggle:
        notion_data["nearpin"] = bool(1)
        notion_data["nearpin_rate"] = int(data.get("nearpin_rate", 5))  # デフォルト5
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
        column_types["snake_rate"] = "number"
        column_types["snake_member"] = "relation"

    if nearpin_toggle:
        column_types["nearpin"] = "checkbox"
        column_types["nearpin_rate"] = "number"
        column_types["nearpin_member"] = "relation"

    # Notion 保存
    page = create_page(NOTION_DB_GAME_SETTINGS_ID, notion_data, column_types)

    # 作成された page_id を返す
    return page["id"]

# ---------------------------------
# ラウンドに紐づくゲーム設定を削除
# ---------------------------------
def delete_game_setting_by_round(round_id: str) -> bool:
    """
    指定されたラウンドに紐づくゲーム設定を削除
    
    Args:
        round_id: ラウンドのpage_id
        
    Returns:
        成功: True, 失敗: False
    """
    try:
        from Services.notion_service import delete_page
        
        # ラウンドに紐づくゲーム設定を取得
        settings = fetch_db_properties(NOTION_DB_GAME_SETTINGS_ID)
        round_settings = [s for s in settings if round_id in s.get("round", [])]
        
        # 各ゲーム設定を削除
        for setting in round_settings:
            delete_page(setting["page_id"])
        
        print(f"Deleted {len(round_settings)} game settings for round {round_id}")
        return True
        
    except Exception as e:
        print(f"delete_game_setting_by_round error: {e}")
        return False
