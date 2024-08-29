import requests
from flask import session, redirect, request, url_for, jsonify
from app import app

DISCORD_OAUTH_URL = 'https://discord.com/api/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/oauth2/token'
DISCORD_API_BASE_URL = 'https://discord.com/api/v10'
DISCORD_SCOPE = 'identify email guilds'

@app.route('/login')
def login():
    session.clear()
    discord_login_url = (
        f"{DISCORD_OAUTH_URL}?client_id={app.config['DISCORD_CLIENT_ID']}&redirect_uri={app.config['DISCORD_REDIRECT_URI']}&response_type=code&scope={DISCORD_SCOPE}"
    )
    return redirect(discord_login_url)

@app.route('/callback')
def callback():
    code = request.args['code']
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

    if 'access_token' in response_data:
        session['discord_token'] = response_data['access_token']
        return redirect('http://localhost:3000/server-list')
    else: 
        redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()

    return redirect('http://localhost:3000')
