# Jullix for Home Assistant

[![Maintainer](https://img.shields.io/badge/maintainer-stevengoossensB-green?style=for-the-badge&logo=github)](https://github.com/stevengoossensB)

[![MIT License](https://img.shields.io/github/license/stevengoossensB/jullix?style=flat-square)](https://github.com/stevengoossensB/jullix/blob/main/LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)

[![GitHub Issues](https://img.shields.io/github/issues/stevengoossensB/ha-jullix)](https://github.com/stevengoossensB/ha-jullix/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/stevengoossensB/ha-jullix/pulls)


[![Validation Status](https://github.com/stevengoossensB/jullix/actions/workflows/validate.yml/badge.svg)](https://github.com/stevengoossensB/jullix/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://github.com/stevengoossensB/ha-idm/search?l=python)
[![Latest Release](https://img.shields.io/github/v/release/stevengoossensB/ha-jullix?logo=github)](https://github.com/stevengoossensB/ha-jullix/releases)
[![Last Commit](https://img.shields.io/github/last-commit/stevengoossensB/ha-jullix)](https://github.com/stevengoossensB/ha-jullix/commits)

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&slug=stevengoossens&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff)](https://coff.ee/stevengoossens)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=stevengoossensB&repository=jullix&category=Integration)

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
- HACS brand assets are stored in `custom_components/jullix/brand/icon.png`
- GitHub repository description and repository topics must be set in GitHub repository settings for HACS repository validation

## License

This project is licensed under the [MIT License](LICENSE).
