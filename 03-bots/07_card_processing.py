"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Process Adaptive Card submissions.
"""

import os

from bot_helpers import delete_message, extract_input_values, get_api, is_allowed_domain, send_card, send_message
from dotenv import load_dotenv
from websocket_client import WebSocketClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN", "")
ALLOWED_DOMAINS = [DOMAIN] if DOMAIN else []
COMMAND_KEYWORD = "message"
api = get_api(BOT_TOKEN)

MESSAGE_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "Send a message",
            "weight": "Bolder",
            "size": "Medium",
        },
        {
            "type": "TextBlock",
            "text": "Enter a message below and click Submit.",
            "wrap": True,
        },
        {
            "type": "Input.Text",
            "id": "message_typed",
            "placeholder": "Type something here",
            "maxLength": 120,
            "isMultiline": True,
        },
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Submit",
            "data": {"callback_keyword": "submit_message"},
        }
    ],
}


def send_message_card(room_id: str) -> None:
    send_card(api, room_id, MESSAGE_CARD, fallback_text="Send a message")


def handle_message(message, activity) -> None:
    room_id = message.roomId
    person_email = getattr(message, "personEmail", "")
    text = (getattr(message, "text", "") or "").strip().lower()

    if ALLOWED_DOMAINS and not is_allowed_domain(person_email, ALLOWED_DOMAINS):
        send_message(api, room_id, "Sorry, this bot is restricted to your lab domain.")
        return

    if text == COMMAND_KEYWORD:
        send_message_card(room_id)
        return

    send_message(api, room_id, f"Send `{COMMAND_KEYWORD}` to open the card.")


def handle_card_action(attachment_action, activity) -> None:
    room_id = attachment_action.roomId
    person_email = getattr(attachment_action, "personEmail", "")
    inputs = extract_input_values(attachment_action)
    typed_message = inputs.get("message_typed", "").strip()

    if ALLOWED_DOMAINS and not is_allowed_domain(person_email, ALLOWED_DOMAINS):
        send_message(api, room_id, "Sorry, this bot is restricted to your lab domain.")
        return

    if getattr(attachment_action, "messageId", None):
        delete_message(api, attachment_action.messageId)

    if not typed_message:
        send_message(api, room_id, "Please enter a message before submitting.")
        send_message_card(room_id)
        return

    send_message(api, room_id, typed_message)
    send_message(
        api,
        room_id,
        f"> **Notification**\n> Your message has been sent:\n> \n> {typed_message}",
    )


if __name__ == "__main__":
    bot = WebSocketClient(
        access_token=BOT_TOKEN,
        bot_name="WebexOne2026",
        on_message=handle_message,
        on_card_action=handle_card_action,
    )
    bot.run()
