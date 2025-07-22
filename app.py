from flask import Flask, render_template, request
import json
import os
import psycopg2

app = Flask(__name__)

QUESTIONS_FILE = 'questions.json'

# Load questions
with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# اتصال به دیتابیس PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)


@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        answers = request.form.to_dict()

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO answers (response) VALUES (%s);",
                (json.dumps(answers, ensure_ascii=False),)
            )
            conn.commit()

        return "پاسخ شما با موفقیت ثبت شد!"

    return render_template('survey.html', questions=questions)


@app.route('/results')
def show_results():
    with conn.cursor() as cur:
        cur.execute("SELECT response FROM answers ORDER BY submitted_at DESC;")
        rows = cur.fetchall()

    responses = [json.loads(row[0]) for row in rows]

    return {"responses": responses}


if __name__ == '__main__':
    app.run(debug=True)
