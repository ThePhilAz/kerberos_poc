import asyncio
import sys
from pathlib import Path
import traceback
from kerberos_poc.unique_web_search.google import GoogleSearch
from kerberos_poc.unique_web_search.client import async_client
import argparse

SAVE_DIR = Path(__file__).parent / "logs"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

def url_to_filename(url: str) -> str:
    """
    Convert a URL into a safe filename by replacing unsafe characters.
    Strips scheme, replaces path/query separators, and limits length.
    """
    import re

    # Strip scheme (http[s]://)
    url_without_scheme = re.sub(r"^https?://", "", url)
    # Replace slashes, question mark, ampersand, etc. with underscores
    safe = re.sub(r"[\/\:\?\&\=\#\%]", "_", url_without_scheme)
    # Remove characters not suitable for filenames
    safe = re.sub(r"[^\w\-_.]", "_", safe)
    # Truncate if very long
    max_length = 100
    if len(safe) > max_length:
        safe = safe[:max_length]
    return safe



def reload_modules():
    """Force reload of settings and proxy_config modules to pick up new env vars."""
    modules_to_reload = [
        "unique_web_search.services.client.proxy_config",
        "unique_web_search.settings",
    ]
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            del sys.modules[module_name]


def safe_run(success_msg: str = "✅ Success", fail_msg: str = "❌ Fail"):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                print(success_msg)
                return result
            except Exception as e:
                print(f"{fail_msg}: {e}")
                traceback.print_exc()

        return wrapper

    return decorator


@safe_run(success_msg="✅ URL Crawler Success", fail_msg="❌ URL Crawler Fail")
async def test_url_crawler(
    url: str = "https://www.google.com",
    debug: bool = False,
):
    async with async_client() as client:
        response = await client.get(url)
    
    with open(SAVE_DIR / f"{url_to_filename(url)}.html", "w") as f:
        f.write(response.text)
    if debug:
        print(response.text)


@safe_run(success_msg="✅ Google Search Success", fail_msg="❌ Google Search Fail")
async def test_google_search(
    query: str = "test search",
    fetch_size: int = 10,
    debug: bool = False,
):
    google_search = GoogleSearch()
    await google_search.search(query, fetch_size, debug)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="uq_web",
        description="Unique Web Search CLI - Test proxy configs and web search functionality",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a URL through the proxy")
    fetch_parser.add_argument(
        "url",
        type=str,
        nargs="?",
        default="https://www.google.com",
        help="URL to fetch (default: https://www.google.com)",
    )
    fetch_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output to print response content",
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Perform a Google search through the proxy"
    )
    search_parser.add_argument(
        "query",
        type=str,
        nargs="?",
        default="What are the recent news about the stock market?",
        help="Search query (default: 'What are the recent news about the stock market?')",
    )
    search_parser.add_argument(
        "--fetch-size",
        type=int,
        default=10,
        help="Number of search results to fetch (default: 10)",
    )
    search_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output to print search results",
    )

    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == "fetch":
        print(f"🌐 Fetching URL: {args.url}")
        asyncio.run(test_url_crawler(url=args.url, debug=args.debug))
    elif args.command == "search":
        print(f"🔍 Searching for: '{args.query}'")
        asyncio.run(
            test_google_search(
                query=args.query, fetch_size=args.fetch_size, debug=args.debug
            )
        )


if __name__ == "__main__":
    main()
