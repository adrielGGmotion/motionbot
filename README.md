# motionbot

**A lightweight, feature-centric Discord automation tool.**

---

## Overview

**motionbot** is an open-source Discord bot designed to provide specific utility features rather than broad server management. It is built with a philosophy of simplicity and modularity, intended primarily for local hosting and personal use cases.

This project prioritizes experimental features and rapid development over the stability required for critical infrastructure. As such, it does not include moderation tools or administrative safeguards.

## Project Philosophy

* **Feature-First:** Focused on delivering specific interactive utilities rather than general-purpose administration.
* **Local Execution:** Designed to be self-hosted by the user, ensuring data control and configuration flexibility.
* **Minimalist Core:** The codebase aims to remain lightweight, avoiding bloat associated with comprehensive management bots.

---

## Stability & Moderation

> **Important Notice Regarding Usage**

**motionbot** is **not** intended for server moderation or critical administrative tasks.

Users should be aware of the following:

1.  **No Moderation Features:** The bot does not process bans, kicks, or audit logs. This is a design choice to maintain focus on utility.
2.  **Stability:** As this software is in active development, users may experience unexpected termination or crashes. Relying on this bot for continuous uptime or server security is not recommended.
3.  **Forking:** While the core repository will not support moderation, the open-source nature of the project allows developers to fork and implement these features at their own risk.

---

## Getting Started

### Prerequisites

Ensure you have the necessary runtime environment installed for your operating system.

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/adrielGGmotion/motionbot.git](https://github.com/adrielGGmotion/motionbot.git)
    ```

2.  Navigate to the directory:
    ```bash
    cd motionbot
    ```

3.  Install dependencies:
    ```bash
    npm install
    ```

### Configuration

Rename `.env.example` to `.env` and insert your Discord Bot Token.

```env
DISCORD_TOKEN=YOUR_TOKEN_HERE
PREFIX=^
CLIENT_ID=YOUR_CLIENT_ID_HERE
GUILD_ID=YOUR_GUILD_ID_HERE
DASHBOARD_LAN_ACCESS=false
```