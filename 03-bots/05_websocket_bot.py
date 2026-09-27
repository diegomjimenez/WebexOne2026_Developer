"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Adam Weeks
- Diego Manuel Jimenez Moreno
- Phil Bellanti

Connect the bot and respond to incoming messages with an echo or an Adaptive Card.
"""

import os
from dotenv import load_dotenv

from bot_helpers import get_api, send_message, send_card
from websocket_client import WebSocketClient

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication with the Webex API.
bot_token = os.getenv("BOT_TOKEN")

# Initialize the WebexAPI client for REST calls
api = get_api(bot_token)


def create_echo_card():
    """
    Returns a dictionary representing an Adaptive Card with a text input.
    """
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "text": "Echo Card",
                "weight": "Bolder",
                "size": "Medium"
            },
            {
                "type": "TextBlock",
                "text": "Type something below and I will echo it back to you.",
                "wrap": True
            },
            {
                "type": "Input.Text",
                "id": "user_input",
                "placeholder": "What's on your mind?",
                "isMultiline": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Send Echo",
                "data": {"action": "echo_submit"}
            }
        ]
    }


def handle_message(message, activity) -> None:
    """
    Executes when a message is received by the bot.
    """
    room_id = message.roomId
    person_email = getattr(message, "personEmail", None)
    text = (getattr(message, "text", "") or "").strip()
    
    print(f"Message from {person_email}: {text}")

    if not text:
        return

    # If the user typed 'card', send the Adaptive Card
    if text.lower() == "card":
        print("Sending Adaptive Card...")
        send_card(api, room_id, create_echo_card(), fallback_text="Echo Card")
    else:
        # Otherwise, simply echo back what they said
        print("Sending echo response...")
        send_message(api, room_id, f"Echo: {text}")


def handle_card_action(attachment_action, activity) -> None:
    """
    Executes when an Adaptive Card is submitted.
    """
    room_id = attachment_action.roomId
    person_email = getattr(attachment_action, "personEmail", None)
    inputs = getattr(attachment_action, "inputs", {}) or {}
    
    print(f"Card submitted by {person_email}")

    # Extract the user input from the card
    user_input = inputs.get("user_input", "").strip()

    if user_input:
        send_message(api, room_id, f"You submitted via card: {user_input}")
    else:
        send_message(api, room_id, "You submitted an empty card!")


if __name__ == "__main__":
    print("Starting WebSocket Bot... (Send 'card' to get an Adaptive Card)")
    bot = WebSocketClient(
        access_token=bot_token,
        bot_name="WebexOne2026",
        on_message=handle_message,
        on_card_action=handle_card_action,
    )
    bot.run()

