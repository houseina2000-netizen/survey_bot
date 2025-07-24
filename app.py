from flask import Flask, render_template, request, Response
import json
import os
from datetime import datetime
import uuid
import csv
from io import StringIO
import smtplib
from email.mime.text import MIMEText
import requests

app = Flask(__name__)

QUESTIONS_FILE = 'questions.json'
RESPONSES_FILE = 'responses.json'

# Load questions once
with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)

@app.route('/', methods=['GET', 'POST', 'HEAD'])
def survey():
    if request.method == 'POST':
        answers = request.form.to_dict()

        # افزودن اطلاعات اضافی
        answers['id'] = str(uuid.uuid4())  # شناسه یکتا
        answers['timestamp'] = datetime.now().isoformat()  # زمان ثبت

        # بارگذاری پاسخ‌های قبلی
        if os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                responses = json.load(f)
        else:
            responses = []

        responses.append(answers)

        # ذخیره پاسخ جدید
        with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        # ارسال ایمیل (در صورت نیاز)
        send_email(answers)
        print("پاسخ شما ارسال شد!")
        

        return "پاسخ شما با موفقیت ثبت شد!"

    return render_template('survey.html', questions=questions)

@app.route('/results')
def show_results():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            responses = json.load(f)
    else:
        responses = []

    return render_template('results.html', responses=responses)

@app.route('/download')
def download_csv():
    if not os.path.exists(RESPONSES_FILE):
        return "هیچ پاسخی برای دانلود موجود نیست."

    with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
        responses = json.load(f)

    if not responses:
        return "فایلی برای دانلود وجود ندارد."

    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=responses[0].keys())
    writer.writeheader()
    writer.writerows(responses)

    output = si.getvalue().encode('utf-8-sig')  # برای درست نمایش دادن فارسی در Excel

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=responses.csv'}
    )

def send_email(answers):
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')

    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Survey Bot <mailgun@{MAILGUN_DOMAIN}>",
            "to": ["ho3einahj@gmail.com"],
            "subject": "پاسخ جدید به نظرسنجی",
            "text": f"""
📝 پاسخ جدید دریافت شد:

نام: {answers.get('first_name', '')}
نام خانوادگی: {answers.get('last_name', '')}
شغل: {answers.get('job', '')}
تحصیلات: {answers.get('education', '')}
سن: {answers.get('age', '')}
زمان ثبت: {answers.get('timestamp', '')}
شناسه: {answers.get('id', '')}
            """
        }
    )

    try:
        response = sg.send(message)
        print("ایمیل با موفقیت ارسال شد:", response.status_code)
    except Exception as e:
        print("خطا در ارسال ایمیل:", e)


if __name__ == '__main__':
    app.run(debug=True)
