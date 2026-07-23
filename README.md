# autoupdate

Cross-platform application auto-updater for Python applications on Windows, macOS, and Linux.

## Installation

```bash
pip install autoupdate
```

## Usage

```python
from autoupdate.autoupdate import perform_update

perform_update(
    endpoint="https://example.com/update-check",
    current_version="1.0.0",
    app_name="MyApp",
    update_available_callback=on_update_available,
    progress_callback=on_download_progress,
    update_complete_callback=on_complete
)
```

### Endpoint Format

Your update endpoint must return JSON with this structure:

```json
{
  "current_version": "1.0.1",
  "description": "Bug fixes and improvements",
  "downloads": {
    "Windows": "https://example.com/myapp-windows.zip",
    "Darwin": "https://example.com/myapp-macos.zip",
    "Linux": "https://example.com/myapp-linux.zip"
  }
}
```

### Update Package Structure

Updates are distributed as ZIP files containing:
- Your application files
- A platform-specific bootstrapper (`bootstrap.exe`, `bootstrap-mac.sh`, or `bootstrap-lin.sh`)

The bootstrapper:
1. Waits for the current process to exit
2. Replaces old files with new ones
3. Restarts the application

### Callbacks

**update_available_callback(version, description)**
- Called when a new version is found
- Return `False` to cancel the update

**progress_callback(downloaded, total)**
- Called during download with bytes downloaded and total size

**update_complete_callback()**
- Called after update is prepared and ready to install

### Password-Protected Updates

```python
perform_update(
    endpoint="https://example.com/update-check",
    current_version="1.0.0",
    password=b"secret"
)
```

## Development

```bash
# Install dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run ruff format

# Type checking
uv run pyright

# Build wheel and source distribution
uv build
```

## License

MIT
