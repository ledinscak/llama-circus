#!/usr/bin/env python3
"""Hacker News Agent - Search and analyze HN stories using Ollama."""

import sys
import re
import argparse
import requests
from ollama import chat

# Default settings
num_results = 10
verbose = False

# Hacker News API base URL
HN_API = "https://hacker-news.firebaseio.com/v0"

# ANSI color codes
ESC = "\x1b["


class Colors:
    RESET = f"{ESC}0m"
    BOLD = f"{ESC}1m"
    DIM = f"{ESC}2m"
    ITALIC = f"{ESC}3m"
    UNDERLINE = f"{ESC}4m"
    RED = f"{ESC}31m"
    GREEN = f"{ESC}32m"
    YELLOW = f"{ESC}33m"
    BLUE = f"{ESC}34m"
    MAGENTA = f"{ESC}35m"
    CYAN = f"{ESC}36m"
    WHITE = f"{ESC}37m"
    BRIGHT_BLACK = f"{ESC}90m"
    BRIGHT_YELLOW = f"{ESC}93m"
    BRIGHT_CYAN = f"{ESC}96m"


def format_output(text: str) -> str:
    """Convert markdown-like syntax to ANSI escape codes."""
    C = Colors

    # Links: [text](url) -> bold text + cyan url
    def link_replace(m):
        return f"{C.BOLD}{m.group(1)}{C.RESET} {C.CYAN}{C.UNDERLINE}{m.group(2)}{C.RESET}"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_replace, text)

    # Bold: **text**
    text = re.sub(r"\*\*(.+?)\*\*", f"{C.BOLD}\\1{C.RESET}", text)

    # Headers
    text = re.sub(r"^(#{1,6})\s+(.+)$", f"{C.BOLD}{C.MAGENTA}\\2{C.RESET}", text, flags=re.MULTILINE)

    # Bullet points
    text = re.sub(r"^(\s*)-\s+", f"\\1{C.CYAN}•{C.RESET} ", text, flags=re.MULTILINE)

    # Numbered lists
    text = re.sub(r"^(\s*)(\d+)\.\s+", f"\\1{C.CYAN}\\2.{C.RESET} ", text, flags=re.MULTILINE)

    # Inline code
    text = re.sub(r"`([^`]+)`", f"{C.BRIGHT_YELLOW}\\1{C.RESET}", text)

    # URLs
    text = re.sub(r"(?<![(\[])(https?://[^\s)\]<>]+)", f"{C.CYAN}{C.UNDERLINE}\\1{C.RESET}", text)

    return text


def fetch_item(item_id: int) -> dict:
    """Fetch a single item from HN API."""
    try:
        response = requests.get(f"{HN_API}/item/{item_id}.json", timeout=10)
        response.raise_for_status()
        return response.json() or {}
    except Exception:
        return {}


def fetch_story_ids(endpoint: str) -> list:
    """Fetch story IDs from an endpoint."""
    try:
        response = requests.get(f"{HN_API}/{endpoint}.json", timeout=10)
        response.raise_for_status()
        return response.json() or []
    except Exception:
        return []


def format_story(item: dict, index: int) -> str:
    """Format a story item for display."""
    title = item.get("title", "No title")
    url = item.get("url", "")
    score = item.get("score", 0)
    author = item.get("by", "unknown")
    comments = item.get("descendants", 0)
    item_id = item.get("id", 0)
    hn_url = f"https://news.ycombinator.com/item?id={item_id}"

    result = f"[{index}] {title}\n"
    result += f"    Score: {score} | Comments: {comments} | By: {author}\n"
    if url:
        result += f"    URL: {url}\n"
    result += f"    HN: {hn_url}"
    return result


def get_top_stories(limit: int = 10) -> str:
    """Get top stories from Hacker News.

    Args:
        limit: Number of stories to fetch (max 30)

    Returns:
        Formatted list of top stories with scores and links
    """
    limit = min(limit, 30)
    if verbose:
        print(f"{Colors.DIM}[get_top_stories] Fetching {limit} stories...{Colors.RESET}")
        sys.stdout.flush()

    story_ids = fetch_story_ids("topstories")[:limit]
    stories = []

    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        if item:
            stories.append(format_story(item, i))

    if not stories:
        return "No top stories found."

    return "\n\n".join(stories)


def get_new_stories(limit: int = 10) -> str:
    """Get newest stories from Hacker News.

    Args:
        limit: Number of stories to fetch (max 30)

    Returns:
        Formatted list of new stories with scores and links
    """
    limit = min(limit, 30)
    if verbose:
        print(f"{Colors.DIM}[get_new_stories] Fetching {limit} stories...{Colors.RESET}")
        sys.stdout.flush()

    story_ids = fetch_story_ids("newstories")[:limit]
    stories = []

    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        if item:
            stories.append(format_story(item, i))

    if not stories:
        return "No new stories found."

    return "\n\n".join(stories)


