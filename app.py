from flask import Flask, render_template, jsonify, redirect, url_for, Response, request
import os
from Services.course_service import get_courses,get_layouts,add_course,get_course_detail,delete_course,get_pars_by_layouts,get_hole_info
from Services.round_service import get_rounds,add_round,get_round_detail,delete_round,update_round
from Services.game_setting_service import add_game_setting, get_game_setting_by_round, delete_game_setting_by_round, update_game_setting
from Services.score_service import get_scores, add_score, get_hole_scores, get_all_scores_for_round_detail, delete_scores_by_round
from Services.user_service import get_users
from Const import olympic_type

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/health', methods=['GET'])
def health():
    return Response("OK", status=200)

# --------------------------
# コース
# --------------------------
@app.route('/course/list')
def course_list():
    data = get_courses()
    return render_template('course/list.html', courses=data)

@app.route('/course/new')
def course_new():
    return render_template('course/new.html')

@app.route('/course/<course_id>')
def course_detail(course_id):
    course, layouts = get_course_detail(course_id)
    return render_template('course/detail.html', course=course, layouts=layouts)

@app.route('/course/create', methods=['POST'])
def course_create():
    name = request.form.get('name')
    course_type = request.form.get('course_type')
    par = request.form.get('par')
    address = request.form.get('address')
    
    course_data = {
        'name': name,
        'course_type': course_type,
        'par': int(par) if par else None,
        'address': address
    }
    
    # レイアウト情報の取得
    layout_names = request.form.getlist('layout_name[]')
    layouts_data = []
    
    for i, layout_name in enumerate(layout_names):
        layout_pars = []
        for hole in range(1, 10):
            par_key = f'par_{hole}[]'
            pars = request.form.getlist(par_key)
            if i < len(pars):
                layout_pars.append(int(pars[i]))
        
        layouts_data.append({
            'layout_name': layout_name,
            'pars': layout_pars
        })
    
    course_page_id = add_course(course_data, layouts_data)
    
    return redirect(url_for('course_list'))

@app.route('/course/<course_id>/delete', methods=['POST'])
def course_delete(course_id):
    success = delete_course(course_id)
    if success:
        return jsonify({'status': 'success', 'message': 'コースを削除しました'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'コースの削除に失敗しました'}), 500

# --------------------------
# ラウンド
# --------------------------
@app.route('/round/list')
def round_list():
    data = get_rounds()
    return render_template('round/list.html', rounds=data)
    
@app.route('/round/new')
def round_new():
    courses = get_courses()
    layouts = get_layouts()
    users = get_users()
    olympic_types = [(val, olympic_type.DISPLAY[val]) for val in olympic_type.ALL]
    return render_template('round/new.html', courses=courses, layouts=layouts, users=users, olympic_types=olympic_types)

@app.route("/round/create", methods=["POST"])
def round_create():
    play_date = request.form.get("play_date")
    course = request.form.get("course")
    layout_in = request.form.get("layout_in")
    layout_out = request.form.get("layout_out")
    member_count = int(request.form.get("member_count"))
    olympic_toggle = bool(request.form.get("olympic_toggle"))
    snake_toggle = bool(request.form.get("snake_toggle"))
    nearpin_toggle = bool(request.form.get("nearpin_toggle"))

    round_data = {
        "play_date": play_date,
        "course": course,
        "layout_in": layout_in,
        "layout_out": layout_out,
        "member_count": member_count,
    }

    member = []
    for i in range(1, member_count + 1):
        round_data[f"member{i}"] = request.form.get(f"member{i}")
    
    round_page_id = add_round(round_data)

    game_setting_data = {
        "play_date": play_date,
        "round_page_id": round_page_id,
        "olympic_toggle": olympic_toggle,
        "snake_toggle": snake_toggle,
        "nearpin_toggle": nearpin_toggle,
    }

    if olympic_toggle:
        game_setting_data["gold"] = request.form.get("gold")
        game_setting_data["silver"] = request.form.get("silver")
        game_setting_data["bronze"] = request.form.get("bronze")
        game_setting_data["iron"] = request.form.get("iron")
        game_setting_data["diamond"] = request.form.get("diamond")
        game_setting_data["olympic_member"] = request.form.getlist("olympic_member[]")
    
    if snake_toggle:
        game_setting_data["snake"] = request.form.get("snake")
        game_setting_data["snake_rate"] = request.form.get("snake_rate")
        game_setting_data["snake_member"] = request.form.getlist("snake_member[]")

    if nearpin_toggle:
        game_setting_data["nearpin_rate"] = request.form.get("nearpin_rate")
        game_setting_data["nearpin_member"] = request.form.getlist("nearpin_member[]")

    game_setting_page_id = add_game_setting(game_setting_data)

    # 作成したラウンドのhole1のスコア入力画面へ遷移
    return redirect(url_for('round_hole', round_id=round_page_id, hole_number=1))

