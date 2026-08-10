"""Shared helpers for the Lab 3 bot exercises."""

from __future__ import annotations

from typing import Any

from webexpythonsdk import WebexAPI


def get_api(token: str) -> WebexAPI:
    return WebexAPI(access_token=token)


def send_message(api: WebexAPI, room_id: str, text: str) -> None:
    api.messages.create(roomId=room_id, text=text)


def send_card(api: WebexAPI, room_id: str, card: dict[str, Any], fallback_text: str = "Card") -> None:
    api.messages.create(
        roomId=room_id,
        text=fallback_text,
        attachments=[
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card,
            }
        ],
    )


def delete_message(api: WebexAPI, message_id: str) -> None:
    api.messages.delete(message_id)


def extract_input_values(attachment_action) -> dict[str, Any]:
    return dict(getattr(attachment_action, "inputs", {}) or {})


def is_allowed_domain(email: str, allowed_domains: list[str]) -> bool:
    if not email or "@" not in email:
        return False
    domain = email.split("@", 1)[1].lower()
    return domain in {item.lower() for item in allowed_domains}
