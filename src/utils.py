import re
import requests
import anthropic
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed

_client = anthropic.Anthropic()


class _TagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts)


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.description: str = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta" or self.description:
            return
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        name = attr_dict.get("name", "").lower()
        prop = attr_dict.get("property", "").lower()
        if name in ("description",) or prop in ("og:description",):
            self.description = attr_dict.get("content", "")


def strip_html(text: str) -> str:
    parser = _TagStripper()
    parser.feed(text)
    return re.sub(r"\s+", " ", parser.get_text()).strip()


def truncate(text: str, length: int = 2000) -> str:
    text = text.strip()
    return text[:length] if len(text) > length else text


def fetch_article_text(url: str, timeout: int = 5) -> str:
    """Fetch article page and return text content for summarization."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; AutoInfoResearch/1.0)"}
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        if "html" not in resp.headers.get("content-type", ""):
            return ""
        html = resp.text
        # Extract meta description
        meta_parser = _MetaParser()
        meta_parser.feed(html[:15000])
        meta_desc = strip_html(meta_parser.description)
        # Extract body text
        body_text = strip_html(html[:50000])
        content = (meta_desc + "\n" + body_text).strip() if meta_desc else body_text
        return truncate(content, 2000)
    except Exception:
        return ""


def summarize_with_claude(title: str, content: str) -> str:
    """Summarize article using Claude API. Returns 100-300 char summary."""
    if not title and not content:
        return ""
    prompt = (
        "以下の記事を100〜300文字で簡潔に要約してください。要約文のみを返してください。\n\n"
        f"タイトル: {title}\n"
        f"内容: {content or '（本文なし）'}"
    )
    try:
        response = _client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        import sys
        print(f"  [WARN] summarize_with_claude failed: {e}", file=sys.stderr)
        return ""


def batch_summarize(items: list[dict], max_workers: int = 10) -> list[str]:
    """Summarize a list of {"title": ..., "content": ...} in parallel."""
    results = [""] * len(items)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(summarize_with_claude, item["title"], item.get("content", "")): i
            for i, item in enumerate(items)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            results[idx] = future.result()
    return results
