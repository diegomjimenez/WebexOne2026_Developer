"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

End-user phone provisioning bot.
"""

import os
import re
import sys
import requests
from dotenv import load_dotenv

# Reuse the WebSocket client and helpers from Lab 3.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03-bots"))
from websocket_client import WebSocketClient
from bot_helpers import get_api, send_message, send_card, delete_message, is_allowed_domain

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication with the Webex API.
bot_token = os.getenv("BOT_TOKEN")
api = get_api(bot_token)

# Service App access token with the spark-admin:devices_write scope, used to create devices.
access_token = os.getenv("WEBEX_ACCESS_TOKEN")

# Only users whose email belongs to this domain can use the bot.
allowed_domain = os.getenv("DOMAIN")
if not allowed_domain:
    raise SystemExit("Set DOMAIN in the .env file before starting the bot.")


def is_authorized(room_id, email):
    """
    Checks the sender's email domain and tells blocked users why they got no answer.
    """
    if is_allowed_domain(email, [allowed_domain]):
        return True

    print(f"Blocked request from {email}")
    send_message(api, room_id, f"Sorry, this bot is only available to users in {allowed_domain}.")
    return False


def normalize_mac_address(mac):
    """
    Accepts AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF or AABBCCDDEEFF.
    Returns the MAC address as 12 uppercase characters, or None if the format is wrong.
    """
    mac = (mac or "").strip().upper()
    if re.fullmatch(r"([0-9A-F]{2}[:-]){5}[0-9A-F]{2}|[0-9A-F]{12}", mac):
        return re.sub(r"[:-]", "", mac)
    return None


def menu_card():
    """
    The main menu: every message to the bot answers with this card.
    """
    return {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "Welcome to the Auto-Provisioning Bot!",
                "weight": "Bolder",
                "size": "Large",
                "wrap": True
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Provision your new IP Phone",
                "data": {"callback_keyword": "provision"}
            }
        ]
    }


def provision_card():
    """
    The provisioning form: phone model and MAC address.
    """
    return {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "Please select the model and enter the MAC address of your new phone:",
                "wrap": True
            },
            {
                "type": "Input.ChoiceSet",
                "choices": [
                    {"title": "DMS Cisco 8851", "value": "DMS Cisco 8851"},
                    {"title": "DMS Cisco 8861", "value": "DMS Cisco 8861"},
                    {"title": "DMS Cisco 8865", "value": "DMS Cisco 8865"}
                ],
                "placeholder": "Phone model",
                "id": "model",
                "isRequired": True,
                "errorMessage": "Model is required",
                "label": "Select model:"
            },
            {
                "type": "Input.Text",
                "placeholder": "AA:BB:CC:DD:EE:FF",
                "id": "mac_address",
                "isRequired": True,
                "errorMessage": "MAC is required",
                "label": "MAC Address:"
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit",
                "data": {"callback_keyword": "provision_callback"}
            }
        ]
    }


def provision_device(room_id, person_id, inputs):
    """
    Validates the submitted data and creates the device for the user with the Devices API.
    """
    mac_address = normalize_mac_address(inputs.get("mac_address"))
    model = inputs.get("model")

    if not mac_address:
        send_message(api, room_id, "> **Error**\n> MAC Address format is incorrect. Use a format like AA:BB:CC:DD:EE:FF or AABBCCDDEEFF.")
        return

    payload = {
        "mac": mac_address,
        "model": model,
        "personId": person_id
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post("https://webexapis.com/v1/devices", headers=headers, json=payload, timeout=30)
    print(f"Provisioning {model} {mac_address}: {response.status_code}")

    if response.status_code == 200:
        send_message(api, room_id, f"> **Info**\n> Your {model} ({mac_address}) has been added successfully.")
    elif response.status_code == 409:
        send_message(api, room_id, "> **Error**\n> This MAC Address is already registered.")
    else:
        print(response.text)
        send_message(api, room_id, "> **Error**\n> There was an error provisioning your phone.")


def handle_card_action(attachment_action, activity):
    """
    Routes each card submission to the right action using its 'callback_keyword'.
    """
    room_id = attachment_action.roomId

    # Card submissions only include the person ID, so look up their email first.
    person = api.people.get(attachment_action.personId)
    if not is_authorized(room_id, person.emails[0]):
        return

    inputs = getattr(attachment_action, "inputs", {}) or {}
    action = inputs.get("callback_keyword")

    # Deletes the submitted card, so it cannot be submitted twice.
    delete_message(api, attachment_action.messageId)

    if action == "provision":
        send_card(api, room_id, provision_card(), fallback_text="Provision your new IP Phone")
    elif action == "provision_callback":
        provision_device(room_id, attachment_action.personId, inputs)


def handle_message(message, activity):
    """
    Any message from an allowed user gets the main menu.
    """
    if not is_authorized(message.roomId, message.personEmail):
        return

    send_card(api, message.roomId, menu_card(), fallback_text="Auto-Provisioning Bot")


# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot using its token.
                      on_message=handle_message,      # Registers the message handler.
                      on_card_action=handle_card_action) # Registers the handler for card submissions.

# Start the bot and make it listen for incoming messages.
bot.run()
