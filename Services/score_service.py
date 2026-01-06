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
        
        for s in scores:
            score = Score.from_notion(s)
            results.append({
                "page_id": score.page_id,
                "name": score.name,
                "round": resolve_relation(score.round or [], round_map),
                "user": resolve_relation(score.user or [], user_map),
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
def get_all_scores_for_round_detail(round_id: str, member_list: list):
    """
    ラウンド詳細画面用に全ホールのスコアを取得
    
    Args:
        round_id: ラウンドID
        member_list: メンバーリスト（順序保持用）[{page_id, display_name}, ...]
    
    Returns:
        list: [(player_name, {hole_number: {'stroke': int, 'putt': int}}), ...] 順序保持
    """
    all_scores = []
    
    try:
        # 全スコアを取得
        scores_data = fetch_db_properties(
            NOTION_DB_SCORES_ID, 
            ["round", "user", "hole_number", "stroke", "putt"]
        )
        
        # ラウンドIDでフィルタリング
        round_scores = [s for s in scores_data if round_id in s.get("round", [])]
        
        # メンバーリストの順序でスコアを整理
        for member in member_list:
            member_id = member.get('page_id')
            player_name = member.get('display_name') or member.get('name', 'Unknown')
            player_scores = {}
            
            # このメンバーのスコアを取得
            for score_data in round_scores:
                user_ids = score_data.get("user", [])
                if member_id in user_ids:
                    hole_number = score_data.get("hole_number")
                    stroke = score_data.get("stroke", 0)
                    putt = score_data.get("putt", 0)
                    
                    if hole_number:
                        player_scores[hole_number] = {
                            'stroke': stroke,
                            'putt': putt
                        }
            
            all_scores.append((player_name, player_scores))
    
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
        scores = fetch_db_properties(NOTION_DB_SCORES_ID, ["name", "round", "user", "hole_number", "stroke", "putt", "olympic", "snake", "snake_out", "nearpin"])
        
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
# ---------------------------------
# オリンピック結果集計
# ---------------------------------
def get_olympic_results(round_id: str, member_list: list, game_setting):
    """
    オリンピックゲームの結果をホールごとに集計
    
    Args:
        round_id: ラウンドID
        member_list: メンバーリスト [{page_id, display_name}, ...]
        game_setting: ゲーム設定オブジェクト
    
    Returns:
        list: [(player_name, {hole_number: points}), ...] メンバー順序保持
    """
    results = []
    
    try:
        # レート設定を取得
        rates = {
            'diamond': game_setting.diamond if game_setting and game_setting.diamond else 5,
            'gold': game_setting.gold if game_setting and game_setting.gold else 3,
            'silver': game_setting.silver if game_setting and game_setting.silver else 2,
            'bronze': game_setting.bronze if game_setting and game_setting.bronze else 1,
            'iron': game_setting.iron if game_setting and game_setting.iron else 0
        }
        
        # 参加メンバーのIDリスト
        olympic_members = game_setting.olympic_member if game_setting and game_setting.olympic_member else []
        
        # スコアデータを取得
        scores_data = fetch_db_properties(
            NOTION_DB_SCORES_ID,
            ["round", "user", "hole_number", "olympic"]
        )
        
        # ラウンドIDでフィルタリング
        round_scores = [s for s in scores_data if round_id in s.get("round", [])]
        
        # メンバーごとにホール別の獲得ポイントを集計
        for member in member_list:
            member_id = member.get('page_id')
            # オリンピック参加メンバーのみ集計
            if member_id not in olympic_members:
                continue
            
            player_name = member.get('display_name') or member.get('name', 'Unknown')
            hole_points = {}  # {hole_number: points}
            
            # このメンバーのスコアを取得
            for score_data in round_scores:
                user_ids = score_data.get("user", [])
                if not user_ids or user_ids[0] != member_id:
                    continue
                
                hole_number = score_data.get("hole_number")
                olympic_result = score_data.get("olympic")
                
                if hole_number:
                    if olympic_result:
                        result_lower = olympic_result.lower()
                        hole_points[hole_number] = rates.get(result_lower, 0)
                    else:
                        hole_points[hole_number] = 0
            
            results.append((player_name, hole_points))
        
    except Exception as e:
        print(f"get_olympic_results error: {e}")
    
    return results

# ---------------------------------
# ヘビ結果集計
# ---------------------------------
def get_snake_results(round_id: str, member_list: list, game_setting):
    """
    ヘビゲームの結果を集計
    
    Args:
        round_id: ラウンドID
        member_list: メンバーリスト [{page_id, display_name}, ...]
        game_setting: ゲーム設定オブジェクト
    
    Returns:
        dict: {
            'hole_snakes': [(player_name, {hole_number: snake_count}), ...],
            'hole_outs': {hole_number: player_name},  # 各ホールのヘビOUT者
            'three_hole_summary': [{
                'holes': 'X-X',
                'total_snakes': int,
                'out_player': 'name',
                'winner': 'name'
            }],
            'total_gained': [(player_name, total_count), ...]
        }
    """
    results = {
        'hole_snakes': [],
        'hole_outs': {},
        'three_hole_summary': [],
        'total_gained': []
    }
    
    try:
        # 参加メンバーのIDリスト
        snake_members = game_setting.snake_member if game_setting and game_setting.snake_member else []
        
        # スコアデータを取得
        scores_data = fetch_db_properties(
            NOTION_DB_SCORES_ID,
            ["round", "user", "hole_number", "snake", "snake_out"]
        )
        
        # ラウンドIDでフィルタリング
        round_scores = [s for s in scores_data if round_id in s.get("round", [])]
        
        # メンバーごとにホール別のヘビ数を集計
        member_hole_snakes = {}
        for member in member_list:
            member_id = member.get('page_id')
            # ヘビ参加メンバーのみ集計
            if member_id not in snake_members:
                continue
            
            player_name = member.get('display_name') or member.get('name', 'Unknown')
            hole_snakes = {}  # {hole_number: snake_count}
            
            # このメンバーのスコアを取得
            for score_data in round_scores:
                user_ids = score_data.get("user", [])
                if not user_ids or user_ids[0] != member_id:
                    continue
                
                hole_number = score_data.get("hole_number")
                snake_count = score_data.get("snake", 0)
                snake_out = score_data.get("snake_out", False)
                
                if hole_number:
                    hole_snakes[hole_number] = snake_count or 0
                    # ヘビOUTの記録
                    if snake_out:
                        results['hole_outs'][hole_number] = player_name
            
            results['hole_snakes'].append((player_name, hole_snakes))
            member_hole_snakes[player_name] = hole_snakes
        
        # 3ホール清算の集計（Separateモード）
        if game_setting.snake == 'Separate':
            hole_ranges = [(1, 3), (4, 6), (7, 9), (10, 12), (13, 15), (16, 18)]
            total_gained_dict = {name: 0 for name, _ in results['hole_snakes']}
            
            for start, end in hole_ranges:
                range_total = 0
                out_player = None
                player_range_snakes = {}  # {player_name: range内のヘビ合計}
                
                # 各プレイヤーのこの範囲の合計ヘビ数を計算
                for player_name, hole_snakes in results['hole_snakes']:
                    range_snakes = sum(hole_snakes.get(h, 0) for h in range(start, end + 1))
                    player_range_snakes[player_name] = range_snakes
                    range_total += range_snakes
                
                # この範囲のOUTプレイヤーを探す
                for h in range(start, end + 1):
                    if h in results['hole_outs']:
                        out_player = results['hole_outs'][h]
                        break
                
                # 獲得者を決定（最もヘビが少ない人）
                winner = None
                if player_range_snakes:
                    # OUTプレイヤーを除外
                    eligible_players = {p: s for p, s in player_range_snakes.items() if p != out_player}
                    if eligible_players:
                        # 最小ヘビ数のプレイヤーを獲得者とする
                        winner = min(eligible_players, key=eligible_players.get)
                        # 獲得者が全員のヘビを獲得
                        total_gained_dict[winner] += range_total
                
                results['three_hole_summary'].append({
                    'holes': f'{start}-{end}',
                    'total_snakes': range_total,
                    'out_player': out_player or '-',
                    'winner': winner or '-'
                })
            
            # 獲得合計をリストに変換
            for player_name, _ in results['hole_snakes']:
                results['total_gained'].append((player_name, int(total_gained_dict[player_name])))
        
        # 全ホール通しで清算（Allモード） - 現在はSeparateと同じロジック
        elif game_setting.snake == 'All':
            hole_ranges = [(1, 3), (4, 6), (7, 9), (10, 12), (13, 15), (16, 18)]
            total_gained_dict = {name: 0 for name, _ in results['hole_snakes']}
            
            for start, end in hole_ranges:
                range_total = 0
                out_player = None
                player_range_snakes = {}  # {player_name: range内のヘビ合計}
                
                # 各プレイヤーのこの範囲の合計ヘビ数を計算
                for player_name, hole_snakes in results['hole_snakes']:
                    range_snakes = sum(hole_snakes.get(h, 0) for h in range(start, end + 1))
                    player_range_snakes[player_name] = range_snakes
                    range_total += range_snakes
                
                # この範囲のOUTプレイヤーを探す
                for h in range(start, end + 1):
                    if h in results['hole_outs']:
                        out_player = results['hole_outs'][h]
                        break
                
                # 獲得者を決定（最もヘビが少ない人）
                winner = None
                if player_range_snakes:
                    # OUTプレイヤーを除外
                    eligible_players = {p: s for p, s in player_range_snakes.items() if p != out_player}
                    if eligible_players:
                        # 最小ヘビ数のプレイヤーを獲得者とする
                        winner = min(eligible_players, key=eligible_players.get)
                        # 獲得者が全員のヘビを獲得
                        total_gained_dict[winner] += range_total
                
                results['three_hole_summary'].append({
                    'holes': f'{start}-{end}',
                    'total_snakes': range_total,
                    'out_player': out_player or '-',
                    'winner': winner or '-'
                })
            
            # 獲得合計をリストに変換
            for player_name, _ in results['hole_snakes']:
                results['total_gained'].append((player_name, int(total_gained_dict[player_name])))
        
    except Exception as e:
        print(f"get_snake_results error: {e}")
    
    return results

# ---------------------------------
# ニアピン結果集計
# ---------------------------------
def get_nearpin_results(round_id: str, member_list: list, game_setting, pars_out: list, pars_in: list):
    """
    ニアピンゲームの結果を集計
    
    Args:
        round_id: ラウンドID
        member_list: メンバーリスト [{page_id, display_name}, ...]
        game_setting: ゲーム設定オブジェクト
        pars_out: OUTのPar情報リスト
        pars_in: INのPar情報リスト
    
    Returns:
        list: [{'hole_number': int, 'winner': str}, ...] Par 3のホール全て（1から順番に）
    """
    results = []
    
    try:
        # 参加メンバーのIDリスト
        nearpin_members = game_setting.nearpin_member if game_setting and game_setting.nearpin_member else []
        
        # スコアデータを取得してニアピン獲得者を検索
        scores_data = fetch_db_properties(
            NOTION_DB_SCORES_ID,
            ["round", "user", "hole_number", "nearpin"]
        )
        
        # ラウンドIDでフィルタリング
        round_scores = [s for s in scores_data if round_id in s.get("round", [])]
        
        # ニアピン獲得者をホールごとにマップ化
        nearpin_winners = {}  # {hole_number: winner_name}
        for score_data in round_scores:
            nearpin = score_data.get("nearpin", False)
            if not nearpin:
                continue
            
            user_ids = score_data.get("user", [])
            if not user_ids or user_ids[0] not in nearpin_members:
                continue
            
            hole_number = score_data.get("hole_number")
            
            # 獲得者の名前を取得
            for member in member_list:
                if member.get('page_id') == user_ids[0]:
                    winner_name = member.get('display_name') or member.get('name', 'Unknown')
                    nearpin_winners[hole_number] = winner_name
                    break
        
        # Par情報から全Par 3ホールを抽出（1から順番に）
        all_pars = pars_out + pars_in  # ホール1-18のPar情報
        for hole_number in range(1, 19):
            if hole_number <= len(all_pars) and all_pars[hole_number - 1] == 3:
                results.append({
                    'hole_number': hole_number,
                    'winner': nearpin_winners.get(hole_number, '-')
                })
        
    except Exception as e:
        print(f"get_nearpin_results error: {e}")
    
    return results