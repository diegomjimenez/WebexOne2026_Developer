"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Organization feedback bot.
"""

import os
import sys
from dotenv import load_dotenv
from webexpythonsdk import WebexAPI  # Import the Webex API SDK for making direct Webex API calls.

# Reuse the WebSocket client and helpers from Lab 3.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "03-bots"))
from websocket_client import WebSocketClient
from bot_helpers import get_api, send_message, send_card, delete_message, is_allowed_domain

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for authentication with the Webex API.
bot_token = os.getenv("BOT_TOKEN")
api = get_api(bot_token)

# Service App access token with the spark-admin:people_read scope, used to list all people in the org.
access_token = os.getenv("WEBEX_ACCESS_TOKEN")

# The only user allowed to send feedback requests. This user also receives all the feedback.
email = os.getenv("EMAIL")

# Only users whose email belongs to this domain can use the bot.
allowed_domain = os.getenv("DOMAIN")
if not allowed_domain:
    raise SystemExit("Set DOMAIN in the .env file before starting the bot.")


def is_authorized(room_id, sender_email):
    """
    Checks the sender's email domain and tells blocked users why they got no answer.
    """
    if is_allowed_domain(sender_email, [allowed_domain]):
        return True

    print(f"Blocked request from {sender_email}")
    send_message(api, room_id, f"Sorry, this bot is only available to users in {allowed_domain}.")
    return False


def is_allowed_sender(sender_email):
    """
    Checks if the sender is the admin configured in EMAIL. Case-insensitive comparison.
    """
    if not email:
        print("EMAIL is not set in .env. All users are blocked from sending feedback requests.")
        return False
    return sender_email.lower() == email.lower()


def menu_card():
    """
    The main menu: every message to the bot answers with this card.
    """
    return {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "Feedback Bot",
                "weight": "Bolder",
                "size": "Large"
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Send feedback card to all users in the organization",
                "data": {"callback_keyword": "feedback"}
            }
        ]
    }


def feedback_card():
    """
    The card every user in the organization receives.
    """
    return {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "We'd love to hear your thoughts!",
                "wrap": True,
                "size": "Medium",
                "weight": "Bolder"
            },
            {
                "type": "Input.Text",
                "placeholder": "Enter your feedback here...",
                "id": "feedback_input", # This ID will be used to extract the input value.
                "isMultiline": True,
                "isRequired": True,
                "errorMessage": "Feedback cannot be empty.",
                "label": "Your Feedback:"
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit Feedback",
                "data": {"callback_keyword": "feedback_submit"}
            }
        ]
    }


def send_feedback_to_all(room_id, sender_email):
    """
    Sends the feedback card to every user in the organization. Only the admin in EMAIL can do this.
    """
    if not is_allowed_sender(sender_email):
        print(f"Unauthorized user {sender_email} tried to send feedback requests.")
        send_message(api, room_id, "> **Error**\n> You are not authorized to send feedback requests to the entire organization.")
        return

    # Bots cannot list everyone in the organization, so use the Service App token.
    # The SDK follows the pagination links automatically, like 03_pagination.py does by hand.
    service_app = WebexAPI(access_token=access_token)
    try:
        all_people = [person for person in service_app.people.list() if person.emails]
    except Exception as error:
        print(f"Error listing people: {error}")
        send_message(api, room_id, "> **Error**\n> I could not list the users in the organization.")
        return

    print(f"Sending the feedback card to {len(all_people)} people")
    failed = 0
    for person in all_people:
        try:
            api.messages.create(
                toPersonEmail=person.emails[0],
                text="Please provide your feedback:", # Fallback text.
                attachments=[{"contentType": "application/vnd.microsoft.card.adaptive", "content": feedback_card()}]
            )
        except Exception as error:
            failed += 1
            print(f"Error sending the feedback card to {person.emails[0]}: {error}")

    summary = f"Feedback cards have been sent to {len(all_people) - failed} users in the organization."
    if failed:
        summary += f" {failed} could not be sent, check the console for details."
    send_message(api, room_id, f"> **Info**\n> {summary}")


def submit_feedback(room_id, sender_email, feedback_text):
    """
    Forwards the submitted feedback to the admin in EMAIL and thanks the user.
    """
    print(f"Feedback submitted by {sender_email}")
    try:
        api.messages.create(
            toPersonEmail=email,
            markdown=f"**New Feedback Received!**\n\n**From:** {sender_email}\n**Feedback:**\n```\n{feedback_text}\n```"
        )
        send_message(api, room_id, "> **Info**\n> Thank you for your feedback! It has been submitted.")
    except Exception as error:
        print(f"Error forwarding feedback to {email}: {error}")
        send_message(api, room_id, "> **Error**\n> There was an error submitting your feedback. Please try again later.")


def handle_card_action(attachment_action, activity):
    """
    Routes each card submission to the right action using its 'callback_keyword'.
    """
    room_id = attachment_action.roomId

    # Card submissions only include the person ID, so look up their email first.
    sender_email = api.people.get(attachment_action.personId).emails[0]
    if not is_authorized(room_id, sender_email):
        return

    inputs = getattr(attachment_action, "inputs", {}) or {}
    action = inputs.get("callback_keyword")

    # Deletes the submitted card, so it cannot be submitted twice.
    delete_message(api, attachment_action.messageId)

    if action == "feedback":
        send_feedback_to_all(room_id, sender_email)
    elif action == "feedback_submit":
        submit_feedback(room_id, sender_email, inputs.get("feedback_input"))


def handle_message(message, activity):
    """
    Any message from an allowed user gets the main menu.
    """
    if not is_authorized(message.roomId, message.personEmail):
        return

    send_card(api, message.roomId, menu_card(), fallback_text="Feedback Bot")


# Create a WebSocket Client object.
bot = WebSocketClient(access_token=bot_token,         # Authenticate the bot using its token.
                      on_message=handle_message,      # Registers the message handler.
                      on_card_action=handle_card_action) # Registers the handler for card submissions.

# Start the bot and make it listen for incoming messages.
bot.run()
