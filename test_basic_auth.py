#!/usr/bin/env python3
"""
Username/Password Authentication Test

Simple test script that demonstrates username/password authentication through a proxy.
Also supports "no authentication" mode with custom CA bundle verification.
Performs two tests:
1. Google Search API request (if configured)
2. Simple URL fetch test

Usage:
    # Username/password authentication
    python test_basic_auth.py --username myuser --password mypass
    python test_basic_auth.py --username myuser --password mypass --debug
    python test_basic_auth.py --username myuser --password mypass --url https://httpbin.org/basic-auth/myuser/mypass
    
    # No authentication with CA bundle verification
    python test_basic_auth.py --no-auth --ca-bundle /path/to/ca-bundle.pem
    python test_basic_auth.py --no-auth  # Uses system default CA bundle
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
        "--no-auth", action="store_true", 
        help="Skip username/password authentication, only use CA bundle verification"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)

    # Get CA bundle path
    ca_bundle_path = args.ca_bundle or SSL_CA_BUNDLE_PATH

    if args.no_auth:
        # No authentication mode - just CA bundle verification
        auth_details = {
            "Authentication": "None (CA Bundle verification only)",
            "CA Bundle": ca_bundle_path if ca_bundle_path else "System default"
        }
        print_test_header(
            "🔓 No Authentication Test (CA Bundle Verification)",
            auth_details,
            PROXY_HOST,
            PROXY_PORT,
            args.url,
        )
        auth_method = NoAuthentication(ca_bundle_path)
        auth_name = "No Authentication"
    else:
        # Username/password authentication mode
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
            "CA Bundle": ca_bundle_path if ca_bundle_path else "System default"
        }
        print_test_header(
            "👤 Username/Password Authentication Test",
            auth_details,
            PROXY_HOST,
            PROXY_PORT,
            args.url,
        )
        auth_method = UsernamePasswordAuthentication(username, password)
        auth_name = "Username/Password"

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
