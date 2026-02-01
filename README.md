# motionbot

**A lightweight, feature-centric Discord automation tool, now rewritten in Python.**

---

## Overview

**motionbot** is an open-source Discord bot designed to provide specific utility features rather than broad server management. It is built with a philosophy of simplicity and modularity, intended primarily for local hosting and personal use cases.

The project has recently been migrated from Node.js to **Python (discord.py)** for better performance, lower configuration overhead, and deeper integration with modern asynchronous web frameworks like **Quart**.

## Key Features

*   **Interactive GSMArena Lookup:** Search for devices and view detailed specifications with custom Discord components (Select Menus & Buttons).
*   **Web Dashboard:** A built-in asynchronous dashboard (Quart) to manage bot stats, themes, and per-server command toggles.
*   **Sticky Messages:** Keep important messages at the bottom of channels with automatic cleanup and file-based persistence.
*   **Localization Support:** Easy-to-manage language files with support for custom string overrides.
*   **Custom Theming:** Define your own primary, accent, and error colors that apply across all bot embeds.

---

## Stability & Moderation

> **Important Notice Regarding Usage**

**motionbot** is **not** intended for server moderation or critical administrative tasks.

1.  **No Moderation Features:** The bot does not process bans, kicks, or audit logs. This is a design choice to maintain focus on utility.
2.  **Stability:** While the Python rewrite improves resource handling, the software is still in active development. Relying on this bot for continuous uptime or server security is not recommended.

---

## Getting Started

### Prerequisites

*   Python 3.10 or higher
*   Pip (Python Package Installer)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/adrielGGmotion/motionbot.git
    cd motionbot
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate    # Windows
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Rename `.env.example` to `.env` and insert your Discord Bot Token and Client ID.

```env
DISCORD_TOKEN=YOUR_TOKEN_HERE
CLIENT_ID=YOUR_CLIENT_ID_HERE
GUILD_ID=YOUR_GUILD_ID_HERE # Optional for development
DASHBOARD_LAN_ACCESS=false
GSM_BASE_URL=https://your-gsm-api.com
GSM_KEEP_ALIVE=true
```

## Running the Bot

Once configured, simply run the entry point:

```bash
python3 main.py
```

The web dashboard will be available at `http://localhost:3000` (or the configured port).