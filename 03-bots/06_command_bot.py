"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

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

HELP_TEXT = (
    "Here is what I can do:\n"
    "- hello: I greet you back.\n"
    "- whoami: I look you up in Webex and tell you who you are.\n"
    "- help: I show this list."
)


def handle_message(message, activity):
    """
    Reads the command the user typed and routes it to the right action.
    """
    room_id = message.roomId
    text = (getattr(message, "text", "") or "").strip().lower()
    # In group spaces the text starts with the bot mention, so only check the last word.
    command = text.split()[-1] if text else ""

    if command == "hello":
        # A simple reply that doesn't need any extra API call.
        send_message(api, room_id, "Hello! Type 'help' to see what I can do.")

    elif command == "whoami":
        # Use the Webex API from inside the bot to look up the sender.
        person = api.people.get(message.personId)
        send_message(api, room_id, f"You are {person.displayName} ({person.emails[0]}).")

    elif command == "help":
        send_message(api, room_id, HELP_TEXT)

    else:
        # Any other text falls back to a hint instead of staying silent.
        send_message(api, room_id, f"Sorry, I don't know '{command}'. Type 'help' to see what I can do.")


# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot with the provided token.
                      on_message=handle_message)      # Map the incoming messages to the command router.

# Start the bot and make it listen for incoming messages.
bot.run()
