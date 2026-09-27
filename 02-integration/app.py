"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

"""
# Lab 2 exercise - a tiny web app that uses your integration (OAuth 2.0 Authorization Code flow)
# to list your rooms and send a message on your behalf. Open http://localhost:3000 after starting it.

import html
import os
import secrets
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    sys.exit("CLIENT_ID and CLIENT_SECRET must be set in your .env file (see Lab 2).")

PORT = 3000
REDIRECT_URI = f"http://localhost:{PORT}/callback"
SCOPES = "spark:people_read spark:rooms_read spark:messages_write"
API = "https://webexapis.com/v1"

# Demo only: a single user's token kept in memory while the server runs.
session = {"token": None, "state": None}

PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Webex Integration Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f5f7; }}
        .container {{ max-width: 500px; margin: auto; padding: 20px; background: white; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        a.button, button {{ display: block; text-align: center; text-decoration: none; background-color: #00a0d1; color: white; border: none; cursor: pointer; font-weight: bold; }}
        a.button:hover, button:hover {{ background-color: #007aa3; }}
        a.button, button, select, input {{ width: 100%; padding: 10px; margin: 10px 0; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }}
        .ok {{ color: green; font-weight: bold; }}
        .error {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Webex Integration Demo</h2>
        {body}
    </div>
</body>
</html>"""


def webex(method, path, token, **kwargs):
    return requests.request(method, f"{API}{path}", headers={"Authorization": f"Bearer {token}"}, timeout=15, **kwargs)


class Handler(BaseHTTPRequestHandler):
    def send_page(self, body, status=200):
        content = PAGE.format(body=body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if url.path == "/login":
            session["state"] = secrets.token_urlsafe(16)
            params = {
                "client_id": CLIENT_ID,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPES,
                "state": session["state"],
            }
            return self.redirect(f"{API}/authorize?{urlencode(params)}")

        if url.path == "/callback":
            if query.get("state", [None])[0] != session["state"]:
                return self.send_page('<p class="error">Invalid state. Please try again.</p><a class="button" href="/login">Login with Webex</a>', 400)
            if "error" in query:
                return self.send_page(f'<p class="error">Authorization failed: {html.escape(query["error"][0])}</p><a class="button" href="/login">Try again</a>', 400)

            response = requests.post(f"{API}/access_token", data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": query.get("code", [""])[0],
                "redirect_uri": REDIRECT_URI,
            }, timeout=15)
            if not response.ok:
                return self.send_page(f'<p class="error">Token exchange failed: {html.escape(response.text)}</p><a class="button" href="/login">Try again</a>', 400)

            session["token"] = response.json()["access_token"]
            print("Access token received. Open http://localhost:3000")
            return self.redirect("/")

        if url.path == "/logout":
            session["token"] = None
            return self.redirect("/")

        if url.path == "/":
            return self.home(query)

        self.send_error(404)

    def do_POST(self):
        if self.path != "/send" or not session["token"]:
            return self.redirect("/")

        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode())
        room_id = form.get("roomId", [""])[0]
        text = form.get("text", [""])[0]

        response = webex("POST", "/messages", session["token"], json={"roomId": room_id, "text": text})
        result = "sent" if response.ok else "failed"
        self.redirect(f"/?{urlencode({'result': result})}")

    def home(self, query):
        token = session["token"]
        if not token:
            return self.send_page(
                "<p>Click below to authorize this app to access your Webex account.</p>"
                '<a class="button" href="/login">Login with Webex</a>'
            )

        me = webex("GET", "/people/me", token)
        rooms = webex("GET", "/rooms", token, params={"max": 50, "sortBy": "lastactivity"})
        if not me.ok or not rooms.ok:
            session["token"] = None
            return self.send_page('<p class="error">Your token is no longer valid.</p><a class="button" href="/login">Login again</a>')

        options = "".join(
            f'<option value="{html.escape(room["id"])}">{html.escape(room.get("title") or "Untitled room")}</option>'
            for room in rooms.json().get("items", [])
        )

        status = ""
        result = query.get("result", [None])[0]
        if result == "sent":
            status = '<p class="ok">Message sent successfully!</p>'
        elif result == "failed":
            status = '<p class="error">Failed to send message.</p>'

        self.send_page(
            f"<p>Logged in as <b>{html.escape(me.json().get('displayName', ''))}</b> (<a href=\"/logout\">logout</a>)</p>"
            "<h3>Send a Message</h3>"
            '<form method="post" action="/send">'
            '<label for="rooms">Select a Room:</label>'
            f'<select id="rooms" name="roomId" required>{options}</select>'
            '<label for="message">Message:</label>'
            '<input type="text" id="message" name="text" placeholder="Hello from my custom app!" required>'
            '<button type="submit">Send Message</button>'
            "</form>"
            f"{status}"
        )


if __name__ == "__main__":
    print(f"Webex Integration Demo running on http://localhost:{PORT}")
    HTTPServer(("localhost", PORT), Handler).serve_forever()
