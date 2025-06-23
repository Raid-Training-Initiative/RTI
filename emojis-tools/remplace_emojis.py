#!/usr/bin/env python3

import argparse
import re
import sys
from typing import Dict, List, Any
import requests

def fetch_application_id(bot_token: str) -> str:
    """
    Resolve the application (client) ID associated with the provided bot token.

    Args:
        bot_token (str): Discord Bot Token.

    Returns:
        str: Application ID.
    """
    url = "https://discord.com/api/v10/oauth2/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch application ID: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(1)
    return response.json()["id"]

def fetch_application_emojis(application_id: str, bot_token: str) -> List[Dict[str, Any]]:
    """
    Fetch all emojis for the specified Discord application.

    Args:
        application_id (str): Discord Application ID.
        bot_token (str): Discord Bot Token.

    Returns:
        List[Dict[str, Any]]: List of emoji dicts, each with 'name' and 'id'.
    """
    url = f"https://discord.com/api/v10/applications/{application_id}/emojis"
    headers = {"Authorization": f"Bot {bot_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch emojis: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(1)
    data = response.json()
    return data if isinstance(data, list) else data.get("items", [])

def build_emoji_map(emoji_list: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Build emoji name -> id mapping.

    Args:
        emoji_list (List[Dict[str, Any]]): Raw emoji objects.

    Returns:
        Dict[str, str]: {emoji_name: emoji_id}
    """
    return {item["name"]: item["id"] for item in emoji_list if "name" in item and "id" in item}

def replace_emojis_in_file(src_path: str, dest_path: str, emoji_map: Dict[str, str]) -> None:
    """
    Replace all <:name:id> in file with updated IDs according to emoji map.

    Args:
        src_path (str): Input file.
        dest_path (str): Output file.
        emoji_map (Dict[str, str]): Mapping {name: new_id}.
    """
    pattern = re.compile(r'<:([a-zA-Z0-9_]+):\d+>')
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    def repl(match):
        name = match.group(1)
        new_id = emoji_map.get(name)
        return f'<:{name}:{new_id}>' if new_id else match.group(0)

    new_content = pattern.sub(repl, content)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    """
    CLI entrypoint:
    - Requires bot_token and src_file,
    - Optional --dest <dest_file> flag (default: overwrite source file).

    Usage:
        python3 replace_emojis_api.py <bot_token> <src_file> [--dest <dest_file>]
    """
    parser = argparse.ArgumentParser(
        description="Update all Discord emoji IDs in a file using the actual emoji mapping (via bot_token, no App ID needed)."
    )
    parser.add_argument("bot_token", help="Discord Bot Token (keep secret!)")
    parser.add_argument("src_file", help="Source file to process (e.g., TypeScript file).")
    parser.add_argument(
        "--dest",
        dest="dest_file",
        default=None,
        help="Destination file (default: overwrite source file if not set)."
    )
    args = parser.parse_args()

    dest_file = args.dest_file if args.dest_file else args.src_file

    application_id = fetch_application_id(args.bot_token)
    emoji_list = fetch_application_emojis(application_id, args.bot_token)
    emoji_map = build_emoji_map(emoji_list)
    replace_emojis_in_file(args.src_file, dest_file, emoji_map)
    print(f"✅ Emoji IDs updated in {args.src_file} → {dest_file}")

if __name__ == "__main__":
    main()
