from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

QUESTIONS_FILE = 'questions.json'
RESPONSES_FILE = 'responses.json'

# Load questions once
with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)


@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        answers = request.form.to_dict()

        # بارگذاري پاسخ‌هاي قبلي
        if os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                responses = json.load(f)
        else:
            responses = []

        responses.append(answers)

        # ذخيره پاسخ جديد
        with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        return "پاسخ شما با موفقيت ثبت شد!"

    return render_template('survey.html', questions=questions)


@app.route('/results')
def show_results():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            responses = json.load(f)
    else:
        responses = []

    return render_template('results.html', responses=responses)


if __name__ == '__main__':
    app.run(debug=True)
import csv
from flask import send_file, Response
from io import StringIO

@app.route('/download')
def download_csv():
    if not os.path.exists(RESPONSES_FILE):
        return "هیچ پاسخی برای دانلود موجود نیست."

    with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
        responses = json.load(f)

    if not responses:
        return "فایلی برای دانلود وجود ندارد."

    # تبدیل JSON به CSV
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=responses[0].keys())
    writer.writeheader()
    writer.writerows(responses)

    output = si.getvalue().encode('utf-8-sig')  # برای نمایش درست فارسی در Excel

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=responses.csv'}
    )
