"""Sample Service App for scheduling a meeting on behalf of a user."""

import datetime
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENTID")
SECRET_ID = os.getenv("SECRETID")
ACCESS_TOKEN = os.getenv("WEBEX_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
HOST_EMAIL = os.getenv("HOST_EMAIL", "A sub users email")


def get_tokens_refresh() -> tuple[str, str]:
    url = "https://webexapis.com/v1/access_token"
    headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
    payload = (
        f"grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={SECRET_ID}"
        f"&refresh_token={REFRESH_TOKEN}"
    )
    response = requests.post(url=url, data=payload, headers=headers, timeout=30)
    response.raise_for_status()
    results = response.json()
    return results["access_token"], results["refresh_token"]


def create_meeting(access_token: str):
    start = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)).replace(microsecond=0).isoformat()
    end = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=25)).replace(microsecond=0).isoformat()

    body = {
        "title": "Automatic Meeting Example",
        "start": start,
        "end": end,
        "hostEmail": HOST_EMAIL,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    return requests.post(
        "https://webexapis.com/v1/meetings",
        headers=headers,
        data=json.dumps(body),
        timeout=30,
    )


if __name__ == "__main__":
    access_token = ACCESS_TOKEN
    refresh_token = REFRESH_TOKEN

    response = create_meeting(access_token)
    if response.status_code == 401:
        access_token, refresh_token = get_tokens_refresh()
        response = create_meeting(access_token)

    if response.status_code == 200:
        print("Meeting created successfully")
        print(response.json())
    else:
        print("Error:", response.status_code, response.text)
