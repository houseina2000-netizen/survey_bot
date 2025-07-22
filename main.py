from flask import Flask, request, render_template, redirect
from supabase import create_client, Client
import os

# ⬇ متغیرهای محیطی برای امنیت بیشتر
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

app = Flask(__name__)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    response = supabase.table('votes').select('*').execute()
    votes = response.data
    yes_count = sum(1 for vote in votes if vote['choice'] == 'yes')
    no_count = sum(1 for vote in votes if vote['choice'] == 'no')
    return render_template('index.html', votes={'yes': yes_count, 'no': no_count})

@app.route('/vote', methods=['POST'])
def vote():
    choice = request.form.get('vote')
    if choice in ['yes', 'no']:
        supabase.table('votes').insert({'choice': choice}).execute()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
