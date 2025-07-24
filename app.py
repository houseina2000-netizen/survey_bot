from flask import Flask, render_template, request, Response
import json
import os
from datetime import datetime
import uuid
import csv
from io import StringIO
import sqlite3

app = Flask(__name__)

QUESTIONS_FILE = 'questions.json'

# Load questions once
with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)


# ----------- 📌 دیتابیس -------------
DB_FILE = 'responses.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id TEXT,
            first_name TEXT,
            last_name TEXT,
            job TEXT,
            education TEXT,
            age TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


def save_to_db(answers):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO responses VALUES (?, ?, ?, ?, ?, ?, ?)', (
        answers['id'],
        answers.get('first_name', ''),
        answers.get('last_name', ''),
        answers.get('job', ''),
        answers.get('education', ''),
        answers.get('age', ''),
        answers['timestamp']
    ))
    conn.commit()
    conn.close()

def load_responses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM responses')
    rows = c.fetchall()
    conn.close()
    # تبدیل به dict
    keys = ['id', 'first_name', 'last_name', 'job', 'education', 'age', 'timestamp']
    responses = [dict(zip(keys, row)) for row in rows]
    return responses

# ---------- 📌 روتر اصلی ----------

@app.route('/', methods=['GET', 'POST', 'HEAD'])
def survey():
    if request.method == 'POST':
        answers = request.form.to_dict()

        answers['id'] = str(uuid.uuid4())
        answers['timestamp'] = datetime.now().isoformat()

        save_to_db(answers)

        print("پاسخ شما ذخیره شد!")

        return "پاسخ شما با موفقیت ثبت شد!"

    return render_template('survey.html', questions=questions)

@app.route('/results')
def show_results():
    responses = load_responses()
    return render_template('results.html', responses=responses)

@app.route('/download')
def download_csv():
    responses = load_responses()
    if not responses:
        return "هیچ پاسخی برای دانلود موجود نیست."

    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=responses[0].keys())
    writer.writeheader()
    writer.writerows(responses)

    output = si.getvalue().encode('utf-8-sig')

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=responses.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)
