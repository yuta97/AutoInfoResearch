import feedparser
from utils import strip_html, truncate, batch_summarize, fetch_article_text, filter_by_interests
from interests import load_interests


HATENA_RSS_URL = "https://b.hatena.ne.jp/hotentry/it.rss"


def fetch_hatena_entries(limit: int = 5, candidate_count: int = 20) -> list[dict]:
    interests = load_interests()
    feed = feedparser.parse(HATENA_RSS_URL)
    candidates = []

    for entry in feed.entries[:candidate_count]:
        bookmark_count = 0
        for tag in entry.get("tags", []):
            if tag.get("scheme") == "https://b.hatena.ne.jp/":
                try:
                    bookmark_count = int(tag.get("term", 0))
                except ValueError:
                    pass

        candidates.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "bookmark_count": bookmark_count,
            "_rss_summary": entry.get("summary", ""),
            "summary": "",
        })

    # Filter by interests relevance before fetching full article content
    entries = filter_by_interests(candidates, interests, keep=limit, title_key="title")

    summarize_inputs = []
    for entry in entries:
        content = fetch_article_text(entry["link"])
        if not content:
            content = truncate(strip_html(entry.pop("_rss_summary", "")), 1000)
        else:
            entry.pop("_rss_summary", None)
        summarize_inputs.append({"title": entry["title"], "content": content})

    # Clean up temp field if not already removed
    for entry in entries:
        entry.pop("_rss_summary", None)

    summaries = batch_summarize(summarize_inputs, interests=interests)
    for entry, summary in zip(entries, summaries):
        entry["summary"] = summary

    return entries
