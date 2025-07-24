from flask import Flask, render_template, request, Response
import json
import os
from datetime import datetime
import uuid
import csv
from io import StringIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

QUESTIONS_FILE = 'questions.json'
RESPONSES_FILE = 'responses.json'

# Load questions once
with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# ارسال ایمیل
def send_email(subject, body, to_email):
    sender_email = "YOUR_EMAIL@gmail.com"  # ← آدرس ایمیل خودت
    sender_password = "YOUR_APP_PASSWORD"  # ← رمز برنامه‌ای (App Password)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("ایمیل با موفقیت ارسال شد.")
    except Exception as e:
        print("خطا در ارسال ایمیل:", str(e))

@app.route('/', methods=['GET', 'POST', 'HEAD'])
def survey():
    if request.method == 'POST':
        answers = request.form.to_dict()
        answers['id'] = str(uuid.uuid4())
        answers['timestamp'] = datetime.now().isoformat()

        if os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                responses = json.load(f)
        else:
            responses = []

        responses.append(answers)

        with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        # ساخت متن ایمیل
        body = "📝 پاسخ جدید ثبت شد:\n\n"
        for key, value in answers.items():
            body += f"{key}: {value}\n"

        # ارسال ایمیل به شما
        send_email("🧾 پاسخ جدید نظرسنجی", body, "ho3einahj@gmail.com")

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

    output = si.getvalue().encode('utf-8-sig')

    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=responses.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)
