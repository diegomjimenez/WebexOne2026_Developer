"""
Webex One 2026 - Exploring the Webex Developer Ecosystem

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

Paginate through organization users.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Service App access token with the spark-admin:people_read scope.
access_token = os.getenv("WEBEX_ACCESS_TOKEN")
MAX = 2


def list_people_page(url: str | None = None) -> None:
    headers = {"Authorization": f"Bearer {access_token}"}
    # The 'next' link already includes the page size, so only send it on the first request.
    params = None if url else {"max": MAX}
    response = requests.get(url or "https://webexapis.com/v1/people", headers=headers, params=params, timeout=30)
    response.raise_for_status()

    for person in response.json().get("items", []):
        print(f"Name: {person.get('displayName')} | Email: {person.get('emails', [''])[0]}")

    # Webex returns the next page URL in the 'Link' header with rel="next".
    if "next" in response.links:
        print("\n--- Next page ---\n")
        list_people_page(response.links["next"]["url"])


if __name__ == "__main__":
    list_people_page()