def get_best_stories(limit: int = 10) -> str:
    """Get best stories from Hacker News (highest rated).

    Args:
        limit: Number of stories to fetch (max 30)

    Returns:
        Formatted list of best stories with scores and links
    """
    limit = min(limit, 30)
    if verbose:
        print(f"{Colors.DIM}[get_best_stories] Fetching {limit} stories...{Colors.RESET}")
        sys.stdout.flush()

    story_ids = fetch_story_ids("beststories")[:limit]
    stories = []

    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        if item:
            stories.append(format_story(item, i))

    if not stories:
        return "No best stories found."

    return "\n\n".join(stories)


def get_ask_hn(limit: int = 10) -> str:
    """Get Ask HN posts - questions from the community.

    Args:
        limit: Number of posts to fetch (max 30)

    Returns:
        Formatted list of Ask HN posts
    """
    limit = min(limit, 30)
    if verbose:
        print(f"{Colors.DIM}[get_ask_hn] Fetching {limit} posts...{Colors.RESET}")
        sys.stdout.flush()

    story_ids = fetch_story_ids("askstories")[:limit]
    stories = []

    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        if item:
            stories.append(format_story(item, i))

    if not stories:
        return "No Ask HN posts found."

    return "\n\n".join(stories)


def get_show_hn(limit: int = 10) -> str:
    """Get Show HN posts - projects and demos shared by the community.

    Args:
        limit: Number of posts to fetch (max 30)

    Returns:
        Formatted list of Show HN posts
    """
    limit = min(limit, 30)
    if verbose:
        print(f"{Colors.DIM}[get_show_hn] Fetching {limit} posts...{Colors.RESET}")
        sys.stdout.flush()

    story_ids = fetch_story_ids("showstories")[:limit]
    stories = []

    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        if item:
            stories.append(format_story(item, i))

    if not stories:
        return "No Show HN posts found."

    return "\n\n".join(stories)


def get_jobs(limit: int = 10) -> str:
    """Get job postings from Hacker News.

    Args:
        limit: Number of jobs to fetch (max 30)

    Returns:
        Formatted list of job postings
    """
    limit = min(limit, 30)
    if verbose:
        print(f"{Colors.DIM}[get_jobs] Fetching {limit} jobs...{Colors.RESET}")
        sys.stdout.flush()

    story_ids = fetch_story_ids("jobstories")[:limit]
    jobs = []

    for i, sid in enumerate(story_ids, 1):
        item = fetch_item(sid)
        if item:
            title = item.get("title", "No title")
            url = item.get("url", "")
            item_id = item.get("id", 0)
            hn_url = f"https://news.ycombinator.com/item?id={item_id}"

            result = f"[{i}] {title}\n"
            if url:
                result += f"    URL: {url}\n"
            result += f"    HN: {hn_url}"
            jobs.append(result)

    if not jobs:
        return "No job postings found."

    return "\n\n".join(jobs)


def get_story_details(story_id: int) -> str:
    """Get full details of a story including top comments.

    Args:
        story_id: The HN story ID

    Returns:
        Story details with title, text, and top comments
    """
    if verbose:
        print(f"{Colors.DIM}[get_story_details] Fetching story {story_id}...{Colors.RESET}")
        sys.stdout.flush()

    item = fetch_item(story_id)
    if not item:
        return f"Story {story_id} not found."

    title = item.get("title", "No title")
    url = item.get("url", "")
    text = item.get("text", "")
    score = item.get("score", 0)
    author = item.get("by", "unknown")
    comments_count = item.get("descendants", 0)
    kids = item.get("kids", [])[:5]  # Top 5 comments

    result = f"Title: {title}\n"
    result += f"Score: {score} | Comments: {comments_count} | By: {author}\n"
    if url:
        result += f"URL: {url}\n"
    if text:
        result += f"\nContent:\n{text}\n"

    if kids:
        result += f"\nTop Comments:\n"
        for kid_id in kids:
            comment = fetch_item(kid_id)
            if comment and comment.get("text"):
                comment_by = comment.get("by", "unknown")
                comment_text = comment.get("text", "")[:500]  # Truncate long comments
                result += f"\n[{comment_by}]: {comment_text}\n"

    return result


def search_stories(query: str, limit: int = 10) -> str:
    """Search for stories matching a query in top and best stories.

    Args:
        query: Search term to match in titles
        limit: Maximum number of results to return

    Returns:
        Formatted list of matching stories
    """
    query_lower = query.lower()
    if verbose:
        print(f"{Colors.DIM}[search_stories] Searching for '{query}'...{Colors.RESET}")
        sys.stdout.flush()

    # Search in top and best stories
    all_ids = set(fetch_story_ids("topstories")[:100])
    all_ids.update(fetch_story_ids("beststories")[:100])
    all_ids.update(fetch_story_ids("newstories")[:50])

    matches = []
    for sid in all_ids:
        if len(matches) >= limit:
            break
        item = fetch_item(sid)
        if item:
            title = item.get("title", "").lower()
            if query_lower in title:
                matches.append(item)

    if not matches:
        return f"No stories found matching '{query}'."

    stories = []
    for i, item in enumerate(matches[:limit], 1):
        stories.append(format_story(item, i))

    return "\n\n".join(stories)


