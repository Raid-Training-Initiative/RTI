# Discord Emoji Synchronization Toolkit

This repository provides two robust Python scripts for **managing and synchronizing custom Discord emojis** when working with Discord bots, especially for teams who need to synchronize emoji assets and their usage between production and development environments.

## Overview / Workflow

The typical use case is:

1. **You have a folder containing your custom emoji image files.**
2. **You want to upload these emojis to a Discord (application) bot,** skipping existing ones.
3. **You want all emoji usages in code (e.g., in a TypeScript utility like `EmojiUtil.ts`) to refer to the correct emoji IDs** for your current bot or application.

This repository provides:

- **`export_emojis.py`:** Download all emoji images from your Discord application to a folder.
- **`import_emojis.py`:** Upload all emoji images from a folder to your Discord application, skipping already-existing names.
- **`remplace_emojis.py`:** Automatically replace all emoji IDs in your TypeScript (or other) source files with the IDs corresponding to your current bot/application.

## 1. `export_emojis.py` – Export All Application Emojis to Folder

### Purpose

Exports all custom emojis **from your Discord application** into a local directory:

- Downloads each emoji as `name.png` or `name.gif`.
- Useful for backup, migration, or synchronizing your emoji assets.

### Usage

```sh
python export_emojis.py <bot_token> <output_folder>
```

**Arguments:**

- `bot_token` – Your Discord bot token (keep secret)
- `output_folder` – The directory where all exported emoji images will be saved

**Example:**

```sh
python export_emojis.py "Bot xxxxx" ./MyEmojisBackup/
```

**Behavior:**

- Fetches the application ID dynamically.
- Downloads every emoji image from your app to the target folder.
- Images are named with their emoji name and appropriate extension.
- Prints summary of exported/failed assets.

**Notes & Limitations:**

- Only works for 'application' emojis (not guild/server emojis).
- Might not work for most bots, as Discord’s application emoji endpoint is rarely used outside special integrations.
- If your endpoint returns 404, check if you’re really using application-level emojis, or switch to a guild emoji export.

## 2. `import_emojis.py` – Bulk Import Your Emoji Assets

### Purpose

Uploads all PNG (or supported) files in a local `Emojis` (or any) folder to your Discord application:

- Skips files where the emoji name already exists on Discord.
- Handles API specifics and error codes for duplicate names (safe to run multiple times).
- Optionally logs skipped/added emojis.

### Usage

```sh
python import_emojis.py <bot_token> <emojis_folder>
```

**Arguments:**

- `bot_token` – Your Discord bot token (keep this private!)
- `emojis_folder` – Path to your emoji image folder. Each file should be named as the target emoji name.

**Example:**

```sh
python import_emojis.py "Bot xxxxx" ./Emojis/
```

**Notes:**

- Only new emojis (by name) will be uploaded. Existing names will be skipped.
- Supported formats: PNG, JPEG, GIF (use Discord's emoji requirements).
- Limitations: Discord may limit the total number of emojis per application.

## 3. `remplace_emojis.py` – Automatic ID Replacement in Source Files

### Purpose

Replaces all custom emoji usages (e.g., `<:SomeEmoji:12345678>`) in your TypeScript code (such as `EmojiUtil.ts`) with the _actual_ IDs from your own Discord application:

- Ensures your development or staging bot always uses the correct IDs, not those of production.
- Seamless for collaborators – simply drop your bot token, and the script does the rest.

### Usage

```sh
python remplace_emojis.py <bot_token> <src_file> [--dest <output_file>]
```

**Arguments:**

- `bot_token` – Your Discord bot token (never commit/log this!)
- `src_file` – The file where emoji IDs should be replaced (e.g., `EmojiUtil.ts`).
- `--dest <output_file>` _(optional)_ – If not specified, source will be overwritten.

**Example:**

```sh
python remplace_emojis.py "Bot xxxxx" EmojiUtil.ts --dest EmojiUtil.local.ts
```

**Behavior:**

- Will consult Discord's API, fetch the list of emojis owned by your bot, and rewrite all custom emoji usages accordingly.
- Unmatched emoji names will remain unchanged.

## Best Practices & Security

- **Do not commit your bot token** to any repository or share it.
- Always double-check before overwriting important source files.
- Use `.gitignore` to ignore intermediate copies (`*.local.ts`, etc.).
- If your emoji mapping changes, re-run both scripts to keep production and local in sync.

## Requirements

- Python 3.7+
- `requests` library (`pip install requests`)
