import requests
from flask import session, jsonify, request, redirect, url_for
from app import app
import json

DISCORD_API_BASE_URL = 'https://discord.com/api/v10'

@app.route('/api/servers', methods=['GET'])
def get_user_servers():
    """Fetch the servers the user has access to and check if the bot is in each server."""
    if 'discord_token' not in session:
        return redirect(url_for('login'))

    headers = {
        'Authorization': f"Bearer {session['discord_token']}"
    }
    user_guilds = requests.get(f"{DISCORD_API_BASE_URL}/users/@me/guilds", headers=headers).json()

    owned_guilds = []
    for guild in user_guilds:
        if isinstance(guild, dict) and guild.get('owner', False):
            guild['bot_in_server'] = is_bot_in_guild(guild['id'])
            owned_guilds.append(guild)

    return jsonify({"owned_guilds": owned_guilds})


@app.route('/api/servers/<guild_id>', methods=['GET'])
def get_server_info(guild_id):
    """Fetches detailed information about a specific server."""
    if 'discord_token' not in session:
        return redirect(url_for('login'))

    headers = {
        'Authorization': f"Bearer {session['discord_token']}"
    }
    
    # Check if bot is in the server
    bot_in_server = is_bot_in_guild(guild_id)
    
    # Fetch server info
    guild_info = requests.get(f"{DISCORD_API_BASE_URL}/guilds/{guild_id}", headers=headers).json()
    guild_info['bot_in_server'] = bot_in_server

    return jsonify(guild_info)


def get_bot_user_id():
    """Fetch the bot's user ID."""
    bot_token = app.config['DISCORD_BOT_TOKEN']
    headers = {
        'Authorization': f"Bot {bot_token}"
    }
    response = requests.get(f"{DISCORD_API_BASE_URL}/users/@me", headers=headers)
    response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
    return response.json()['id']

def is_bot_in_guild(guild_id):
    """Checks if bot is in a specific server."""
    bot_token = app.config['DISCORD_BOT_TOKEN']
    bot_user_id = get_bot_user_id()  # Get the bot's user ID
    
    headers = {
        'Authorization': f"Bot {bot_token}"
    }
    
    response = requests.get(f"{DISCORD_API_BASE_URL}/guilds/{guild_id}/members/{bot_user_id}", headers=headers)

    return response.status_code == 200

@app.route('/api/add-bot', methods=['POST'])
def add_bot_to_server():
    """Adds the bot to the specified server by ID."""
    if 'discord_token' not in session:
        return redirect(url_for('login'))

    data = request.json
    guild_id = data.get('guild_id')

    if not guild_id:
        return jsonify({"error": "Guild ID is required"}), 400

    client_id = app.config['DISCORD_CLIENT_ID']
    permissions = 8  # Administrator permissions

    invite_url = (
        f"https://discord.com/oauth2/authorize?client_id={client_id}"
        f"&scope=bot&permissions={permissions}&guild_id={guild_id}&response_type=code&redirect_uri={app.config['DISCORD_REDIRECT_URI']}"
    )

    return jsonify({"invite_url": invite_url})

@app.route('/api/remove-bot', methods=['POST'])
def remove_bot_from_server():
    """Bot leaves the specified server by ID."""
    if 'discord_token' not in session:
        return redirect(url_for('login'))

    data = request.json
    guild_id = data.get('guild_id')

    if not guild_id:
        return jsonify({"error": "Guild ID is required"}), 400

    bot_token = app.config['DISCORD_BOT_TOKEN']
    
    headers = {
        'Authorization': f"Bot {bot_token}"
    }

    response = requests.delete(f"{DISCORD_API_BASE_URL}/users/@me/guilds/{guild_id}", headers=headers)
    
    if response.status_code == 204:
        return jsonify({"message": "Bot has left the server successfully"})
    else:
        print(f"Failed to leave guild {guild_id}: {response.status_code}")
        print(f"Response content: {response.content}")
        return jsonify({"error": "Failed to leave the server", "details": response.json()}), response.status_code

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Returns a list of available server templates."""
    # Assuming templates are stored in a JSON file or database
    with open("app/Templates.json", "r") as f:
        templates = json.load(f)
    return jsonify(templates)

@app.route('/api/apply-template', methods=['POST'])
def apply_template():
    """Applies the selected template to the specified server."""
    if 'discord_token' not in session:
        return redirect(url_for('login'))

    data = request.json
    guild_id = data.get('guild_id')
    template_key = data.get('template_key')

    if not guild_id or not template_key:
        return jsonify({"error": "Guild ID and Template Key are required"}), 400

    # Retrieve the template and apply it
    with open("templates.json", "r") as f:
        templates = json.load(f)

    template = templates.get(template_key)
    if not template:
        return jsonify({"error": "Template not found"}), 404

    # Apply the template to the guild
    apply_template_to_guild(guild_id, template)

    return jsonify({"message": "Template applied successfully"})

def apply_template_to_guild(guild_id, template):
    """Applies a template to the specified guild."""
    bot_token = app.config['DISCORD_BOT_TOKEN']
    headers = {'Authorization': f"Bot {bot_token}"}

    # Create roles, channels, and categories based on the template
    # (same logic as discussed previously)
    # ...