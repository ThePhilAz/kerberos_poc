#!/usr/bin/env python3
"""
Username/Password Authentication Test

Simple test script that demonstrates username/password authentication through a proxy.
Performs two tests:
1. Google Search API request (if configured)
2. Simple URL fetch test

Usage:
    python test_basic_auth.py --username myuser --password mypass
    python test_basic_auth.py --username myuser --password mypass --debug
    python test_basic_auth.py --username myuser --password mypass --url https://httpbin.org/basic-auth/myuser/mypass
"""

import sys
import logging
import argparse
import getpass
from kerberos_poc.proxy_client import ProxyClient
from kerberos_poc.auth_methods import UsernamePasswordAuthentication
from kerberos_poc.config import (
    PROXY_HOST,
    PROXY_PORT,
    AUTH_USERNAME,
    AUTH_PASSWORD,
    TEST_URL,
)
from test_utils import run_test_suite, setup_logging, print_test_header

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Test username/password authentication through proxy"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--url", default=TEST_URL, help=f"URL to test (default: {TEST_URL})"
    )
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument(
        "--password", help="Password for authentication (will prompt if not provided)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)

    # Get credentials from args or config
    username = args.username or AUTH_USERNAME
    password = args.password or AUTH_PASSWORD

    # Prompt for credentials if not provided
    if not username:
        username = input("Username: ")
    if not password:
        password = getpass.getpass("Password: ")

    if not username or not password:
        logger.error("❌ Both username and password are required")
        return 1

    # Print test header
    auth_details = {"Username": username}
    print_test_header(
        "👤 Username/Password Authentication Test",
        auth_details,
        PROXY_HOST,
        PROXY_PORT,
        args.url,
    )

    client = None
    try:
        # Initialize username/password authentication
        logger.info("🚀 Initializing username/password authentication...")
        auth_method = UsernamePasswordAuthentication(username, password)
        client = ProxyClient(auth_method=auth_method)

        # Create authenticated session
        logger.info("🔐 Creating authenticated session...")
        client.create_authenticated_session()
        logger.info("✅ Authentication successful!")

        # Run the test suite
        return run_test_suite(client, args.url, "Username/Password")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return 1

    finally:
        if client:
            client.close()
            logger.info("🧹 Cleanup completed")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
