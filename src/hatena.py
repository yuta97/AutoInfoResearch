import feedparser
from utils import strip_html, truncate, batch_summarize, fetch_article_text


HATENA_RSS_URL = "https://b.hatena.ne.jp/hotentry/it.rss"


def fetch_hatena_entries(limit: int = 5) -> list[dict]:
    feed = feedparser.parse(HATENA_RSS_URL)
    entries = []
    summarize_inputs = []

    for entry in feed.entries[:limit]:
        bookmark_count = 0
        for tag in entry.get("tags", []):
            if tag.get("scheme") == "https://b.hatena.ne.jp/":
                try:
                    bookmark_count = int(tag.get("term", 0))
                except ValueError:
                    pass

        title = entry.get("title", "")
        link = entry.get("link", "")
        # Fetch actual article content from the URL
        content = fetch_article_text(link)
        # Fall back to RSS description if article fetch failed
        if not content:
            content = truncate(strip_html(entry.get("summary", "")), 1000)

        entries.append({
            "title": title,
            "link": link,
            "bookmark_count": bookmark_count,
            "summary": "",
        })
        summarize_inputs.append({"title": title, "content": content})

    summaries = batch_summarize(summarize_inputs)
    for entry, summary in zip(entries, summaries):
        entry["summary"] = summary

    return entries
