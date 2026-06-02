# Tuya Home Core

Shared credential store for Tuya-based Home Assistant integrations.

Install this first. It authenticates with Tuya Cloud once and makes the
connection available to all companion integrations (Tuya Watering, Tuya Cameras).

## Prerequisites

- A Tuya IoT Platform account at https://iot.tuya.com
- An active Cloud project with **Smart Home** API access
- Your API Key (Access ID) and API Secret (Access Secret)

## Installation via HACS

1. In HACS → Integrations → Custom repositories, add `a000a999a/ha-tuya-home-core`
2. Install **Tuya Home Core**
3. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Tuya Home Core**
3. Enter your project label, API Key, API Secret, and select your region

| Field | Required | Description |
|-------|----------|-------------|
| Project label | No | Friendly name shown in companion integrations (e.g. "Main Home", "Wallis") |
| API Key | Yes | Access ID from iot.tuya.com project |
| API Secret | Yes | Access Secret from iot.tuya.com project |
| Region | Yes | eu / us / cn / in — must match your project's data centre |

## Multiple Tuya projects

The Tuya developer platform limits each project to **50 devices**. If your device count exceeds this, create additional projects on iot.tuya.com and add a separate **Tuya Home Core** entry for each one.

Each entry is fully independent — its own credentials, device list, and area map. Companion integrations (Tuya Cameras, Tuya Watering) each select which core entry to use, so you can have one camera integration per Tuya project running in parallel.

Give each entry a distinct **Project label** so companion integrations can tell them apart in the account selector.

## What it does

- Validates credentials on setup
- Fetches your Tuya device list and home/area assignments
- Refreshes every 14 days (configurable)
- Exposes the authenticated client to companion integrations

## Companion integrations

- [Tuya Watering](https://github.com/a000a999a/ha-tuya-watering)
- [Tuya Cameras](https://github.com/a000a999a/ha-tuya-cameras)
