from flask import Flask
from flask_cors import CORS
from .config import Config

app = Flask(__name__)

# Allow credentials and specify the origin
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.config.from_object(Config)

from app import discord_oauth, routes
