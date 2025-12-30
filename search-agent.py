import sys
import re
import os
import argparse
import tempfile
import subprocess
import requests
from ollama import chat
from ddgs import DDGS


# Default number of results (can be overridden by -n flag)
num_results = 10

# ANSI color codes (using \x1b escape)
ESC = "\x1b["

class Colors:
    RESET = f"{ESC}0m"
    BOLD = f"{ESC}1m"
    DIM = f"{ESC}2m"
    ITALIC = f"{ESC}3m"
    UNDERLINE = f"{ESC}4m"

    # Foreground colors
    BLACK = f"{ESC}30m"
    RED = f"{ESC}31m"
    GREEN = f"{ESC}32m"
    YELLOW = f"{ESC}33m"
    BLUE = f"{ESC}34m"
    MAGENTA = f"{ESC}35m"
    CYAN = f"{ESC}36m"
    WHITE = f"{ESC}37m"

    # Bright foreground colors
    BRIGHT_BLACK = f"{ESC}90m"
    BRIGHT_RED = f"{ESC}91m"
    BRIGHT_GREEN = f"{ESC}92m"
    BRIGHT_YELLOW = f"{ESC}93m"
    BRIGHT_BLUE = f"{ESC}94m"
    BRIGHT_MAGENTA = f"{ESC}95m"
    BRIGHT_CYAN = f"{ESC}96m"
    BRIGHT_WHITE = f"{ESC}97m"


def format_output(text: str) -> str:
    """Convert markdown-like syntax to ANSI escape codes"""
    C = Colors  # shorthand

    # Links: [text](url) -> bold text + cyan url (no brackets)
    def link_replace(m):
        link_text = m.group(1)
        url = m.group(2)
        return f"{C.BOLD}{link_text}{C.RESET} {C.CYAN}{C.UNDERLINE}{url}{C.RESET}"
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_replace, text)

    # Remove any remaining standalone [ or ] that might be left over
    # (from malformed markdown links)

    # Bold: **text** or __text__
    def bold_replace(m):
        return f"{C.BOLD}{m.group(1)}{C.RESET}"
    text = re.sub(r'\*\*(.+?)\*\*', bold_replace, text)
    text = re.sub(r'__(.+?)__', bold_replace, text)

    # Headers: # Header (must be at start of line)
    def header_replace(m):
        return f"{C.BOLD}{C.MAGENTA}{m.group(2)}{C.RESET}"
    text = re.sub(r'^(#{1,6})\s+(.+)$', header_replace, text, flags=re.MULTILINE)

    # Bullet points (only dash)
    def bullet_replace(m):
        return f"{m.group(1)}{C.CYAN}•{C.RESET} "
    text = re.sub(r'^(\s*)-\s+', bullet_replace, text, flags=re.MULTILINE)

    # Numbered lists
    def number_replace(m):
        return f"{m.group(1)}{C.CYAN}{m.group(2)}.{C.RESET} "
    text = re.sub(r'^(\s*)(\d+)\.\s+', number_replace, text, flags=re.MULTILINE)

    # Inline code: `code`
    def code_replace(m):
        return f"{C.BRIGHT_YELLOW}{m.group(1)}{C.RESET}"
    text = re.sub(r'`([^`]+)`', code_replace, text)

    # Standalone URLs
    def url_replace(m):
        return f"{C.CYAN}{C.UNDERLINE}{m.group(0)}{C.RESET}"
    text = re.sub(r'(?<![(\[])(https?://[^\s)\]<>]+)', url_replace, text)

    # Clean up any leftover markdown artifacts
    text = re.sub(r'\[([^\]]+)\](?!\()', r'\1', text)  # [text] without (url)

    # Clean up any stray ANSI-like codes that might appear from LLM output
    # (e.g., literal "1m", "0m" without the escape prefix)
    text = re.sub(r'(?<!\x1b\[)(?<!\d)([0-9]{1,2})m(?=\s|[A-Z])', '', text)

    return text


