"""
Webex One 2026 - Troubleshoot and Manage Your Organization with an AI Assistant

- Diego Manuel Jimenez Moreno
- Phil Bellanti
- Adam Weeks

WebSocket client
"""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
import uuid
from typing import Callable, Optional

import certifi
import requests
import websockets
from webexpythonsdk import WebexAPI

logger = logging.getLogger(__name__)

DEFAULT_U2C_URL = "https://u2c.wbx2.com/u2c/api/v1/catalog"
DEVICE_DATA = {
    "deviceName": "webexone2026-bot",
    "deviceType": "DESKTOP",
    "localizedModel": "python",
    "model": "python",
    "name": "webexone2026-bot",
    "systemName": "webexone2026-bot",
    "systemVersion": "1.0",
}

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

MessageHandler = Callable[..., None]
CardActionHandler = Callable[..., None]


class WebSocketClient:
    def __init__(
        self,
        access_token: str,
        bot_name: str = "WebexOne2026",
        on_message: Optional[MessageHandler] = None,
        on_card_action: Optional[CardActionHandler] = None,
    ) -> None:
        self.access_token = access_token
        self.bot_name = bot_name
        self.api = WebexAPI(access_token=access_token)
        self.session = requests.Session()
        self.tracking_id = f"webexone2026_{uuid.uuid4()}"
        self.session.headers.update(self._headers())
        self.api._session.update_headers(self._headers())
        self.on_message = on_message
        self.on_card_action = on_card_action
        self.device_info = None
        self.device_url = self._get_device_url()
        self.websocket = None
        self.share_id = None

    def _headers(self) -> dict:
        sdk_ua = self.api._session.headers["User-Agent"]
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": f"WebexOne2026-Bot '{self.bot_name}' ({sdk_ua})",
            "trackingid": self.tracking_id,
        }

    def _get_device_url(self) -> str:
        response = self.session.get(DEFAULT_U2C_URL, params={"format": "hostmap"})
        response.raise_for_status()
        return response.json()["serviceLinks"]["wdm"]

    def _get_device_info(self, check_existing: bool = True) -> dict:
        if check_existing:
            response = self.session.get(f"{self.device_url}/devices")
            response.raise_for_status()
            for device in response.json().get("devices", []):
                if device["name"] == DEVICE_DATA["name"]:
                    self.device_info = device
                    return device

        response = self.session.post(f"{self.device_url}/devices", json=DEVICE_DATA)
        response.raise_for_status()
        self.device_info = response.json()
        return self.device_info

    def _get_base64_message_id(self, activity: dict) -> str:
        activity_id = activity["id"]
        conversation_url = activity["target"]["url"]
        conv_target_id = activity["target"]["id"]
        verb = "messages" if activity["verb"] in ["post", "update"] else "attachment/actions"
        if activity["verb"] == "update" and self.share_id is not None:
            activity_id = self.share_id
            self.share_id = None

        conversation_message_url = conversation_url.replace(
            f"conversations/{conv_target_id}", f"{verb}/{activity_id}"
        )
        conversation_message = self.session.get(conversation_message_url).json()
        return conversation_message["id"]

    def _ack_message(self, message_id: str) -> None:
        ack_message = {"type": "ack", "messageId": message_id}
        asyncio.run(self.websocket.send(json.dumps(ack_message)))

    def _process_incoming_websocket_message(self, msg: dict) -> None:
        data = msg.get("data", {})
        if data.get("eventType") != "conversation.activity":
            return

        activity = data["activity"]
        verb = activity.get("verb")

        if verb == "share":
            self.share_id = activity["id"]
            return

        if verb == "post":
            message_id = self._get_base64_message_id(activity)
            webex_message = self.api.messages.get(message_id)
            self._ack_message(message_id)
            if self.on_message:
                self.on_message(webex_message, activity)
            return

        if verb == "update":
            obj = activity.get("object", {})
            if obj.get("objectType") != "content" or obj.get("contentCategory") != "documents":
                return
            message_id = self._get_base64_message_id(activity)
            webex_message = self.api.messages.get(message_id)
            self._ack_message(message_id)
            if self.on_message:
                self.on_message(webex_message, activity)
            return

        if verb == "cardAction":
            message_id = self._get_base64_message_id(activity)
            attachment_action = self.api.attachment_actions.get(message_id)
            self._ack_message(message_id)
            if self.on_card_action:
                self.on_card_action(attachment_action, activity)

    async def _connect_and_listen(self) -> None:
        ws_url = self.device_info["webSocketUrl"]
        async with websockets.connect(ws_url, ssl=ssl_context, extra_headers=self._headers()) as websocket:
            self.websocket = websocket
            print("WebSocket connected")
            auth = {
                "id": str(uuid.uuid4()),
                "type": "authorization",
                "data": {"token": f"Bearer {self.access_token}"},
            }
            await websocket.send(json.dumps(auth))

            while True:
                raw = await websocket.recv()
                msg = json.loads(raw)
                loop = asyncio.get_event_loop()
                loop.run_in_executor(None, self._process_incoming_websocket_message, msg)

    def run(self) -> None:
        if self.device_info is None and self._get_device_info() is None:
            raise RuntimeError("Unable to register bot device for WebSocket connection")

        while True:
            try:
                asyncio.get_event_loop().run_until_complete(self._connect_and_listen())
            except Exception as exc:
                logger.warning("WebSocket connection error: %s", exc)
                self._get_device_info(check_existing=False)
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))
