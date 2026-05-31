# CLAUDE.md — ha-tuya-home-core

Extends /home/alex/ha-projects/CLAUDE.md. Read that file first.

## This Repo's Role
Shared credential store and Tuya area registry for all sub-integrations.
Other integrations call `hass.data[DOMAIN][entry_id]` to get the coordinator.

## Checklist Additions
- [ ] config_flow must make a live Tuya API call to validate credentials before saving
- [ ] coordinator refresh interval is 1 hour — do not reduce this
- [ ] area map must be cached in coordinator.data, not fetched on demand
- [ ] `get_area_map()` must never call the Tuya API directly — use coordinator.data only
- [ ] On coordinator refresh failure: log warning, keep stale data, do not raise

## Key Interfaces Exposed to Sub-integrations
- `coordinator.data["areas"]`  → {device_id: area_name}
- `coordinator.data["devices"]` → full device list
- `coordinator.client`         → authenticated tinytuya.Cloud instance
