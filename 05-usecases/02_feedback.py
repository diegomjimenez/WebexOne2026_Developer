"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Exercise 5.2 - Organization feedback bot.
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03-bots"))

from bot_helpers import extract_input_values, get_api, is_allowed_domain, send_card, send_message
from websocket_client import WebSocketClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVICE_APP_TOKEN = os.getenv("SERVICE_APP_TOKEN")
DOMAIN = os.getenv("DOMAIN", "")
ADMIN_EMAIL = os.getenv("EMAIL")
ALLOWED_SENDERS = {ADMIN_EMAIL} if ADMIN_EMAIL else set()

api = get_api(BOT_TOKEN)
service_api = get_api(SERVICE_APP_TOKEN) if SERVICE_APP_TOKEN else api

FEEDBACK_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {"type": "TextBlock", "text": "Organization Feedback", "weight": "Bolder", "size": "Medium"},
        {"type": "Input.Text", "id": "feedback_text", "placeholder": "Enter your feedback", "isMultiline": True},
    ],
    "actions": [{"type": "Action.Submit", "title": "Submit feedback", "data": {"callback_keyword": "feedback_submit"}}],
}

ADMIN_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {"type": "TextBlock", "text": "Feedback Assistant", "weight": "Bolder", "size": "Medium"},
        {"type": "Input.Text", "id": "request_text", "placeholder": "Feedback request message", "isMultiline": True},
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Send feedback card to all users in the organization",
            "data": {"callback_keyword": "feedback_broadcast"},
        }
    ],
}


def is_allowed_sender(email: str) -> bool:
    return email in ALLOWED_SENDERS or (DOMAIN and is_allowed_domain(email, [DOMAIN]))


def broadcast_feedback_cards(request_text: str) -> int:
    sent = 0
    for person in service_api.people.list(max=100):
        email = person.emails[0]
        card = {
            **FEEDBACK_CARD,
            "body": [
                FEEDBACK_CARD["body"][0],
                {"type": "TextBlock", "text": request_text, "wrap": True},
                FEEDBACK_CARD["body"][1],
            ],
        }
        service_api.messages.create(
            toPersonEmail=email,
            text="Feedback request",
            attachments=[{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}],
        )
        sent += 1
    return sent


def handle_message(message, activity) -> None:
    room_id = message.roomId
    person_email = getattr(message, "personEmail", "")

    if not is_allowed_sender(person_email):
        send_message(api, room_id, "You are not authorized to use the feedback assistant.")
        return

    send_card(api, room_id, ADMIN_CARD, fallback_text="Feedback Assistant")


def handle_card_action(attachment_action, activity) -> None:
    room_id = attachment_action.roomId
    person_email = getattr(attachment_action, "personEmail", "")
    inputs = extract_input_values(attachment_action)
    callback = inputs.get("callback_keyword") or attachment_action.type

    if callback == "feedback_broadcast":
        if not is_allowed_sender(person_email):
            send_message(api, room_id, "You are not authorized to broadcast feedback requests.")
            return
        request_text = inputs.get("request_text", "Please share your feedback.")
        count = broadcast_feedback_cards(request_text)
        send_message(api, room_id, f"Feedback cards sent to {count} users.")
        return

    if callback == "feedback_submit":
        feedback = inputs.get("feedback_text", "").strip()
        if ADMIN_EMAIL:
            send_message(api, room_id, "Thank you for your feedback.")
            service_api.messages.create(toPersonEmail=ADMIN_EMAIL, text=f"Feedback from {person_email}: {feedback}")
        return


if __name__ == "__main__":
    bot = WebSocketClient(
        access_token=BOT_TOKEN,
        bot_name="WebexOne2026-Feedback",
        on_message=handle_message,
        on_card_action=handle_card_action,
    )
    bot.run()
