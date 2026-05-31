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
3. Enter your API Key, API Secret, and select your region

| Field   | Description |
|---------|-------------|
| API Key | Access ID from iot.tuya.com project |
| API Secret | Access Secret from iot.tuya.com project |
| Region | eu / us / cn / in — must match your project's data centre |

## What it does

- Validates credentials on setup
- Fetches your Tuya device list and home/area assignments
- Refreshes every 60 minutes
- Exposes the authenticated client to companion integrations

## Companion integrations

- [Tuya Watering](https://github.com/a000a999a/ha-tuya-watering)
- [Tuya Cameras](https://github.com/a000a999a/ha-tuya-cameras)
