"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Create a custom handler with domain restriction.
"""

import os

from bot_helpers import delete_message, get_api, is_allowed_domain, send_card, send_message
from dotenv import load_dotenv
from websocket_client import WebSocketClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN", "")
ALLOWED_DOMAINS = [DOMAIN] if DOMAIN else []
COMMAND_KEYWORD = "message"
api = get_api(BOT_TOKEN)

HELLO_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "Send Hello!",
            "weight": "Bolder",
            "size": "Medium",
        },
        {
            "type": "TextBlock",
            "text": "Click the button below or send the keyword `message` to trigger the handler.",
            "wrap": True,
        },
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Send Hello!",
            "data": {"callback_keyword": "send_hello"},
        }
    ],
}


def send_hello(room_id: str, message_id: str | None = None) -> None:
    if message_id:
        delete_message(api, message_id)
    send_message(api, room_id, "Hello!")
    send_message(api, room_id, "Your Hello! message has been sent.")


def handle_message(message, activity) -> None:
    room_id = message.roomId
    person_email = getattr(message, "personEmail", "")
    text = (getattr(message, "text", "") or "").strip().lower()

    if ALLOWED_DOMAINS and not is_allowed_domain(person_email, ALLOWED_DOMAINS):
        send_message(api, room_id, "Sorry, this bot is restricted to your lab domain.")
        return

    if text == COMMAND_KEYWORD:
        send_hello(room_id)
        return

    send_card(api, room_id, HELLO_CARD, fallback_text="Send Hello!")


def handle_card_action(attachment_action, activity) -> None:
    room_id = attachment_action.roomId
    person_email = getattr(attachment_action, "personEmail", "")

    if ALLOWED_DOMAINS and not is_allowed_domain(person_email, ALLOWED_DOMAINS):
        send_message(api, room_id, "Sorry, this bot is restricted to your lab domain.")
        return

    send_hello(room_id, getattr(attachment_action, "messageId", None))


if __name__ == "__main__":
    bot = WebSocketClient(
        access_token=BOT_TOKEN,
        bot_name="WebexOne2026",
        on_message=handle_message,
        on_card_action=handle_card_action,
    )
    bot.run()
