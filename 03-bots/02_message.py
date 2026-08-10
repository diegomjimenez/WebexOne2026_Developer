"""Send a direct message to yourself using the bot token."""

import os

from dotenv import load_dotenv
from webexpythonsdk import WebexAPI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")

webex = WebexAPI(BOT_TOKEN)


def find_person_by_email(email: str):
    for person in webex.people.list(email=email):
        return person
    return None


def send_direct_message(email: str, text: str) -> None:
    person = find_person_by_email(email)
    if not person:
        raise RuntimeError(f"Unable to find person with email {email}")

    webex.messages.create(toPersonEmail=email, text=text)
    print(f"Message sent to {person.displayName}")


if __name__ == "__main__":
    send_direct_message(EMAIL, "Hello from your WebexOne 2026 bot!")
