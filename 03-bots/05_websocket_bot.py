"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks
"""

import os
from dotenv import load_dotenv
# Import the shared WebSocketClient class
from websocket_client import WebSocketClient
# Import the Webex API SDK for direct API calls
from bot_helpers import get_api, send_message

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication with the Webex API.
bot_token = os.getenv("BOT_TOKEN")
api = get_api(bot_token)

def handle_message(message, activity):
    """
    Executes when a message is received by the bot.
    """
    room_id = message.roomId
    text = (getattr(message, "text", "") or "").strip()
    
    if text:
        # Echo back what they said
        send_message(api, room_id, f"Echo: {text}")

# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot with the provided token.
                      on_message=handle_message)      # Map the incoming messages to the echo handler.

# Start the bot and make it listen for incoming messages.
bot.run()
