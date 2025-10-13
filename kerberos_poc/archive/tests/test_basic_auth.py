#!/usr/bin/env python3
"""
Username/Password PROXY Authentication Test

Simple test script that demonstrates username/password PROXY authentication.
Also supports "no authentication" mode. CA bundle is handled globally for all methods.
Performs two tests:
1. Google Search API request (if configured)
2. Simple URL fetch test

Usage:
    # Username/password PROXY authentication (credentials sent to proxy, not target)
    python test_basic_auth.py --username proxy_user --password proxy_pass
    python test_basic_auth.py --username proxy_user --password proxy_pass --debug

    # No authentication (just proxy connectivity with CA bundle)
    python test_basic_auth.py --no-auth --ca-bundle /path/to/ca-bundle.pem
    python test_basic_auth.py --no-auth  # Uses system default CA bundle

Note: CA bundle is applied globally by ProxyClient for SSL verification of proxy connections.
"""

import sys
import logging
import argparse
import getpass
from kerberos_poc.proxy_client import ProxyClient
from kerberos_poc.auth_methods import UsernamePasswordAuthentication, NoAuthentication
from kerberos_poc.config import (
    PROXY_HOST,
    PROXY_PORT,
    AUTH_USERNAME,
    AUTH_PASSWORD,
    SSL_CA_BUNDLE_PATH,
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
    parser.add_argument(
        "--ca-bundle", help="Path to CA bundle file for server verification"
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Skip username/password authentication, only use CA bundle verification",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)

    # CA bundle is now handled globally by ProxyClient, but show it in display
    ca_bundle_path = args.ca_bundle or SSL_CA_BUNDLE_PATH

    if args.no_auth:
        # No authentication mode
        auth_details = {
            "Authentication": "None",
            "CA Bundle": ca_bundle_path
            if ca_bundle_path
            else "System default (global)",
        }
        print_test_header(
            "🔓 No Authentication Test",
            auth_details,
            PROXY_HOST,
            PROXY_PORT,
            args.url,
        )
        auth_method = NoAuthentication()
        auth_name = "No Authentication"
    else:
        # Username/password PROXY authentication mode
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

        auth_details = {
            "Username": username,
            "Auth Type": "PROXY Basic Auth",
            "CA Bundle": ca_bundle_path
            if ca_bundle_path
            else "System default (global)",
        }
        print_test_header(
            "👤 Username/Password PROXY Authentication Test",
            auth_details,
            PROXY_HOST,
            PROXY_PORT,
            args.url,
        )
        auth_method = UsernamePasswordAuthentication(username, password)
        auth_name = "Username/Password PROXY Auth"

    client = None
    try:
        # Initialize authentication
        logger.info(f"🚀 Initializing {auth_name.lower()} authentication...")
        client = ProxyClient(auth_method=auth_method)

        # Create authenticated session
        logger.info("🔐 Creating authenticated session...")
        client.create_authenticated_session()
        logger.info("✅ Authentication successful!")

        # Run the test suite
        return run_test_suite(client, args.url, auth_name)

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
