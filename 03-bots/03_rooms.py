"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Create a room and add your lab user to it.
"""

import os

from dotenv import load_dotenv
from webexpythonsdk import WebexAPI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL = os.getenv("EMAIL")

webex = WebexAPI(BOT_TOKEN)


def create_webex_room(title: str):
    room = webex.rooms.create(title=title)
    print(f"Created room: {room.title} ({room.id})")
    return room


def add_person_to_room(room_id: str, email: str) -> None:
    membership = webex.memberships.create(roomId=room_id, personEmail=email)
    print(f"Added {membership.personEmail} to room {room_id}")


if __name__ == "__main__":
    room = create_webex_room("WebexOne 2026 Bot Room")
    add_person_to_room(room.id, EMAIL)
