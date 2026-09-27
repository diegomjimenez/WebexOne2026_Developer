"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Paginate through organization users.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

SERVICE_APP_TOKEN = os.getenv("SERVICE_APP_TOKEN")
MAX = 2


def list_people_page(url: str | None = None) -> None:
    headers = {"Authorization": f"Bearer {SERVICE_APP_TOKEN}"}
    params = {"max": MAX}
    response = requests.get(url or "https://webexapis.com/v1/people", headers=headers, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    for person in payload.get("items", []):
        print(f"Name: {person.get('displayName')} | Email: {person.get('emails', [''])[0]}")

    links = payload.get("links", {})
    if "next" in links:
        print("\n--- Next page ---\n")
        list_people_page(links["next"])


if __name__ == "__main__":
    list_people_page()
