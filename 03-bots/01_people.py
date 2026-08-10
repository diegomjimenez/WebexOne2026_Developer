"""Find people in the organization using the Webex People API."""

import os

from dotenv import load_dotenv
from webexpythonsdk import WebexAPI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")
DOMAIN = os.getenv("DOMAIN")

webex = WebexAPI(BOT_TOKEN)


def find_people(display_name: str) -> None:
    """Find people by display name."""
    try:
        for person in webex.people.list(displayName=display_name):
            print(f"Name: {person.displayName}, Email: {person.emails}")
    except Exception as exc:
        print(f"An error occurred: {exc}")


def all_people() -> None:
    """List all people in the organization.

    Requires admin privileges and will not work with a standard bot token.
    """
    try:
        for person in webex.people.list():
            print(f"Name: {person.displayName}, Email: {person.emails}")
    except Exception as exc:
        print(f"An error occurred: {exc}")


if __name__ == "__main__":
    if EMAIL:
        find_people(EMAIL.split("@")[0])
    if DOMAIN:
        print(f"\nLab domain: {DOMAIN}")
