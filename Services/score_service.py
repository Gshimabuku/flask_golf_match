from Services.notion_service import fetch_db_properties, create_page, build_id_name_map, resolve_relation, update_page
from config import NOTION_DB_SCORES_ID, NOTION_DB_ROUNDS_ID, NOTION_DB_USERS_ID, NOTION_DB_HOLES_ID
from Models.score import Score

# ---------------------------------
# スコア一覧取得
# ---------------------------------
def get_scores(round_id=None, user_id=None):
    results = []

    try:
        scores = fetch_db_properties(NOTION_DB_SCORES_ID)
        
        # フィルタリング
        if round_id:
            scores = [s for s in scores if round_id in s.get("round", [])]
        if user_id:
            scores = [s for s in scores if user_id in s.get("user", [])]
        
        # リレーション解決
        rounds = fetch_db_properties(NOTION_DB_ROUNDS_ID, ["name"])
        round_map = build_id_name_map(rounds, "name")
        
        users = fetch_db_properties(NOTION_DB_USERS_ID, ["name"])
        user_map = build_id_name_map(users, "name")
        
        holes = fetch_db_properties(NOTION_DB_HOLES_ID, ["name"])
        hole_map = build_id_name_map(holes, "name")
        
        for s in scores:
            score = Score.from_notion(s)
            results.append({
                "page_id": score.page_id,
                "name": score.name,
                "round": resolve_relation(score.round or [], round_map),
                "user": resolve_relation(score.user or [], user_map),
                "hole": resolve_relation(score.hole or [], hole_map),
                "hole_number": score.hole_number,
                "stroke": score.stroke,
                "putt": score.putt,
                "olympic": score.olympic,
                "snake": score.snake,
                "snake_out": score.snake_out,
                "nearpin": score.nearpin
            })

    except Exception as e:
        print("get_scores error:", e)

    return results

# ---------------------------------
# 特定ラウンドの全スコア取得（完了チェック用）
# ---------------------------------
def get_scores_by_round(round_id: str):
    """指定されたラウンドの全スコアを取得"""
    results = []

    try:
        scores = fetch_db_properties(NOTION_DB_SCORES_ID, ["round", "hole_number"])
        
        # フィルタリング
        round_scores = [s for s in scores if round_id in s.get("round", [])]
        
        # Scoreオブジェクトに変換
        for s in round_scores:
            score = Score.from_notion(s)
            results.append(score)

    except Exception as e:
        print("get_scores_by_round error:", e)

    return results

# ---------------------------------
# ラウンド詳細用のスコア取得
# ---------------------------------
def get_all_scores_for_round_detail(round_id: str):
    """
    ラウンド詳細画面用に全ホールのスコアを取得
    
    Returns:
        dict: {player_name: {hole_number: {'score': int}}}
    """
    all_scores = {}
    
    try:
        # ユーザー情報を取得
        users_data = fetch_db_properties(NOTION_DB_USERS_ID, ["name", "display_name"])
        user_map = {u["page_id"]: u.get("display_name") or u.get("name", "") for u in users_data}
        
        # 全スコアを取得
        scores_data = fetch_db_properties(
            NOTION_DB_SCORES_ID, 
            ["round", "user", "hole_number", "stroke", "putt"]
        )
        
        # ラウンドIDでフィルタリング
        round_scores = [s for s in scores_data if round_id in s.get("round", [])]
        
        # プレイヤーごと、ホールごとに整理
        for score_data in round_scores:
            user_ids = score_data.get("user", [])
            if not user_ids:
                continue
                
            user_id = user_ids[0]
            player_name = user_map.get(user_id, "Unknown")
            hole_number = score_data.get("hole_number")
            stroke = score_data.get("stroke", 0)
            putt = score_data.get("putt", 0)
            
            if player_name not in all_scores:
                all_scores[player_name] = {}
            
            if hole_number:
                all_scores[player_name][hole_number] = {
                    'score': stroke + putt
                }
    
    except Exception as e:
        print(f"get_all_scores_for_round_detail error: {e}")
    
    return all_scores

# ---------------------------------
# 特定ラウンド・ユーザー・ホールのスコア取得
# ---------------------------------
def get_existing_score(round_id: str, user_id: str, hole_number: int):
    """指定されたラウンド、ユーザー、ホールのスコアを取得"""
    try:
        scores = fetch_db_properties(NOTION_DB_SCORES_ID, ["round", "user", "hole_number"])
        
        # フィルタリング
        for s in scores:
            if (round_id in s.get("round", []) and 
                user_id in s.get("user", []) and 
                s.get("hole_number") == hole_number):
                return s.get("page_id")
        
        return None
    except Exception as e:
        print("get_existing_score error:", e)
        return None

