"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Space directory bot: join listed spaces, or list your own space for everyone.
"""

import json
import os
import sys
from dotenv import load_dotenv
from webexpythonsdk import ApiError

# Reuse the WebSocket client and helpers from Lab 3.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03-bots"))
from websocket_client import WebSocketClient
from bot_helpers import get_api, send_message, send_card, delete_message, is_allowed_domain

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication with the Webex API.
bot_token = os.getenv("BOT_TOKEN")
api = get_api(bot_token)

# Only users whose email belongs to this domain can use the bot.
allowed_domain = os.getenv("DOMAIN")
if not allowed_domain:
    raise SystemExit("Set DOMAIN in the .env file before starting the bot.")

# The bot's own email, shown to users so they know who to add to their space.
bot_email = api.people.me().emails[0]

# The directory of listed spaces is saved next to this script, so it survives a restart.
DIRECTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spaces.json")


def load_directory():
    """
    Returns the list of spaces everyone can join: [{"id": ..., "title": ...}, ...]
    """
    if not os.path.exists(DIRECTORY_FILE):
        return []
    with open(DIRECTORY_FILE) as file:
        return json.load(file)


def save_directory(spaces):
    with open(DIRECTORY_FILE, "w") as file:
        json.dump(spaces, file, indent=2)


def is_member(room_id, person_id):
    """
    Checks whether a person is a member of a space.
    """
    return any(True for _ in api.memberships.list(roomId=room_id, personId=person_id))


def is_authorized(room_id, email):
    """
    Checks the sender's email domain and tells blocked users why they got no answer.
    """
    if is_allowed_domain(email, [allowed_domain]):
        return True

    print(f"Blocked request from {email}")
    send_message(api, room_id, f"Sorry, this bot is only available to users in {allowed_domain}.")
    return False


def menu_card():
    """
    The main menu: every message to the bot answers with this card.
    """
    return {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "Space Directory",
                "weight": "Bolder",
                "size": "Large"
            },
            {
                "type": "TextBlock",
                "text": "Join one of the listed spaces, or list one of your spaces so everyone can find it.",
                "wrap": True
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Join a space",
                "data": {"callback_keyword": "browse"}
            },
            {
                "type": "Action.Submit",
                "title": "List a space",
                "data": {"callback_keyword": "choose_space"}
            }
        ]
    }


def spaces_card(title, spaces, callback_keyword, button_title):
    """
    A card with a dropdown of spaces. The selected space ID is returned as 'room_id'.
    """
    return {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "wrap": True
            },
            {
                "type": "Input.ChoiceSet",
                "id": "room_id",
                "placeholder": "Select a space",
                "choices": [{"title": space["title"], "value": space["id"]} for space in spaces],
                "isRequired": True,
                "errorMessage": "Select a space"
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "actions": [
            {
                "type": "Action.Submit",
                "title": button_title,
                "data": {"callback_keyword": callback_keyword}
            }
        ]
    }


def show_directory(room_id):
    """
    Sends the list of spaces the user can join.
    """
    spaces = load_directory()
    if not spaces:
        send_message(api, room_id, "No spaces are listed yet. Use **List a space** to add the first one.")
        return

    send_card(api, room_id, spaces_card("Which space do you want to join?", spaces, "join", "Join"),
              fallback_text="Select a space to join")


def join_space(room_id, person_id, selected_room_id):
    """
    Adds the user to the selected space, as long as it is in the directory.
    """
    # Never trust card inputs blindly: only spaces from the directory can be joined.
    space = next((space for space in load_directory() if space["id"] == selected_room_id), None)
    if not space:
        send_message(api, room_id, "That space is not in the directory.")
        return

    try:
        api.memberships.create(roomId=space["id"], personId=person_id)
        send_message(api, room_id, f"> **Info**\n> You have been added to **{space['title']}**.")
    except ApiError as error:
        if error.status_code == 409:
            send_message(api, room_id, f"You are already a member of **{space['title']}**.")
        else:
            print(f"Could not add {person_id} to {space['title']}: {error}")
            send_message(api, room_id, f"Sorry, I could not add you to **{space['title']}**.")


def choose_space_to_list(room_id, person_id):
    """
    Sends the spaces that the user could list: group spaces where both the bot
    and the user are members, and that are not listed yet.
    """
    listed_ids = {space["id"] for space in load_directory()}
    candidates = [
        {"id": room.id, "title": room.title}
        for room in api.rooms.list(type="group")
        if room.id not in listed_ids and is_member(room.id, person_id)
    ]

    if not candidates:
        send_message(api, room_id, f"To list a space, first add me (**{bot_email}**) to it, then try again.")
        return

    send_card(api, room_id, spaces_card("Which space do you want to list?", candidates, "list_space", "List it"),
              fallback_text="Select a space to list")


def list_space(room_id, person_id, selected_room_id):
    """
    Adds the selected space to the directory, so everyone can join it.
    """
    # Check again when the card is submitted: only members can list their own spaces.
    if not is_member(selected_room_id, person_id):
        send_message(api, room_id, "You can only list spaces you are a member of.")
        return

    spaces = load_directory()
    if any(space["id"] == selected_room_id for space in spaces):
        send_message(api, room_id, "That space is already listed.")
        return

    title = api.rooms.get(selected_room_id).title
    spaces.append({"id": selected_room_id, "title": title})
    save_directory(spaces)
    send_message(api, room_id, f"> **Info**\n> **{title}** is now listed. Everyone can join it with **Join a space**.")


def handle_card_action(attachment_action, activity):
    """
    Routes each card submission to the right action using its 'callback_keyword'.
    """
    room_id = attachment_action.roomId
    person_id = attachment_action.personId

    # Card submissions only include the person ID, so look up their email first.
    person = api.people.get(person_id)
    if not is_authorized(room_id, person.emails[0]):
        return

    inputs = getattr(attachment_action, "inputs", {}) or {}
    action = inputs.get("callback_keyword")

    # Deletes the submitted card, so it cannot be submitted twice.
    delete_message(api, attachment_action.messageId)

    if action == "browse":
        show_directory(room_id)
    elif action == "join":
        join_space(room_id, person_id, inputs.get("room_id"))
    elif action == "choose_space":
        choose_space_to_list(room_id, person_id)
    elif action == "list_space":
        list_space(room_id, person_id, inputs.get("room_id"))


def handle_message(message, activity):
    """
    Any message from an allowed user gets the main menu.
    """
    if not is_authorized(message.roomId, message.personEmail):
        return

    send_card(api, message.roomId, menu_card(), fallback_text="Space Directory")


# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot using its token.
                      on_message=handle_message,      # Registers the message handler.
                      on_card_action=handle_card_action) # Registers the handler for card submissions.

# Start the bot and make it listen for incoming messages.
bot.run()
