"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Process Adaptive Card submissions.
"""

import os
from dotenv import load_dotenv
from websocket_client import WebSocketClient
from bot_helpers import get_api, send_message, send_card, delete_message

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication with the Webex API.
bot_token = os.getenv("BOT_TOKEN")
api = get_api(bot_token)


def handle_card_action(attachment_action, activity):
    """
    Executes when an Adaptive Card with 'callback_keyword': 'message_callback' is submitted.
    It extracts the message input from the card and sends it back to the user.
    """
    room_id = attachment_action.roomId
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
    Executes the 'message' command. Constructs and sends an Adaptive Card
    to the user for input.
    """
    room_id = message.roomId
    text = (getattr(message, "text", "") or "").strip().lower()
    
    # The keyword users type to activate this command.
    if text == "message":
        # Define the Adaptive Card structure for user input.
        card = {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
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
        }
        
        # Attach the Adaptive Card to the response.
        send_card(api, room_id, card, fallback_text="Please enter your message:")


# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot using its token.
                      on_message=handle_message,      # Registers the message handler.
                      on_card_action=handle_card_action) # Registers the callback command for card submissions.

# Start the bot and make it listen for incoming messages.
# This call is typically blocking and keeps the bot running, waiting for commands or card submissions.
bot.run()

