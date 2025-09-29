"""
Test utilities for authentication testing

This module provides common test functions that can be reused across
different authentication method test files.
"""

import logging
from typing import Union
from kerberos_poc.config import (
    GOOGLE_SEARCH_API_KEY,
    GOOGLE_SEARCH_ENGINE_ID,
    GOOGLE_SEARCH_CONTEXT,
    GOOGLE_SEARCH_URL,
)

logger = logging.getLogger(__name__)


def test_google_search(client) -> bool:
    """
    Test Google Search API through the proxy

    Args:
        client: Authenticated proxy client instance

    Returns:
        bool: True if test passed, False if failed
    """
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        logger.warning("⚠️ Google Search API not configured - skipping search test")
        logger.info(
            "💡 Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID to enable search test"
        )
        return True

    try:
        logger.info("🔍 Testing Google Search API...")
        logger.info(f"Search URL: {GOOGLE_SEARCH_URL}")
        logger.info(f"Search query: {GOOGLE_SEARCH_CONTEXT}")

        # Google Custom Search API request
        params = {
            "key": GOOGLE_SEARCH_API_KEY,
            "cx": GOOGLE_SEARCH_ENGINE_ID,
            "q": GOOGLE_SEARCH_CONTEXT,
        }

        response = client.make_request(GOOGLE_SEARCH_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Google Search API test successful!")

            # Display search results information
            search_info = data.get("searchInformation", {})
            total_results = search_info.get("totalResults", "0")
            search_time = search_info.get("searchTime", "unknown")

            logger.info(f"📊 Found {total_results} results in {search_time} seconds")

            # Show first result if available
            items = data.get("items", [])
            if items:
                first_result = items[0]
                title = first_result.get("title", "No title")
                link = first_result.get("link", "No URL")
                snippet = first_result.get("snippet", "No description")

                logger.info(f"🔗 First result: {title}")
                logger.info(f"🌐 URL: {link}")
                logger.info(f"📝 Description: {snippet[:100]}...")
            else:
                logger.info("📭 No search results found")

            return True
        else:
            logger.error(f"❌ Google Search API test failed: {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        logger.error(f"❌ Google Search API test failed: {e}")
        return False


def test_url_fetch(client, url: str) -> bool:
    """
    Test simple URL fetch through the proxy

    Args:
        client: Authenticated proxy client instance
        url: URL to fetch

    Returns:
        bool: True if test passed, False if failed
    """
    try:
        logger.info(f"🌐 Testing URL fetch: {url}")

        response = client.make_request(url)

        if response.status_code == 200:
            logger.info("✅ URL fetch test successful!")
            logger.info(f"📄 Response length: {len(response.text)} characters")

            # Display response headers information
            content_type = response.headers.get("content-type", "unknown")
            server = response.headers.get("server", "unknown")

            logger.info(f"📋 Content type: {content_type}")
            logger.info(f"🖥️ Server: {server}")

            # Show response preview
            preview = response.text[:200].replace("\n", " ").replace("\r", "").strip()
            if len(response.text) > 200:
                preview += "..."

            logger.info(f"📄 Preview: {preview}")

            return True
        else:
            logger.error(f"❌ URL fetch test failed: {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        logger.error(f"❌ URL fetch test failed: {e}")
        return False


def run_test_suite(client, test_url: str, auth_method_name: str) -> int:
    """
    Run the complete test suite for an authentication method

    Args:
        client: Authenticated proxy client instance
        test_url: URL to use for the fetch test
        auth_method_name: Name of the authentication method for display

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger.info(f"🚀 Running test suite for {auth_method_name} authentication")

    # Run tests
    results = []

    # Test 1: Google Search API
    logger.info("\n" + "=" * 40)
    logger.info("TEST 1: Google Search API")
    logger.info("=" * 40)
    results.append(test_google_search(client))

    # Test 2: URL Fetch
    logger.info("\n" + "=" * 40)
    logger.info("TEST 2: URL Fetch")
    logger.info("=" * 40)
    results.append(test_url_fetch(client, test_url))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    passed = sum(results)
    total = len(results)

    logger.info(f"✅ Passed: {passed}/{total}")
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.info(f"❌ {total - passed} test(s) failed")
        return 1


def setup_logging(debug: bool = False) -> None:
    """
    Set up logging configuration for tests

    Args:
        debug: Enable debug logging if True
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(level)

    if debug:
        logger.debug("Debug logging enabled")


def print_test_header(
    title: str,
    auth_details: dict,
    proxy_host: str,
    proxy_port: Union[int, None],
    test_url: str,
) -> None:
    """
    Print a standardized test header

    Args:
        title: Test title
        auth_details: Dictionary of authentication details to display
        proxy_host: Proxy hostname
        proxy_port: Proxy port
        test_url: Test URL
    """
    logger.info("=" * 60)
    logger.info(title)
    logger.info("=" * 60)

    # Display authentication details
    for key, value in auth_details.items():
        if value:
            logger.info(f"{key}: {value}")

    logger.info(
        f"Proxy: {proxy_host}:{proxy_port if proxy_port is not None else 'N/A'}"
    )
    logger.info(f"Test URL: {test_url}")
    logger.info("=" * 60)