# ---------------------------------
# 特定ラウンド・ホールのスコア取得
# ---------------------------------
def get_hole_scores(round_id: str, hole_number: int):
    """指定されたラウンドとホール番号のスコアを全メンバー分取得"""
    results = {}

    try:
        scores = fetch_db_properties(NOTION_DB_SCORES_ID, ["name", "round", "user", "hole", "hole_number", "stroke", "putt", "olympic", "snake", "snake_out", "nearpin"])
        
        # フィルタリング
        hole_scores = [s for s in scores if round_id in s.get("round", []) and s.get("hole_number") == hole_number]
        
        # user_idをキーにした辞書に変換
        for s in hole_scores:
            user_ids = s.get("user", [])
            if user_ids:
                user_id = user_ids[0]
                score = Score.from_notion(s)
                results[user_id] = {
                    "page_id": score.page_id,
                    "stroke": score.stroke,
                    "putt": score.putt,
                    "olympic": score.olympic,
                    "snake": score.snake,
                    "snake_out": score.snake_out,
                    "nearpin": score.nearpin
                }

    except Exception as e:
        print("get_hole_scores error:", e)

    return results

# ---------------------------------
# スコア登録
# ---------------------------------
def add_score(data: dict) -> str:
    round_id = data["round_id"]
    user_id = data["user_id"]
    hole_id = data["hole_id"]
    hole_number = data["hole_number"]
    stroke = data.get("stroke", 0)
    putt = data.get("putt", 0)
    olympic = data.get("olympic")
    snake = data.get("snake")
    snake_out = data.get("snake_out", False)
    nearpin = data.get("nearpin", False)
    
    # name生成（例: {round_name}-{user_name}-{hole_number}）
    rounds = fetch_db_properties(NOTION_DB_ROUNDS_ID, ["name"])
    round_name = next((r["name"] for r in rounds if r["page_id"] == round_id), "")
    
    users = fetch_db_properties(NOTION_DB_USERS_ID, ["name"])
    user_name = next((u["name"] for u in users if u["page_id"] == user_id), "")
    
    name = f"{round_name}-{user_name}-{hole_number}"
    
    notion_data = {
        "name": name,
        "round": [round_id],
        "user": [user_id],
        "hole": [hole_id],
        "hole_number": hole_number,
        "stroke": stroke,
        "putt": putt,
    }
    
    if olympic:
        notion_data["olympic"] = olympic
    if snake is not None:
        notion_data["snake"] = snake
    if snake_out:
        notion_data["snake_out"] = snake_out
    if nearpin:
        notion_data["nearpin"] = nearpin
    
    column_types = {
        "name": "title",
        "round": "relation",
        "user": "relation",
        "hole": "relation",
        "hole_number": "number",
        "stroke": "number",
        "putt": "number",
        "olympic": "select",
        "snake": "number",
        "snake_out": "checkbox",
        "nearpin": "checkbox"
    }
    
    page = create_page(NOTION_DB_SCORES_ID, notion_data, column_types)
    
    return page["id"]

# ---------------------------------
# スコア更新
# ---------------------------------
def update_score(score_page_id: str, data: dict):
    """既存のスコアを更新"""
    stroke = data.get("stroke", 0)
    putt = data.get("putt", 0)
    olympic = data.get("olympic")
    snake = data.get("snake")
    snake_out = data.get("snake_out", False)
    nearpin = data.get("nearpin", False)
    
    notion_data = {
        "stroke": stroke,
        "putt": putt,
    }
    
    if olympic:
        notion_data["olympic"] = olympic
    if snake is not None:
        notion_data["snake"] = snake
    if snake_out:
        notion_data["snake_out"] = snake_out
    if nearpin:
        notion_data["nearpin"] = nearpin
    
    column_types = {
        "stroke": "number",
        "putt": "number",
        "olympic": "select",
        "snake": "number",
        "snake_out": "checkbox",
        "nearpin": "checkbox"
    }
    
    update_page(score_page_id, notion_data, column_types)
    print(f"Score {score_page_id} updated")

# ---------------------------------
# ラウンドに紐づくスコアをすべて削除
# ---------------------------------
def delete_scores_by_round(round_id: str) -> bool:
    """
    指定されたラウンドに紐づくスコアをすべて削除
    
    Args:
        round_id: ラウンドのpage_id
        
    Returns:
        成功: True, 失敗: False
    """
    try:
        from Services.notion_service import delete_page
        
        # ラウンドに紐づくスコアを取得
        scores_data = fetch_db_properties(NOTION_DB_SCORES_ID, ["round"])
        round_scores = [s for s in scores_data if round_id in s.get("round", [])]
        
        # 各スコアを削除
        for score in round_scores:
            delete_page(score["page_id"])
        
        print(f"Deleted {len(round_scores)} scores for round {round_id}")
        return True
        
    except Exception as e:
        print(f"delete_scores_by_round error: {e}")
        return False
