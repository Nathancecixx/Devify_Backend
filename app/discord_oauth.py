import requests
from flask import session, redirect, request, url_for, jsonify
from app import app

DISCORD_OAUTH_URL = 'https://discord.com/api/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/oauth2/token'
DISCORD_API_BASE_URL = 'https://discord.com/api/v8'
DISCORD_SCOPE = 'identify email'

@app.route('/login')
def login():
    discord_login_url = (
        f"{DISCORD_OAUTH_URL}?client_id={app.config['DISCORD_CLIENT_ID']}&redirect_uri={app.config['DISCORD_REDIRECT_URI']}&response_type=code&scope={DISCORD_SCOPE}"
    )
    return redirect(discord_login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'client_id': app.config['DISCORD_CLIENT_ID'],
        'client_secret': app.config['DISCORD_CLIENT_SECRET'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': app.config['DISCORD_REDIRECT_URI'],
        'scope': DISCORD_SCOPE
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    response_data = response.json()
    session['discord_token'] = response_data['access_token']
    return redirect('http://localhost:3000/server-list')
