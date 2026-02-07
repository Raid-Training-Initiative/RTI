#!/usr/bin/env python3

import argparse
import os
import requests
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

def fetch_application_emojis(application_id: str, bot_token: str) -> List[dict]:
    """
    Fetch the list of emojis for the Discord application.
    """
    url = f"https://discord.com/api/v10/applications/{application_id}/emojis"
    headers = {"Authorization": f"Bot {bot_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch emoji list: {response.status_code} - {response.text}")
    return response.json().get("items", [])

def download_emoji_image(emoji: dict, output_dir: str) -> str:
    """
    Download an emoji image from its URL, save in output_dir, return filename.
    """
    name = emoji["name"]
    is_animated = emoji.get("animated", False)
    ext = "gif" if is_animated else "png"
    url = emoji.get("url")
    if not url:
        # Fallback for legacy emoji object structure
        emoji_id = emoji["id"]
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
    filename = f"{name}.{ext}"
    filepath = os.path.join(output_dir, filename)
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(resp.content)
        return filename
    else:
        raise Exception(f"Failed to download emoji image from {url}, code: {resp.status_code}")

def main():
    """
    CLI entry point: exports all application emojis to a directory.
    """
    parser = argparse.ArgumentParser(
        description="Export all emojis from a Discord application to a directory."
    )
    parser.add_argument(
        "bot_token",
        help="Discord bot token (keep secret!)"
    )
    parser.add_argument(
        "output_dir",
        help="Directory where exported emojis will be saved."
    )
    args = parser.parse_args()

    application_id = fetch_application_id(args.bot_token)
    print(f"Resolved application_id = {application_id}")
    emojis = fetch_application_emojis(application_id, args.bot_token)
    print(f"Emojis fetched: {len(emojis)}")

    os.makedirs(args.output_dir, exist_ok=True)
    exported = 0
    for emoji in emojis:
        try:
            filename = download_emoji_image(emoji, args.output_dir)
            print(f"[EXPORTED] {filename}")
            exported += 1
        except Exception as exc:
            print(f"[ERROR] Failed to export emoji '{emoji.get('name')}': {exc}")

    print(f"Export done. {exported} emoji images saved in: {args.output_dir}")

if __name__ == "__main__":
    main()
