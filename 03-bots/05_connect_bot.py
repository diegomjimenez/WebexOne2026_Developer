"""Exercise 3.5 - Connect the bot and respond to incoming messages."""

import os

from bot_helpers import get_api, send_card, send_message
from dotenv import load_dotenv
from websocket_client import WebSocketClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
api = get_api(BOT_TOKEN)

WELCOME_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "Welcome to your WebexOne 2026 bot",
            "weight": "Bolder",
            "size": "Medium",
        },
        {
            "type": "TextBlock",
            "text": "Send any message to receive this card and an echo reply.",
            "wrap": True,
        },
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Echo Words Back to You!",
            "data": {"callback_keyword": "echo_prompt"},
        }
    ],
}


def handle_message(message, activity) -> None:
    room_id = message.roomId
    person_email = getattr(message, "personEmail", None)
    text = getattr(message, "text", "") or ""
    print(f"Message from {person_email}: {text}")

    send_card(api, room_id, WELCOME_CARD, fallback_text="Welcome")
    if text.strip():
        send_message(api, room_id, f"You said: {text}")


def handle_card_action(attachment_action, activity) -> None:
    room_id = attachment_action.roomId
    send_message(api, room_id, "Thanks! Continue with the next exercise to build a custom handler.")


if __name__ == "__main__":
    bot = WebSocketClient(
        access_token=BOT_TOKEN,
        bot_name="WebexOne2026",
        on_message=handle_message,
        on_card_action=handle_card_action,
    )
    bot.run()
