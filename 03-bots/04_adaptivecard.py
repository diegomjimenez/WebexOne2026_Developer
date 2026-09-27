"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Send an Adaptive Card to your lab room.
"""

import os
from dotenv import load_dotenv
from webexpythonsdk import WebexAPI # Import the WebexAPI class from the Webex Python SDK

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for API authentication.
bot_token = os.getenv("BOT_TOKEN")
# Email address of the recipient for the Adaptive Card.
email = os.getenv("EMAIL")

# Initialize the WebexAPI client with the bot token.
webex = WebexAPI(bot_token)

# Define the Adaptive Card structure.
# The 'content' field should contain a valid JSON Adaptive Card payload.
card = {
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content":
        # PASTE YOUR ADAPTIVE CARD JSON HERE!
        # This is a placeholder for the actual Adaptive Card JSON structure.
        # Example structure is provided below in 'card_example'.
        {} # Placeholder for actual card content
}

# Send a message with the Adaptive Card as an attachment to the specified person.
# The 'text' parameter can be an optional fallback text if the card cannot be rendered.
webex.messages.create(toPersonEmail=email, text="Your client does not support Adaptive Cards. Please update your client.", attachments=[card])

'''
# Example Adaptive Card structure (commented out for reference).
card_content_example = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "WebexOne",
                            "horizontalAlignment": "Left",
                            "wrap": True,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }
                    ],
                        "width": "stretch"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "This is my first Adaptive Card!",
            "wrap": True
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.3"
}
'''