# Tools available to the LLM
tools = [
    get_top_stories,
    get_new_stories,
    get_best_stories,
    get_ask_hn,
    get_show_hn,
    get_jobs,
    get_story_details,
    search_stories,
]

available_functions = {
    "get_top_stories": get_top_stories,
    "get_new_stories": get_new_stories,
    "get_best_stories": get_best_stories,
    "get_ask_hn": get_ask_hn,
    "get_show_hn": get_show_hn,
    "get_jobs": get_jobs,
    "get_story_details": get_story_details,
    "search_stories": search_stories,
}

# System prompt
SYSTEM_PROMPT = """You are a Hacker News research assistant that helps developers discover and understand trending tech content.

AVAILABLE TOOLS:
- get_top_stories(limit): Current trending stories
- get_new_stories(limit): Latest submissions
- get_best_stories(limit): Highest rated stories
- get_ask_hn(limit): Community questions and discussions
- get_show_hn(limit): Project showcases and demos
- get_jobs(limit): Job postings
- get_story_details(story_id): Full story with comments
- search_stories(query, limit): Search stories by keyword

RESPONSE FORMAT:
After gathering information, provide a detailed analysis with:

## Overview
Brief summary of what you found (2-3 sentences).

## Key Stories
For each relevant story, explain:
- **What it is**: Title and brief description
- **Why it matters**: Relevance to developers
- **How to apply it**: Practical applications or learnings
- **Link**: URL to the story

## Insights
- Common themes or trends you noticed
- Technologies or topics getting attention

## Project Ideas
Suggest 2-3 hobby project ideas inspired by the stories found. For each:
- Project name and description
- Technologies involved
- Learning outcomes

## Sources
List the HN discussion links for further reading.

GUIDELINES:
- Focus on developer-relevant content
- Explain technical concepts clearly
- Suggest practical applications
- Be specific about why things matter
- Include project ideas that build on the topics found
"""

# Argument parsing
parser = argparse.ArgumentParser(description="Search Hacker News and get AI-analyzed insights")
parser.add_argument("query", help="Your question or topic to explore")
parser.add_argument("-v", "--verbose", action="store_true", help="Show intermediate results")
parser.add_argument("-m", "--model", default="llama3.1:8b", help="Ollama model to use (default: llama3.1:8b)")
parser.add_argument("-n", "--num-results", type=int, default=10, help="Number of stories to fetch (default: 10)")
args = parser.parse_args()

user_input = args.query
verbose = args.verbose
model = args.model
num_results = args.num_results

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_input},
]

if verbose:
    print(f"{Colors.BOLD}{Colors.BLUE}[Model]{Colors.RESET} {Colors.BRIGHT_CYAN}{model}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}[Results]{Colors.RESET} {Colors.BRIGHT_CYAN}{num_results}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}[Query]{Colors.RESET} {Colors.WHITE}{user_input}{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

response = chat(model=model, messages=messages, tools=tools)
messages.append(response.message)

# Handle tool calls
while response.message.tool_calls:
    for call in response.message.tool_calls:
        if verbose:
            print(f"{Colors.BOLD}{Colors.YELLOW}[Tool Call]{Colors.RESET} {Colors.BRIGHT_YELLOW}{call.function.name}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}[Arguments]{Colors.RESET} {Colors.DIM}{call.function.arguments}{Colors.RESET}")
            print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

        func = available_functions.get(call.function.name)
        if func:
            # Inject num_results as limit if applicable
            args_dict = call.function.arguments.copy() if call.function.arguments else {}
            if "limit" in args_dict:
                args_dict["limit"] = min(args_dict["limit"], num_results)
            elif call.function.name not in ["get_story_details"]:
                args_dict["limit"] = num_results
            result = func(**args_dict)
        else:
            result = f"Unknown function: {call.function.name}"

        if verbose:
            print(f"{Colors.BOLD}{Colors.GREEN}[Tool Result]{Colors.RESET}")
            # Color the result
            colored = result
            colored = re.sub(r"^\[(\d+)\]", f"{Colors.BOLD}{Colors.YELLOW}[\\1]{Colors.RESET}", colored, flags=re.MULTILINE)
            colored = re.sub(r"(Score: \d+)", f"{Colors.GREEN}\\1{Colors.RESET}", colored)
            colored = re.sub(r"(Comments: \d+)", f"{Colors.BLUE}\\1{Colors.RESET}", colored)
            colored = re.sub(r"(https?://[^\s]+)", f"{Colors.CYAN}{Colors.UNDERLINE}\\1{Colors.RESET}", colored)
            print(colored)
            print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

        messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})

    response = chat(model=model, messages=messages, tools=tools)
    messages.append(response.message)

if verbose:
    print(f"{Colors.BOLD}{Colors.GREEN}[Final Answer]{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

print(format_output(response.message.content))
