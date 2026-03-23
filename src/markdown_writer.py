import os
from datetime import date


OUTPUT_DIR = "output"


def write_markdown(
    hatena_entries: list[dict],
    hn_stories: list[dict],
    target_date: date | None = None,
) -> str:
    if target_date is None:
        target_date = date.today()

    date_str = target_date.strftime("%Y-%m-%d")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{date_str}.md")

    lines = [
        f"# Daily Tech Research - {date_str}",
        "",
        "## はてなブックマーク 人気記事 (IT)",
        "",
        "| # | タイトル | ブックマーク数 |",
        "|---|---------|------------|",
    ]
    for i, entry in enumerate(hatena_entries, 1):
        title = entry["title"].replace("|", "\\|")
        summary = entry.get("summary", "").replace("|", "\\|").replace("\n", " ").replace("\r", "")
        cell = f"[{title}]({entry['link']})<br>{summary}" if summary else f"[{title}]({entry['link']})"
        lines.append(f"| {i} | {cell} | {entry['bookmark_count']} |")

    lines += [
        "",
        "## Hacker News Top Stories",
        "",
        "| # | Title | Score | Comments |",
        "|---|-------|-------|---------|",
    ]
    for i, story in enumerate(hn_stories, 1):
        title = story["title"].replace("|", "\\|")
        summary = story.get("summary", "").replace("|", "\\|").replace("\n", " ").replace("\r", "")
        cell = f"[{title}]({story['url']})<br>{summary}" if summary else f"[{title}]({story['url']})"
        lines.append(f"| {i} | {cell} | {story['score']} | {story['comments']} |")

    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path
