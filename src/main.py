import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Must run before importing modules that initialize API clients

from hatena import fetch_hatena_entries
from hackernews import fetch_hn_stories
from qiita import fetch_qiita_entries
from zenn import fetch_zenn_entries
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

    print("Fetching Qiita entries...")
    try:
        qiita_entries = fetch_qiita_entries()
        print(f"  -> {len(qiita_entries)} entries fetched")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch Qiita: {e}", file=sys.stderr)
        qiita_entries = []

    print("Fetching Zenn entries...")
    try:
        zenn_entries = fetch_zenn_entries()
        print(f"  -> {len(zenn_entries)} entries fetched")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch Zenn: {e}", file=sys.stderr)
        zenn_entries = []

    output_path = write_markdown(hatena_entries, hn_stories, qiita_entries, zenn_entries)
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