def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return results

    Args:
      query: The search query

    Returns:
      Search results with titles, snippets and URLs
    """
    try:
        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=num_results), 1):
                title = r.get("title", "No title")
                body = r.get("body", "No description")
                url = r.get("href", "")
                results.append(f"[{i}] Title: {title}\nSnippet: {body}\nURL: {url}")

        if not results:
            return f"No results found for: {query}"

        return "\n\n".join(results)
    except Exception as e:
        return f"Error searching: {e}"


def news_search(query: str) -> str:
    """Search for recent news using DuckDuckGo

    Args:
      query: The search query

    Returns:
      News results with titles, snippets, dates and URLs
    """
    try:
        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.news(query, max_results=num_results), 1):
                title = r.get("title", "No title")
                body = r.get("body", "No description")
                date = r.get("date", "Unknown date")
                url = r.get("url", "")
                source = r.get("source", "Unknown source")
                results.append(f"[{i}] Title: {title}\nSource: {source}\nDate: {date}\nSnippet: {body}\nURL: {url}")

        if not results:
            return f"No news found for: {query}"

        return "\n\n".join(results)
    except Exception as e:
        return f"Error searching news: {e}"


def fetch_url(url: str) -> str:
    """Fetch content from a URL

    Args:
      url: The URL to fetch

    Returns:
      The text content from the URL (truncated)
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        # Return first 2000 chars to avoid overwhelming the LLM
        return response.text[:2000]
    except requests.RequestException as e:
        return f"Error fetching URL: {e}"


def image_search(query: str) -> str:
    """Search for images related to a query and display the first result in terminal using chafa

    Args:
      query: The search query for images

    Returns:
      Description of the displayed image
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=min(num_results, 5)))

        if not results:
            return f"No images found for: {query}"

        errors = []
        # Try to download and display the first working image
        for i, result in enumerate(results, 1):
            image_url = result.get("image", "")
            title = result.get("title", "No title")

            if not image_url:
                continue

            try:
                # Download the image with browser-like headers
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://duckduckgo.com/",
                }
                response = requests.get(
                    image_url,
                    timeout=10,
                    headers=headers,
                    stream=True
                )
                response.raise_for_status()

                # Get file extension from URL or content type
                content_type = response.headers.get("content-type", "")
                if "jpeg" in content_type or "jpg" in content_type:
                    ext = ".jpg"
                elif "png" in content_type:
                    ext = ".png"
                elif "gif" in content_type:
                    ext = ".gif"
                elif "webp" in content_type:
                    ext = ".webp"
                else:
                    ext = ".jpg"

                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp.write(chunk)
                    tmp_path = tmp.name

                # Display using chafa
                try:
                    result_output = subprocess.run(
                        ["chafa", "--size=60x30", "--colors=256", tmp_path],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result_output.returncode == 0:
                        print(f"\n{Colors.BOLD}{Colors.MAGENTA}[Image {i}: {title}]{Colors.RESET}")
                        print(f"{Colors.CYAN}{image_url}{Colors.RESET}\n")
                        print(result_output.stdout)
                        return f"Displayed image: {title} (URL: {image_url})"
                    else:
                        errors.append(f"[{i}] chafa error: {result_output.stderr}")
                except FileNotFoundError:
                    return "Error: chafa is not installed. Install with: sudo apt install chafa"
                except subprocess.TimeoutExpired:
                    errors.append(f"[{i}] chafa timeout")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            except requests.RequestException as e:
                errors.append(f"[{i}] download error: {e}")
                continue

        error_details = "; ".join(errors) if errors else "unknown error"
        return f"Could not display any images for: {query}. Errors: {error_details}"
    except Exception as e:
        return f"Error searching images: {e}"


tools = [web_search, news_search, fetch_url, image_search]
available_functions = {
    "web_search": web_search,
    "news_search": news_search,
    "fetch_url": fetch_url,
    "image_search": image_search,
}


# System prompts for different formats
BASE_PROMPT = """You are a research assistant that searches the web to answer questions accurately.

TOOL SELECTION:
- web_search: General knowledge, facts, how-to questions
- news_search: Current events, recent news, trending topics
- image_search: When user asks to see something, or to illustrate news stories
- fetch_url: Only if search snippets lack detail and you need the full page

GUIDELINES:
- Only state facts found in search results, never make up information
- If sources conflict, mention the disagreement
- If information seems outdated, note when it was published
- Use specific numbers, dates, names when available
"""

FORMAT_PROMPTS = {
    "brief": """
RESPONSE FORMAT:
- Give a direct, concise answer in 2-3 sentences maximum
- No bullet points, no headers, just the essential answer
- End with one most relevant source URL
""",
    "detailed": """
RESPONSE FORMAT:
1. Start with a direct answer (2-3 sentences)
2. Provide comprehensive details with context and background
3. Include relevant statistics, dates, and quotes when available
4. End with "Sources:" listing all URLs you used
""",
    "bullets": """
RESPONSE FORMAT:
1. One sentence summary at the top
2. Key facts as bullet points (5-8 bullets)
3. Each bullet should be one clear, standalone fact
4. End with "Sources:" listing the URLs you used
""",
    "all": """
