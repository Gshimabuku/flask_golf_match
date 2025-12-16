from flask import Flask, render_template, jsonify, redirect, url_for, Response
import os
from Services.course_service import get_courses,get_layouts

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


if __name__ == '__main__':
    app.run(debug=True)
