import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Must run before importing modules that initialize API clients

from hatena import fetch_hatena_entries
from hackernews import fetch_hn_stories
from markdown_writer import write_markdown


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY is not set. Summaries will be empty.", file=sys.stderr)
        print("  Set it with: export ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)

    print("Fetching はてなブックマーク entries...")
    try:
        hatena_entries = fetch_hatena_entries()
        print(f"  -> {len(hatena_entries)} entries fetched")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch Hatena: {e}", file=sys.stderr)
        hatena_entries = []

    print("Fetching Hacker News stories...")
    try:
        hn_stories = fetch_hn_stories()
        print(f"  -> {len(hn_stories)} stories fetched")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch HN: {e}", file=sys.stderr)
        hn_stories = []

    output_path = write_markdown(hatena_entries, hn_stories)
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
