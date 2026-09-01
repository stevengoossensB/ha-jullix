# Contributing

Thanks for your interest in improving this integration.

## Development setup

1. Clone this repository.
2. Copy `custom_components/jullix` into a Home Assistant test instance under `config/custom_components/`.
3. Enable debug logging if needed:

```yaml
logger:
  logs:
    custom_components.jullix: debug
```

## Pull requests

- Keep changes focused and small.
- Update documentation when behavior or setup changes.
- Make sure Home Assistant can start and the integration loads without errors.
