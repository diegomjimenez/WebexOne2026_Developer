"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Find people in the organization using the Webex People API.
"""

import os
from dotenv import load_dotenv
from webexpythonsdk import WebexAPI # Import the WebexAPI class from the Webex Python SDK

# Load environment variables from the .env file.
load_dotenv()

# Webex Bot Token for API authentication.
bot_token = os.getenv("BOT_TOKEN")
# Email address for user lookup.
email = os.getenv("EMAIL")

# Initialize the WebexAPI client with the bot token.
webex = WebexAPI(bot_token)

def all_people():
    """
    Retrieves and prints the display name and email(s) for all people
    accessible by the authenticated Webex bot/user.
    """
    try:
        # List all people in the organization.
        # webex.people.list() returns a GeneratorContainer, which is iterable.
        all_people_iterator = webex.people.list()
        # Iterate through the people and print their details.
        for person in all_people_iterator:
            print(f"Name: {person.displayName}, Email: {person.emails}")
    except Exception as e:
        # Catch and print any exceptions that occur during the API call.
        print(f"An error occurred while listing all people: {e}")

def find_people(email_address: str):
    """
    Finds and prints the display name and email(s) for a specific person
    based on their email address.

    Args:
        email_address (str): The email address of the person to find.
    """
    try:
        # List people, filtering by the provided email address.
        # webex.people.list() returns a GeneratorContainer, which is iterable.
        found_people_iterator = webex.people.list(email=email_address)
        # Iterate through the (potentially single) person found and print their details.
        for person in found_people_iterator:
            print(f"Name: {person.displayName}, Email: {person.emails}")
    except Exception as e:
        # Catch and print any exceptions that occur during the API call.
        print(f"An error occurred while finding people by email: {e}")

# Call the find_people function using the email loaded from environment variables.
find_people(email_address=email)

# Call the all_people function to list all accessible users.
all_people()
