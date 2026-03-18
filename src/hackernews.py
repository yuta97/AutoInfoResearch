import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import fetch_article_text, summarize_with_claude, filter_by_interests
from interests import load_interests


HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def fetch_hn_stories(limit: int = 5, candidate_count: int = 50) -> list[dict]:
    interests = load_interests()

    response = requests.get(HN_TOP_STORIES_URL, timeout=10)
    response.raise_for_status()
    story_ids = response.json()[:candidate_count]

    stories = []
    for story_id in story_ids:
        try:
            item_response = requests.get(
                HN_ITEM_URL.format(id=story_id), timeout=10
            )
            item_response.raise_for_status()
            item = item_response.json()
            if item and item.get("type") == "story":
                stories.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                    "summary": "",
                })
        except requests.RequestException:
            continue

    stories.sort(key=lambda x: x["score"], reverse=True)

    # Filter by interests relevance (from score-sorted candidates)
    top_stories = filter_by_interests(stories, interests, keep=limit, title_key="title")

    def _fetch_and_summarize(idx: int, story: dict) -> tuple[int, str]:
        content = fetch_article_text(story["url"])
        summary = summarize_with_claude(story["title"], content, interests)
        return idx, summary

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(_fetch_and_summarize, i, s)
            for i, s in enumerate(top_stories)
        ]
        for future in as_completed(futures):
            idx, summary = future.result()
            top_stories[idx]["summary"] = summary

    return top_stories
