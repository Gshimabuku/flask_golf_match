from flask import Flask, render_template, jsonify, redirect, url_for, Response, request
import os
from Services.course_service import get_courses,get_layouts
from Services.round_service import add_round
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

# --------------------------
# ラウンド
# --------------------------
@app.route('/round/new')
def round_new():
    courses = get_courses()
    layouts = get_layouts()
    users = get_users()
    return render_template('round/new.html', courses=courses, layouts=layouts, users=users)

@app.route("/round/create", methods=["POST"])
def round_create():
    data = {
        "play_date": request.form.get("play_date"),
        "course": request.form.get("course"),
        "layout_in": request.form.get("layout_in"),
        "layout_out": request.form.get("layout_out"),
        "member_count": request.form.get("member_count"),
    }

    member_count = request.form.get("member_count")
    member = []
    for i in range(1, member_count + 1):
        data[f"member{i}"] = request.form.get(f"member{i}")

    round_page_id = add_round(data)

    # 必要なら page_id を使った画面へ遷移も可能
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
