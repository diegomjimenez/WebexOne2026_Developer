"""Send an Adaptive Card to your lab room."""

import json
import os

from dotenv import load_dotenv
from webexpythonsdk import WebexAPI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")

webex = WebexAPI(BOT_TOKEN)

CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "WebexOne 2026 Adaptive Card",
            "weight": "Bolder",
            "size": "Medium",
        },
        {
            "type": "TextBlock",
            "text": "Replace this card with your own design from the Buttons and Cards Designer.",
            "wrap": True,
        },
    ],
}


def find_person_by_email(email: str):
    for person in webex.people.list(email=email):
        return person
    return None


def send_card_to_user(email: str) -> None:
    person = find_person_by_email(email)
    if not person:
        raise RuntimeError(f"Unable to find person with email {email}")

    webex.messages.create(
        toPersonEmail=email,
        text="Adaptive Card",
        attachments=[
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": CARD,
            }
        ],
    )
    print("Adaptive Card sent")


if __name__ == "__main__":
    send_card_to_user(EMAIL)
