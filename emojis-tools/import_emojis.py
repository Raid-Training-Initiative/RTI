#!/usr/bin/env python3

import argparse
import os
import requests
import base64
from typing import List

def fetch_application_id(bot_token: str) -> str:
    """
    Fetch the current application's ID using the Discord API and bot token.
    """
    url = "https://discord.com/api/v10/oauth2/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch application ID: {response.status_code} - {response.text}")
    return response.json()["id"]

def fetch_existing_emojis(application_id: str, bot_token: str) -> List[str]:
    """
    Fetch the list of existing emoji names for the Discord application.
    """
    url = f"https://discord.com/api/v10/applications/{application_id}/emojis"
    headers = {"Authorization": f"Bot {bot_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch emoji list: {response.status_code} - {response.text}")
    return [e["name"] for e in response.json().get("items", [])]

def encode_image_to_datauri(image_path: str) -> str:
    """
    Encode an image file as a data URI.
    """
    ext = os.path.splitext(image_path)[1].lower()
    mimetype = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif"
    }.get(ext)
    if not mimetype:
        raise ValueError(f"Unsupported file type: {ext}")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mimetype};base64,{encoded}"

def is_name_already_taken_error(response: requests.Response) -> bool:
    """
    Returns True if the error is a duplicate emoji name error returned by Discord API.
    """
    try:
        if response.status_code == 400 or response.status_code == 50035:
            data = response.json()
            # Discord returns code 50035 and an error detail structure
            err = data.get("errors", {}).get("name", {}).get("_errors", [])
            for suberr in err:
                if suberr.get("code") == "APPLICATION_EMOJI_NAME_ALREADY_TAKEN":
                    return True
    except Exception:
        pass
    return False

def create_emoji(application_id: str, bot_token: str, emoji_name: str, image_data: str) -> str:
    """
    Creates an emoji in the Discord application.
    Returns 'ok' if created, 'skip' if already exists, otherwise raises exceptions.
    """
    url = f"https://discord.com/api/v10/applications/{application_id}/emojis"
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": emoji_name,
        "image": image_data
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in (201, 200):
        return "ok"
    if is_name_already_taken_error(response):
        return "skip"
    raise RuntimeError(
        f"Failed to create emoji '{emoji_name}': {response.status_code} - {response.text}"
    )

def main():
    """
    CLI entry point: imports all emojis in a given directory into a Discord application.
    """
    parser = argparse.ArgumentParser(
        description="Import all emojis from a directory into a Discord application (bot integration)."
    )
    parser.add_argument(
        "bot_token",
        help="Discord bot token (keep secret!)"
    )
    parser.add_argument(
        "emoji_dir",
        help="Directory containing emoji image files (PNG/JPG/GIF, file name is used as emoji name)."
    )
    args = parser.parse_args()

    application_id = fetch_application_id(args.bot_token)
    print(f"Resolved application_id = {application_id}")
    existing = set(fetch_existing_emojis(application_id, args.bot_token))
    print(f"Existing emoji names: {existing}")

    supported_exts = (".png", ".jpg", ".jpeg", ".gif")
    imported = 0
    skipped = 0

    for filename in os.listdir(args.emoji_dir):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in supported_exts:
            continue
        if name in existing:
            print(f"[SKIP] {name} - already exists in emoji list.")
            skipped += 1
            continue
        filepath = os.path.join(args.emoji_dir, filename)
        try:
            datauri = encode_image_to_datauri(filepath)
            result = create_emoji(application_id, args.bot_token, name, datauri)
            if result == "ok":
                print(f"[IMPORTED] '{name}' from {filename}")
                imported += 1
            elif result == "skip":
                print(f"[SKIP] {name} - name already exists (API).")
                skipped += 1
        except Exception as exc:
            print(f"[ERROR] Failed to import '{filename}': {exc}")

    print(f"Import done. {imported} uploaded, {skipped} skipped (already present).")

if __name__ == "__main__":
    main()
