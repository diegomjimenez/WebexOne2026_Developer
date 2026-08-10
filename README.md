# WebexOne 2026 Developer Lab Code

Sample Python code for **LAB-21122: Exploring the Webex Developer Ecosystem**.

Repository: [https://github.com/diegomjimenez/WebexOne2026_Developer](https://github.com/diegomjimenez/WebexOne2026_Developer)

## Setup

```bash
git clone https://github.com/diegomjimenez/WebexOne2026_Developer.git
cd WebexOne2026_Developer
python -m venv webexone2026
source webexone2026/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Repository layout

| Folder | Purpose |
| --- | --- |
| `03-bots/` | Bot exercises and shared WebSocket client |
| `04-serviceapps/` | Service App meeting scheduler sample |
| `06-usecases/` | Pagination, feedback, and device provisioning exercises |

## Lab mapping

| Lab guide section | Scripts |
| --- | --- |
| Lab 3 – Building a Bot | `03-bots/01_people.py` through `07_card_processing.py` |
| Lab 4 – Service App | `04-serviceapps/01_serviceapp.py` |
| Lab 5 – Use Cases | `06-usecases/01_pagination.py`, `02_feedback.py`, `03_device.py` |

### Lab 3 bot exercises

| File | Topic |
| --- | --- |
| `01_people.py` | Find people |
| `02_message.py` | Send a direct message |
| `03_rooms.py` | Create a room and add a member |
| `04_adaptivecard.py` | Send an Adaptive Card |
| `05_connect_bot.py` | Connect the bot over WebSocket |
| `06_custom_handler.py` | Create a custom handler |
| `07_card_processing.py` | Process Adaptive Card submissions |
| `websocket_client.py` | Shared WebSocket client |
| `bot_helpers.py` | Shared helper functions |

Run bot exercises from inside `03-bots/`.