# --------------------------
# ラウンド設定編集画面
# --------------------------
@app.route('/round/<round_id>/edit')
def round_edit(round_id):
    """ラウンド設定編集画面"""
    # ラウンド情報取得
    round_data = get_round_detail(round_id)
    if not round_data:
        return "Round not found", 404
    
    # ゲーム設定取得
    game_setting = get_game_setting_by_round(round_id)
    
    # ユーザー一覧取得
    users = get_users()
    
    # 戻り先のホール番号を取得（デフォルトは1）
    return_hole = request.args.get('hole', 1, type=int)
    
    return render_template('round/edit.html',
                         round=round_data,
                         game_setting=game_setting,
                         users=users,
                         return_hole=return_hole)

# --------------------------
# ラウンド設定更新
# --------------------------
@app.route('/round/<round_id>/update', methods=['POST'])
def round_update(round_id):
    """ラウンド設定更新処理"""
    try:
        # ラウンド情報取得
        round_data = get_round_detail(round_id)
        if not round_data:
            return "Round not found", 404
        
        # 戻り先のホール番号
        return_hole = request.form.get('return_hole', 1, type=int)
        
        # ラウンド基本情報の更新
        play_date = request.form.get("play_date")
        member_count = len(round_data.get('member_list', []))
        
        members = []
        for i in range(1, member_count + 1):
            member_id = request.form.get(f"member{i}")
            if member_id:
                members.append(member_id)
        
        round_update_data = {
            "play_date": play_date,
            "members": members
        }
        
        update_round(round_id, round_update_data)
        
        # ゲーム設定の更新
        game_setting = get_game_setting_by_round(round_id)
        if game_setting:
            olympic_toggle = bool(request.form.get("olympic_toggle"))
            snake_toggle = bool(request.form.get("snake_toggle"))
            nearpin_toggle = bool(request.form.get("nearpin_toggle"))
            
            game_setting_data = {}
            
            if olympic_toggle:
                game_setting_data["gold"] = request.form.get("gold")
                game_setting_data["silver"] = request.form.get("silver")
                game_setting_data["bronze"] = request.form.get("bronze")
                game_setting_data["iron"] = request.form.get("iron")
                game_setting_data["diamond"] = request.form.get("diamond")
                game_setting_data["olympic_member"] = request.form.getlist("olympic_member[]")
            
            if snake_toggle:
                game_setting_data["snake"] = request.form.get("snake")
                game_setting_data["snake_rate"] = request.form.get("snake_rate")
                game_setting_data["snake_member"] = request.form.getlist("snake_member[]")
            
            if nearpin_toggle:
                game_setting_data["nearpin"] = True
                game_setting_data["nearpin_rate"] = request.form.get("nearpin_rate")
                game_setting_data["nearpin_member"] = request.form.getlist("nearpin_member[]")
            
            update_game_setting(game_setting.page_id, game_setting_data)
        
        # 更新後、元のホールのスコア入力画面へ戻る
        return redirect(url_for('round_hole', round_id=round_id, hole_number=return_hole))
        
    except Exception as e:
        print(f"round_update error: {e}")
        return f"更新中にエラーが発生しました: {str(e)}", 500

# --------------------------
# ラウンド詳細画面
# --------------------------
@app.route('/round/<round_id>/detail')
def round_detail(round_id):
    # ラウンド情報取得
    round_data = get_round_detail(round_id)
    if not round_data:
        return "Round not found", 404
    
    # ゲーム設定取得
    game_setting = get_game_setting_by_round(round_id)
    
    # 全ホールのスコアを取得（メンバー順序を保持）
    all_scores = get_all_scores_for_round_detail(round_id, round_data.get('member_list', []))
    
    # Par情報を取得
    layout_out_ids = round_data.get("layout_out", [])
    layout_in_ids = round_data.get("layout_in", [])
    pars_out, pars_in, par_out_total, par_in_total = get_pars_by_layouts(layout_out_ids, layout_in_ids)
    
    return render_template('round/detail.html',
                         round=round_data,
                         game_setting=game_setting,
                         scores=all_scores,
                         pars_out=pars_out,
                         pars_in=pars_in,
                         par_out_total=par_out_total,
                         par_in_total=par_in_total)

# --------------------------
# ラウンド削除
# --------------------------
@app.route('/round/<round_id>/delete', methods=['POST'])
def round_delete(round_id):
    """ラウンドと関連データ（スコア、ゲーム設定）を削除"""
    try:
        # 1. スコアを削除
        delete_scores_by_round(round_id)
        
        # 2. ゲーム設定を削除
        delete_game_setting_by_round(round_id)
        
        # 3. ラウンドを削除
        success = delete_round(round_id)
        
        if success:
            return jsonify({'status': 'success', 'message': 'ラウンドを削除しました'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'ラウンドの削除に失敗しました'}), 500
    except Exception as e:
        print(f"round_delete error: {e}")
        return jsonify({'status': 'error', 'message': f'削除中にエラーが発生しました: {str(e)}'}), 500

