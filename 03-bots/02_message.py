"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

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
# Your email address, used to find your user ID.
email = os.getenv("EMAIL")

# Initialize the WebexAPI client with the bot token.
webex = WebexAPI(bot_token)

def create_webex_room(room_title: str):
    """
    Creates a new Webex room with the given title.

    Args:
        room_title (str): The title for the new Webex room.

    Returns:
        webexpythonsdk.models.Room: The created room object if successful, None otherwise.
    """
    try:
        print(f"Attempting to create room with title: '{room_title}'...")
        new_room = webex.rooms.create(title=room_title)
        print(f"Room created successfully! Room ID: {new_room.id}, Title: {new_room.title}")
        return new_room
    except Exception as e:
        print(f"An error occurred while creating the room: {e}")
        return None

def add_person_to_room(room_id: str, person_email: str):
    """
    Finds a person by their email and adds them to a specified Webex room.

    Args:
        room_id (str): The ID of the room to add the person to.
        person_email (str): The email address of the person to add.

    Returns:
        webexpythonsdk.models.Membership: The membership object if successful, None otherwise.
    """
    try:
        # 1. Find the user by email to get their person ID
        print(f"Attempting to find user with email: '{person_email}'...")
        # webex.people.list() returns a GeneratorContainer, which is iterable.
        found_people = list(webex.people.list(email=person_email))
        
        if found_people:
            # Assuming the first result is the correct person
            person_to_add = found_people[0]
            print(f"Found user: {person_to_add.displayName}, Person ID: {person_to_add.id}")

            # 2. Add the user to the specified room
            print(f"Attempting to add {person_to_add.displayName} to room ID: '{room_id}'...")
            membership = webex.memberships.create(
                roomId=room_id,
                personId=person_to_add.id
            )
            print(f"User '{person_to_add.displayName}' added to room successfully! Membership ID: {membership.id}")
            return membership
        else:
            print(f"Error: Could not find any user with email '{person_email}'. Cannot add to room.")
            return None
    except Exception as e:
        print(f"An error occurred while adding person to room: {e}")
        return None

# Define the title for your new room.
new_room_name = "WebexOne Room"

# Step 1: Create the room
created_room = create_webex_room(new_room_name)

# Step 2: If the room was created successfully, add yourself to it.
if created_room:
    add_person_to_room(created_room.id, email)
else:
    print("Room creation failed, cannot proceed to add members.")
