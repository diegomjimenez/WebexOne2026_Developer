"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Send a direct message to yourself using the bot token.
"""

import os
from dotenv import load_dotenv
from webexpythonsdk import WebexAPI # Import the WebexAPI class from the Webex Python SDK

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for API authentication.
bot_token = os.getenv("BOT_TOKEN")
# Email address for user lookup and message recipient.
email = os.getenv("EMAIL")

# Initialize the main WebexAPI client with the bot token.
webex = WebexAPI(bot_token)

def send_teams_message(bot_token: str, message: str, person_email: str):
    """
    Sends a direct message to a specified person via Webex Teams.

    Args:
        bot_token (str): The authentication token for the Webex bot.
        message (str): The content of the message to send (supports Markdown).
        person_email (str): The email address of the recipient.
    """
    # Initialize a new WebexAPI client for sending messages.
    webexbot = WebexAPI(bot_token)
    # Create a direct message to the specified person's email with the given markdown content.
    webexbot.messages.create(toPersonEmail=person_email, markdown=message)

def find_people(email_address: str):
    """
    Finds a person by their email address using the Webex API.

    Args:
        email_address (str): The email address of the person to find.

    Returns:
        webexpythonsdk.models.Person: The first person object found, or None if an error occurs or no person is found.
    """
    try:
        # List people, filtering by the provided email address.
        # webex.people.list() returns a GeneratorContainer, so convert it to a list for indexing.
        found_people = list(webex.people.list(email=email_address))
        
        # Return the first person object found.
        if found_people:
            return found_people[0]
        else:
            print(f"No person found with email: {email_address}.")
            return None
    except Exception as e:
        # Catch and print any exceptions that occur during the API call.
        print(f"An error occurred while finding people by email: {e}")
        return None

# Find the person associated with the email loaded from environment variables.
person = find_people(email_address=email)

# If a person was found, send them a personalized message.
if person:
    send_teams_message(bot_token, f"Hello {person.displayName}!", person.emails[0])
else:
    print(f"Could not find a person with email: {email}. Message not sent.")
