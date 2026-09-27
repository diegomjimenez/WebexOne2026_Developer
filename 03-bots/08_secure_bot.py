"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks
"""

import os
from dotenv import load_dotenv
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


def is_authorized(room_id, email):
    """
    Checks the sender's email domain and tells blocked users why they got no answer.
    """
    if is_allowed_domain(email, [allowed_domain]):
        return True

    print(f"Blocked request from {email}")
    send_message(api, room_id, f"Sorry, this bot is only available to users in {allowed_domain}.")
    return False


def handle_card_action(attachment_action, activity):
    """
    Executes when the Adaptive Card is submitted, but only for users in the allowed domain.
    """
    room_id = attachment_action.roomId

    # Card submissions only include the person ID, so look up their email first.
    # In group spaces anyone can press Submit, so this check matters here too.
    person = api.people.get(attachment_action.personId)
    if not is_authorized(room_id, person.emails[0]):
        return

    inputs = getattr(attachment_action, "inputs", {}) or {}

    # Extract the 'message' input from the submitted Adaptive Card's inputs.
    message_content = inputs.get("message")

    # Deletes the Adaptive Card message after submission.
    if getattr(attachment_action, "messageId", None):
        delete_message(api, attachment_action.messageId)

    # Create a direct message to the room with the extracted message content.
    if message_content:
        send_message(api, room_id, message_content)
        # Return a confirmation message, formatted as an info quote.
        send_message(api, room_id, "> **Info**\n> Message sent")


def handle_message(message, activity):
    """
    Executes the 'message' command, but only for users in the allowed domain.
    """
    room_id = message.roomId

    # Messages already include the sender's email, so check it before doing anything else.
    if not is_authorized(room_id, message.personEmail):
        return

    text = (getattr(message, "text", "") or "").strip().lower()
    # In group spaces the text starts with the bot mention, so only check the last word.
    command = text.split()[-1] if text else ""

    # The keyword users type to activate this command.
    if command == "message":
        # Define the Adaptive Card structure for user input.
        card = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "Input.Text",
                    "placeholder": "Message",
                    "id": "message",
                    "isRequired": True,
                    "errorMessage": "Message is required",
                    "label": "Message:"
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3",
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Submit",
                    "data": {
                        "callback_keyword": "message_callback" # This links to the card action handler.
                    }
                }
            ]
        }

        # Attach the Adaptive Card to the response.
        send_card(api, room_id, card, fallback_text="Please enter your message:")
    else:
        # Let the user know which keyword the bot understands.
        send_message(api, room_id, "Type 'message' to get the card.")


# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot using its token.
                      on_message=handle_message,      # Registers the message handler.
                      on_card_action=handle_card_action) # Registers the callback command for card submissions.

# Start the bot and make it listen for incoming messages.
bot.run()
