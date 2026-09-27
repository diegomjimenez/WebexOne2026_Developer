"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Exercise 5.3 - End-user phone provisioning bot.
"""

import os
import re
import sys

import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03-bots"))

from bot_helpers import extract_input_values, get_api, send_card, send_message
from websocket_client import WebSocketClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVICE_APP_TOKEN = os.getenv("SERVICE_APP_TOKEN")

api = get_api(BOT_TOKEN)

MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^[0-9A-Fa-f]{12}$")

PROVISION_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {"type": "TextBlock", "text": "Provision your new IP Phone", "weight": "Bolder", "size": "Medium"},
        {"type": "Input.Text", "id": "mac_address", "placeholder": "AA:BB:CC:DD:EE:FF"},
        {
            "type": "Input.ChoiceSet",
            "id": "phone_model",
            "value": "DMS Cisco 8851",
            "choices": [
                {"title": "DMS Cisco 8851", "value": "DMS Cisco 8851"},
                {"title": "DMS Cisco 8861", "value": "DMS Cisco 8861"},
                {"title": "DMS Cisco 8865", "value": "DMS Cisco 8865"},
            ],
        },
    ],
    "actions": [{"type": "Action.Submit", "title": "Provision", "data": {"callback_keyword": "provision_device"}}],
}

MENU_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [{"type": "TextBlock", "text": "Phone Provisioning Assistant", "weight": "Bolder"}],
    "actions": [{"type": "Action.Submit", "title": "Provision your new IP Phone", "data": {"callback_keyword": "open_provision"}}],
}


def is_valid_mac_address(value: str) -> bool:
    return bool(MAC_REGEX.match(value.strip()))


def normalize_mac(value: str) -> str:
    cleaned = value.replace(":", "").replace("-", "").upper()
    return ":".join(cleaned[i : i + 2] for i in range(0, 12, 2))


def provision_device(mac_address: str, phone_model: str) -> tuple[bool, str]:
    payload = {
        "mac": normalize_mac(mac_address),
        "model": phone_model,
        "name": f"WebexOne-{mac_address[-4:]}",
    }
    headers = {"Authorization": f"Bearer {SERVICE_APP_TOKEN or BOT_TOKEN}"}
    response = requests.post("https://webexapis.com/v1/devices", headers=headers, json=payload, timeout=30)
    if response.status_code in (200, 201):
        return True, f"Device {payload['mac']} provisioned successfully as {phone_model}."
    if response.status_code == 409:
        return False, "That MAC address is already registered."
    return False, f"Provisioning failed: {response.status_code} {response.text}"


def handle_message(message, activity) -> None:
    send_card(api, message.roomId, MENU_CARD, fallback_text="Phone Provisioning Assistant")


def handle_card_action(attachment_action, activity) -> None:
    room_id = attachment_action.roomId
    inputs = extract_input_values(attachment_action)
    callback = inputs.get("callback_keyword")

    if callback == "open_provision":
        send_card(api, room_id, PROVISION_CARD, fallback_text="Provision your new IP Phone")
        return

    if callback == "provision_device":
        mac_address = inputs.get("mac_address", "")
        phone_model = inputs.get("phone_model", "DMS Cisco 8851")

        if not is_valid_mac_address(mac_address):
            send_message(api, room_id, "Invalid MAC address format. Use AA:BB:CC:DD:EE:FF or AABBCCDDEEFF.")
            return

        _, result_message = provision_device(mac_address, phone_model)
        send_message(api, room_id, result_message)


if __name__ == "__main__":
    bot = WebSocketClient(
        access_token=BOT_TOKEN,
        bot_name="WebexOne2026-Provisioning",
        on_message=handle_message,
        on_card_action=handle_card_action,
    )
    bot.run()