# --------------------------
# スコア入力画面
# --------------------------
@app.route('/round/<round_id>/hole/<int:hole_number>')
def round_hole(round_id, hole_number):
    # ラウンド情報取得
    round_data = get_round_detail(round_id)
    if not round_data:
        return "Round not found", 404
    
    # ゲーム設定取得
    game_setting = get_game_setting_by_round(round_id)
    
    # ホール情報取得（PARを取得するため）
    hole_par = 4  # デフォルト値
    
    # layout_outまたはlayout_inからホール情報を取得
    # スコア入力画面: 1-9ホール → layout_out, 10-18ホール → layout_in
    # holesテーブル: 各レイアウトともhole_number 1-9
    if hole_number <= 9:
        layout_ids = round_data.get("layout_out", [])
        actual_hole_number = hole_number  # 1-9はそのまま
    else:
        layout_ids = round_data.get("layout_in", [])
        actual_hole_number = hole_number - 9  # 10-18 → 1-9に変換
    
    hole_info = get_hole_info(layout_ids, actual_hole_number)
    if hole_info:
        hole_par = hole_info['par']
    
    # 既存スコア取得
    existing_scores = get_hole_scores(round_id, hole_number)
    
    # オリンピック選択肢
    olympic_types = [(val, olympic_type.DISPLAY[val]) for val in olympic_type.ALL]
    
    return render_template('round/hole.html', 
                         round=round_data, 
                         hole_number=hole_number,
                         hole_par=hole_par,
                         members=round_data.get('member_list', []),
                         existing_scores=existing_scores,
                         olympic_types=olympic_types,
                         game_setting=game_setting)

@app.route('/round/<round_id>/hole/<int:hole_number>/save', methods=['POST'])
def round_hole_save(round_id, hole_number):
    # ラウンド情報取得
    round_data = get_round_detail(round_id)
    if not round_data:
        return "Round not found", 404
    
    # 各メンバーのスコアを保存
    members = request.form.getlist('member_id[]')
    
    # 保存前に既存スコアの有無をチェック（遷移先判定用）
    from Services.score_service import get_existing_score, update_score
    has_existing_before_save = any(
        get_existing_score(round_id, member_id, hole_number) 
        for member_id in members
    )
    
    for i, member_id in enumerate(members, start=1):
        stroke = request.form.get(f'stroke_{i}')
        putt = request.form.get(f'putt_{i}')
        olympic = request.form.get(f'olympic_{i}')
        snake = request.form.get(f'snake_{i}')
        snake_out = request.form.get(f'snake_out_{i}')
        nearpin = request.form.get(f'nearpin_{i}')
        
        if stroke:  # ストロークが入力されている場合のみ保存
            # 既存スコアをチェック
            existing_score_id = get_existing_score(round_id, member_id, hole_number)
            
            if existing_score_id:
                # 更新
                score_data = {
                    "stroke": int(stroke),
                    "putt": int(putt) if putt else 0,
                    "olympic": olympic if olympic else None,
                    "snake": int(snake) if snake else None,
                    "snake_out": bool(snake_out),
                    "nearpin": bool(nearpin)
                }
                update_score(existing_score_id, score_data)
            else:
                # 新規作成
                score_data = {
                    "round_id": round_id,
                    "user_id": member_id,
                    "hole_number": hole_number,
                    "stroke": int(stroke),
                    "putt": int(putt) if putt else 0,
                    "olympic": olympic if olympic else None,
                    "snake": int(snake) if snake else None,
                    "snake_out": bool(snake_out),
                    "nearpin": bool(nearpin)
                }
                add_score(score_data)
    
    # 全ホールのスコアが完了しているかチェック
    try:
        from Services.score_service import get_scores_by_round
        from Services.round_service import update_round_complete
        
        # 現在のラウンドの全スコアを取得
        all_scores = get_scores_by_round(round_id)
        
        # 入力済みのホール番号を抽出
        score_holes = {score.hole_number for score in all_scores if score.hole_number is not None}
        
        # 1-18のホールがすべて揃っているかチェック
        new_complete = (score_holes == set(range(1, 19)))
        
        # 現在のcomplete状態を取得
        current_complete = round_data.get('complete', False)
        
        # 変更があった時のみ更新
        if current_complete != new_complete:
            update_round_complete(round_id, new_complete)
    except Exception as e:
        print(f"Error checking round completion: {e}")
    
    # 保存後の遷移先を判定（保存前にチェックした結果を使用）
    if has_existing_before_save:
        # 更新モード：現在のホールに留まる
        return redirect(url_for('round_hole', round_id=round_id, hole_number=hole_number))
    else:
        # 新規作成モード：次のホールへ
        if hole_number < 18:
            return redirect(url_for('round_hole', round_id=round_id, hole_number=hole_number + 1))
        else:
            # 18ホール完了したらラウンド一覧へ
            return redirect(url_for('round_list'))

if __name__ == '__main__':
    app.run(debug=True)
