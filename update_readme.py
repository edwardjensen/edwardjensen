#!/usr/bin/env python3
"""
Fetches recent blog posts from edwardjensen.net JSON feed
and updates the README.md with the latest entries.
"""

import os
import re
import urllib.request
import json
from datetime import datetime

FEED_URL = os.environ.get("SITE_JSON_FEED", "https://www.edwardjensen.net/feed.json")
README_PATH = "README.md"
MAX_POSTS = 5


def fetch_feed():
    """Fetch and parse the JSON feed."""
    request = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": "GitHub-Actions-README-Updater/1.0"}
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def format_date(date_string):
    """Convert ISO date string to 'd MMMM yyyy' format (e.g., '26 December 2025')."""
    dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
    return dt.strftime("%-d %B %Y")


def generate_posts_markdown(items, max_posts=MAX_POSTS):
    """Generate markdown list of recent posts."""
    entries = []
    for item in items[:max_posts]:
        title = item["title"].upper()
        url = item["url"]
        date = format_date(item["date_published"])
        excerpt = item.get("post_excerpt", "")
        
        entry = f"**[{title}]({url}) ({date})**"
        if excerpt:
            entry += f"\n_{excerpt}_"
        
        entries.append(entry)
    
    return "\n\n".join(entries)


def update_readme(posts_markdown):
    """Replace content between BLOG-POSTS markers in README."""
    with open(README_PATH, "r") as f:
        content = f.read()

    pattern = r"(<!-- BLOG-POSTS:START -->).*?(<!-- BLOG-POSTS:END -->)"
    replacement = f"\\1\n{posts_markdown}\n\\2"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(README_PATH, "w") as f:
        f.write(new_content)


def main():
    feed = fetch_feed()
    items = feed.get("items", [])
    
    if not items:
        print("No items found in feed.")
        return

    posts_markdown = generate_posts_markdown(items)
    update_readme(posts_markdown)
    print(f"Updated README with {min(len(items), MAX_POSTS)} posts.")


if __name__ == "__main__":
    main()