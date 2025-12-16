from flask import Flask, render_template, jsonify, redirect, url_for, Response, request
import os
from Services.course_service import get_courses,get_layouts
from Services.round_service import add_round

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
    return render_template('round/new.html', courses=courses, layouts=layouts)

@app.route("/round/create", methods=["POST"])
def round_create():
    
    data = {
        "play_date": request.form.get("play_date"),
        "course": request.form.get("course"),
        "layout_in": request.form.get("layout_in"),
        "layout_out": request.form.get("layout_out"),
        "rate": int(request.form.get("rate", 0)),
    }

    round_page_id = add_round(data)

    # 必要なら page_id を使った画面へ遷移も可能
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
