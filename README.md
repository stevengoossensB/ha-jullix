# Jullix for Home Assistant

[![Maintainer](https://img.shields.io/badge/maintainer-stevengoossensB-green?style=for-the-badge&logo=github)](https://github.com/stevengoossensB)
[![MIT License](https://img.shields.io/github/license/stevengoossensB/jullix?style=flat-square)](https://github.com/stevengoossensB/jullix/blob/main/LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)
[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=stevengoossensB&repository=jullix&category=integration)
[![Validation Status](https://github.com/stevengoossensB/jullix/actions/workflows/validate.yml/badge.svg)](https://github.com/stevengoossensB/jullix/actions/workflows/validate.yml)

[Jullix](https://jullix.com) is an energy management platform that exposes local REST endpoints for meter, solar, battery, charger and plug telemetry.

This custom integration imports that data into Home Assistant as sensors and updates it on a fixed polling interval.

## Features

- Config flow setup from **Settings → Devices & Services**
- Local polling of Jullix endpoints (`/api/ems/*`)
- Automatic sensor creation for:
  - meter
  - solar
  - battery
  - charger
  - plug
- Entity metadata (units, classes, state classes) from integration sensor mappings

## Installation

### HACS (recommended)

1. Open HACS → **Integrations** → **⋮** → **Custom repositories**
2. Add `https://github.com/stevengoossensB/jullix` as category **Integration**
3. Install **Jullix**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/jullix` to `config/custom_components/jullix`
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Jullix**
4. Enter the Jullix host (default: `http://jullix.local`)

## Entities overview

The integration dynamically flattens values from Jullix payloads and creates sensors for detected keys.

Common examples include:

- Meter: power, energy counters, voltage, gas/water values, CAPTAR values
- Solar: power and produced energy
- Battery: power, charged/discharged energy, battery voltage, battery SOC

## Troubleshooting

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.jullix: debug
```

If no entities appear:

- verify Home Assistant can reach your host URL
- confirm the Jullix API responds on `/api/ems/meter`
- reconfigure the integration if host details changed

## Developer notes

- Integration code lives in `custom_components/jullix`
- Metadata for Home Assistant is in `custom_components/jullix/manifest.json`
- HACS metadata is in `hacs.json`

## License

This project is licensed under the [MIT License](LICENSE).
