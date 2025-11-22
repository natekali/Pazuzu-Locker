![banner](https://github.com/natekali/Pazuzu-Locker/assets/117448792/a530e303-9b3b-4c1d-87c9-290544ecb1c3)

# Pazuzu-Locker 👿

File encryption toolkit built with **Fernet** symmetric encryption. For each file, a **unique encryption key** is generated, making forensic analysis significantly more difficult. The manifest (CSV file containing file paths and keys) is uploaded to PixelDrain and removed locally. Decryption requires the PixelDrain **file ID**.

## ⛔️ Disclaimer 
This software is provided for **educational and security research purposes only**. I am **not responsible** for any misuse or damage caused by this tool. By using it, you agree to these terms and accept full responsibility for your actions.

## 🐉 Features

* **Modern Package Structure** - Clean `src/` layout with typed configuration  
* **Type-Hinted Codebase** - Full type annotations for better IDE support
* **Structured Logging** - JSON or text format with contextual fields
* **Flexible Configuration** - TOML files, environment variables, and CLI overrides  
* **Dry-Run Mode** - Simulate operations without modifying files
* **Include/Exclude Globs** - Fine-grained control over which files to process
* **Error Handling** - Graceful handling of permission and I/O errors

## ℹ️ Installation

**Requirements**: Python 3.10+

1. Clone this repository:
```bash
git clone https://github.com/natekali/Pazuzu-Locker.git
cd Pazuzu-Locker
```

2. Install in development mode:
```bash
pip install -e .
```

This will install all dependencies and make the `pazuzu` command available.

## 🛠️ Configuration

Configuration is managed via `config/pazuzu.toml`. You can also use environment variables (prefixed with `PAZUZU_`) or CLI arguments to override settings.

### Example Configuration

```toml
[pazuzu]
start_dir = "/path/to/target"
manifest_dir = "./manifests"
include_globs = ["**/*"]
exclude_globs = ["**/*.pazuzu", "**/.git/**"]
dry_run = true  # safe default to avoid accidental encryption
log_level = "INFO"
log_format = "json"

[pazuzu.provider]
name = "pixeldrain"
upload_endpoint = "https://pixeldrain.com/api/file"
download_endpoint = "https://pixeldrain.com/api/file/{id}"
```

### Environment Variables

Override any config value with environment variables:

```bash
export PAZUZU_START_DIR=/home/user/documents
export PAZUZU_LOG_LEVEL=DEBUG
export PAZUZU_DRY_RUN=true
```

## 🔐 Usage

### Package Entry Point

Test that the package loads correctly:

```bash
python -m pazuzu_locker --help
```

### Encrypt Files

```bash
pazuzu encrypt --start-dir /path/to/target
```

Or with configuration overrides:

```bash
pazuzu encrypt \
  --start-dir /path/to/target \
  --log-level DEBUG \
  --log-format text \
  --exclude "**/*.txt"
```

### Decrypt Files

Use the manifest ID returned from encryption:

```bash
pazuzu decrypt --manifest-id YOUR_MANIFEST_ID
```

Or set it in `config/pazuzu.toml` or via environment:

```bash
export PAZUZU_MANIFEST_ID=YOUR_MANIFEST_ID
pazuzu decrypt
```

### Dry Run

Test operations without modifying files:

```bash
pazuzu encrypt --start-dir /path/to/target --dry-run
```

## 📦 Package Structure

```
pazuzu-locker/
├── config/
│   └── pazuzu.toml          # Configuration file
├── src/
│   └── pazuzu_locker/       # Main package
│       ├── __init__.py      # Package exports
│       ├── __main__.py      # Module entry point
│       ├── cli.py           # Command-line interface
│       ├── config.py        # Configuration management
│       ├── crypto.py        # Encryption/decryption
│       ├── logging.py       # Structured logging
│       ├── manifest.py      # CSV manifest handling
│       ├── providers.py     # Remote storage providers
│       └── workflow.py      # Encryption/decryption workflows
├── pyproject.toml           # PEP 621 project metadata
└── README.md
```

## 🔍 Module Documentation

### `pazuzu_locker.config`
- `AppConfig` - Pydantic model for application configuration
- `ProviderConfig` - Configuration for remote storage providers
- `load_config()` - Load configuration from TOML, env vars, and overrides

### `pazuzu_locker.crypto`
- `generate_key()` - Generate a new Fernet encryption key
- `encrypt_data()` - Encrypt bytes using Fernet
- `decrypt_data()` - Decrypt bytes using Fernet

### `pazuzu_locker.manifest`
- `Manifest` - CSV-based manifest for file paths and keys
- `ManifestEntry` - Single entry in the manifest

### `pazuzu_locker.providers`
- `ManifestProvider` - Protocol for upload/download providers
- `PixelDrainProvider` - PixelDrain implementation
- `create_provider()` - Factory function for providers

### `pazuzu_locker.workflow`
- `encrypt_directory()` - Encrypt files and upload manifest
- `decrypt_from_manifest()` - Download manifest and decrypt files

### `pazuzu_locker.logging`
- `configure_logging()` - Set up structured logging
- `JsonFormatter` - JSON log formatter with context fields

## 🐝 VirusTotal Check
**Pazuzu Locker** can easily **bypass many antivirus solutions**, making it **easier** to deploy for security testing purposes.
![VT_check](https://github.com/natekali/Pazuzu-Locker/assets/117448792/d336c9b5-3cda-42d4-a506-093bc92cecbc)

## 💼 Author
* [@natekali](https://github.com/natekali)
