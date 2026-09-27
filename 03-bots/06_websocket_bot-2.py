"""
Webex One 2026 - Exploring the possibilities of Webex APIs

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks
"""

import os
from dotenv import load_dotenv
from websocket_client import WebSocketClient
from bot_helpers import get_api, send_message

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication.
bot_token = os.getenv("BOT_TOKEN")
api = get_api(bot_token)

def handle_message(message, activity):
    """
    Executes the 'message' command. Sends a "Hello!" message back to the user.
    """
    room_id = message.roomId
    text = (getattr(message, "text", "") or "").strip().lower()
    
    # Check if the user typed '/message' or 'message' to invoke this command.
    if text == "message":
        # Create a direct message to the person in the room.
        send_message(api, room_id, "Hello!")
        send_message(api, room_id, "Message sent")

# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot with the provided token.      # Assign a name to the bot.
                      on_message=handle_message)      # Map the incoming messages to the handler.

# Start the bot and make it listen for incoming messages.
# This call is typically blocking and keeps the bot running, waiting for commands.
bot.run()
