import asyncio
import os
import sys
from unique_web_search.settings import env_settings
from httpx import AsyncClient
import argparse
from functools import partial


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

        return wrapper

    return decorator


@safe_run(success_msg="✅ URL Crawler Success", fail_msg="❌ URL Crawler Fail")
async def test_url_crawler(
    async_client: partial[AsyncClient], url: str = "https://www.google.com"
):
    async with async_client() as client:
        response = await client.get(url)
        # print(response.text)


@safe_run(success_msg="✅ Google Search Success", fail_msg="❌ Google Search Fail")
async def test_google_search(
    async_client: partial[AsyncClient], query: str = "test search"
):
    params = {
        "url": env_settings.google_search_api_endpoint,
        "params": {
            "q": query,
            "cx": env_settings.google_search_engine_id,
            "key": env_settings.google_search_api_key,
        },
    }

    async with async_client() as client:
        response = await client.get(**params)
    # print(response.json())


def test_set(
    async_client: partial[AsyncClient],
    url_to_fetch: str = "https://www.google.com",
    query: str = "What are the recent news about the stock market?",
):
    asyncio.run(test_url_crawler(async_client, url_to_fetch))
    asyncio.run(test_google_search(async_client, query))


if __name__ == "__main__":
    # INSERT_YOUR_CODE

    parser = argparse.ArgumentParser(
        description="Test unique web search proxy configs."
    )
    parser.add_argument(
        "--url", type=str, default="https://www.google.com", help="URL to fetch"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="What are the recent news about the stock market?",
        help="Google search query",
    )
    parser.add_argument(
        "--proxy_protocol",
        type=str,
        default="http",
        help="Proxy protocol (http or https)",
    )
    args = parser.parse_args()

    url_to_fetch = args.url
    query = args.query
    proxy_protocol = args.proxy_protocol

    for auth_method in ["none", "username_password", "ssl_tls"]:
        print(50 * "#")
        print(f"Testing {auth_method} with {proxy_protocol} proxy protocol")
        print(50 * "#")

        reload_modules()
        os.environ["PROXY_PROTOCOL"] = args.proxy_protocol
        os.environ["PROXY_AUTH_MODE"] = auth_method

        from unique_web_search.services.client.proxy_config import (
            async_client,
            env_settings,
        )

        test_set(async_client, url_to_fetch, query)

        print("\n")
