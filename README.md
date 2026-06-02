# Tuya Home Core

Shared credential store for Tuya-based Home Assistant integrations.

Provides Tuya Cloud API access, device discovery and area mapping to companion
integrations (Tuya Cameras, Tuya Watering).

---

## Full setup guide

Tuya cameras in HA use two complementary systems. Both are needed.

| System | Provides | HA integration |
|---|---|---|
| **Tuya Hub** (SmartLife consumer API) | Live video streams · `camera.xxx` entities | Official **Tuya** integration |
| **Tuya Developer API** | SD card monitoring · MQTT motion alerts · Format SD | **Tuya Home Core** + **Tuya Cameras** |

### Step 1 — Register cameras in SmartLife

Using the SmartLife app on your phone:
1. Pair each camera to your Wi-Fi
2. Assign each camera to a **home** (e.g. "Brasil", "Wallis") — home names become area labels in HA
3. Repeat for each SmartLife account if cameras are split across accounts

### Step 2 — Add the official Tuya hub to HA

This provides `camera.xxx` stream entities for live video in the Lovelace camera cards.

1. **Settings → Devices & Services → Add Integration → Tuya**
2. Follow the QR code login flow for your SmartLife account
3. Repeat for each SmartLife account (one hub per account)

> If cameras appear in both the original and a new account, the second hub will log
> "already exists — ignoring" for those cameras. This is harmless.

### Step 3 — Create a Tuya Developer Platform project

At [iot.tuya.com](https://iot.tuya.com):

1. Create a Cloud project (or use an existing one)
2. Enable **Smart Home** API + **Device Status Notification** API
3. Under **Service API** → subscribe to **Device management** and **Device Status Change**
4. Under **Message Service** → enable MQTT and subscribe to motion BizCodes
5. Copy your **API Key** (Access ID) and **API Secret**
6. Max 50 devices per project — create one project per account/location

### Step 4 — Add Tuya Home Core in HA

1. **Settings → Devices & Services → Add Integration → Tuya Home Core**
2. Enter a **Project label** (e.g. "Main Home", "Wallis") — shown in companion integration selectors
3. Enter API Key, API Secret, Region (eu/us/cn/in)
4. Repeat for each developer project

### Step 5 — Add companion integrations

- **Tuya Cameras** → SD monitoring, MQTT motion alerts, Format SD buttons (one entry per Tuya Home Core entry)
- **Tuya Watering** → weather-based valve control

### Step 6 — Press Refresh All Cameras

From the **Overview → Home** view or **Cameras** view, press **Refresh All Cameras**:
- Pulls the updated device list from every Tuya project
- Creates SD usage, status, and Format SD Card entities for all cameras
- Fills in the picture-glance card entities in the Cameras dashboard view

---

## Prerequisites

- A Tuya IoT Platform account at [iot.tuya.com](https://iot.tuya.com)
- An active Cloud project with **Smart Home** API access
- Your API Key (Access ID) and API Secret

## Installation via HACS

1. In HACS → Integrations → Custom repositories, add `a000a999a/ha-tuya-home-core`
2. Install **Tuya Home Core** and restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration → Tuya Home Core**

## Configuration

| Field | Required | Description |
|-------|----------|-------------|
| Project label | No | Friendly name shown in companion integrations (e.g. "Main Home", "Wallis") |
| API Key | Yes | Access ID from iot.tuya.com project |
| API Secret | Yes | Access Secret from iot.tuya.com project |
| Region | Yes | eu / us / cn / in — must match your project's data centre |

To rename an existing entry: **Configure → fill in Project label → Save**. The title updates immediately.

## Multiple Tuya projects

The developer platform limits each project to **50 devices**. Add one Tuya Home Core entry per project. Each entry is fully independent with its own device list and area map.

## What it does

- Validates credentials on setup via a live API call
- Fetches your Tuya device list and home/area assignments
- Refreshes every 14 days (configurable); manual refresh button available
- Exposes the authenticated client to companion integrations via `hass.data`

## Companion integrations

- [Tuya Cameras](https://github.com/a000a999a/ha-tuya-cameras)
- [Tuya Watering](https://github.com/a000a999a/ha-tuya-watering)
