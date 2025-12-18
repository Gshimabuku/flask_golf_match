from flask import Flask, render_template, jsonify, redirect, url_for, Response, request
import os
from Services.course_service import get_courses,get_layouts,add_course
from Services.round_service import get_rounds,add_round,add_game_setting
from Services.user_service import get_users

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
    return render_template('round/new.html', courses=courses, layouts=layouts, users=users)

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
        game_setting_data["snake_member"] = request.form.getlist("snake_member[]")

    if nearpin_toggle:
        game_setting_data["nearpin_member"] = request.form.getlist("nearpin_member[]")

    game_setting_page_id = add_game_setting(game_setting_data)

    # 必要なら page_id を使った画面へ遷移も可能
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