RESPONSE FORMAT:
Create a comprehensive research report with the following sections:

## Summary
2-3 sentence executive summary answering the core question.

## Key Findings
Detailed bullet points of the most important facts discovered. Include specific numbers, dates, names, and quotes where available.

## Analysis
In-depth explanation and analysis of the findings:
- What does this information mean?
- How do different sources compare or contrast?
- What is the broader context?
- Are there any controversies or conflicting viewpoints?

## Background
Relevant historical context or background information that helps understand the topic better.

## Limitations
Note any gaps in the information, potential biases in sources, or areas where data was unclear or conflicting.

## Recommendations
Suggest 3-5 specific topics, questions, or search queries the user could explore next to deepen their understanding. Format as actionable items.

## Sources
List all URLs used with brief description of what each source provided.

GUIDELINES FOR THIS FORMAT:
- Be thorough and analytical, not just descriptive
- Connect dots between different pieces of information
- Highlight what's most significant and why
- Be honest about uncertainty or conflicting information
- Make recommendations specific and actionable
- IMPORTANT: Use image_search at least 2 times to find and display relevant images that illustrate the topic
""",
}

parser = argparse.ArgumentParser(description="Search the web and get AI-summarized answers")
parser.add_argument("query", help="The search query")
parser.add_argument("-v", "--verbose", action="store_true", help="Show intermediate results")
parser.add_argument("-m", "--model", default="llama3.1:8b", help="Ollama model to use (default: llama3.1:8b)")
parser.add_argument("-f", "--format", dest="output_format", choices=["brief", "detailed", "bullets", "all"],
                    default="bullets", help="Output format: brief, detailed, bullets, or all (default: bullets)")
parser.add_argument("-n", "--num-results", type=int, default=10, help="Number of search results to fetch (default: 10)")
args = parser.parse_args()

user_input = args.query
verbose = args.verbose
model = args.model
output_format = args.output_format
num_results = args.num_results  # overrides the default

system_prompt = BASE_PROMPT + FORMAT_PROMPTS[output_format]

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

if verbose:
    print(f"{Colors.BOLD}{Colors.BLUE}[Model]{Colors.RESET} {Colors.BRIGHT_CYAN}{model}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}[Format]{Colors.RESET} {Colors.BRIGHT_CYAN}{output_format}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}[Results]{Colors.RESET} {Colors.BRIGHT_CYAN}{num_results}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}[Query]{Colors.RESET} {Colors.WHITE}{user_input}{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

response = chat(model=model, messages=messages, tools=tools)

messages.append(response.message)

# Handle multiple tool calls if needed
while response.message.tool_calls:
    for call in response.message.tool_calls:
        if verbose:
            print(f"{Colors.BOLD}{Colors.YELLOW}[Tool Call]{Colors.RESET} {Colors.BRIGHT_YELLOW}{call.function.name}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}[Arguments]{Colors.RESET} {Colors.DIM}{call.function.arguments}{Colors.RESET}")
            print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

        func = available_functions.get(call.function.name)
        if func:
            result = func(**call.function.arguments)
        else:
            result = f"Unknown function: {call.function.name}"

        if verbose:
            print(f"{Colors.BOLD}{Colors.GREEN}[Tool Result]{Colors.RESET}")
            # Color the result parts
            colored_result = result
            # Enumerate numbers [1], [2], etc.
            colored_result = re.sub(r'^\[(\d+)\]', f'{Colors.BOLD}{Colors.YELLOW}[\\1]{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(Title:)', f'{Colors.BOLD}{Colors.MAGENTA}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(Snippet:)', f'{Colors.BRIGHT_BLACK}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(URL:)', f'{Colors.CYAN}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(Source:)', f'{Colors.YELLOW}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(Date:)', f'{Colors.BLUE}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(Displayed image:)', f'{Colors.BOLD}{Colors.GREEN}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'^(Could not display|Error|No images)', f'{Colors.RED}\\1{Colors.RESET}', colored_result, flags=re.MULTILINE)
            colored_result = re.sub(r'(https?://[^\s]+)', f'{Colors.CYAN}{Colors.UNDERLINE}\\1{Colors.RESET}', colored_result)
            print(colored_result)
            print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

        messages.append(
            {"role": "tool", "tool_name": call.function.name, "content": str(result)}
        )

    response = chat(model=model, messages=messages, tools=tools)
    messages.append(response.message)

if verbose:
    print(f"{Colors.BOLD}{Colors.GREEN}[Final Answer]{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")

print(format_output(response.message.content))
