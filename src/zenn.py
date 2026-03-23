import feedparser
from utils import strip_html, truncate, batch_summarize, fetch_article_text, filter_by_interests
from interests import load_interests


ZENN_RSS_URL = "https://zenn.dev/feed"


def fetch_zenn_entries(limit: int = 5, candidate_count: int = 20) -> list[dict]:
    interests = load_interests()
    feed = feedparser.parse(ZENN_RSS_URL)
    candidates = []

    for entry in feed.entries[:candidate_count]:
        candidates.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "_rss_summary": entry.get("summary", ""),
            "summary": "",
        })

    entries = filter_by_interests(candidates, interests, keep=limit, title_key="title")

    summarize_inputs = []
    for entry in entries:
        content = fetch_article_text(entry["link"])
        if not content:
            content = truncate(strip_html(entry.pop("_rss_summary", "")), 1000)
        else:
            entry.pop("_rss_summary", None)
        summarize_inputs.append({"title": entry["title"], "content": content})

    for entry in entries:
        entry.pop("_rss_summary", None)

    summaries = batch_summarize(summarize_inputs, interests=interests)
    for entry, summary in zip(entries, summaries):
        entry["summary"] = summary

    return entries
