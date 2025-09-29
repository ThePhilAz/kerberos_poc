#!/usr/bin/env python3
"""
Kerberos Authentication Test

Simple test script that demonstrates Kerberos authentication through a proxy.
Performs two tests:
1. Google Search API request (if configured)
2. Simple URL fetch test

Usage:
    python test_kerberos.py
    python test_kerberos.py --debug
    python test_kerberos.py --url https://httpbin.org/get
"""

import sys
import logging
import argparse
from kerberos_poc.proxy_client import ProxyKerberosClient
from kerberos_poc.config import (
    PROXY_HOST,
    PROXY_PORT,
    KERBEROS_PRINCIPAL,
    TEST_URL,
    KEYTAB_FILE_PATH,
    KRB5_CONF_PATH,
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
        description="Test Kerberos authentication through proxy"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--url", default=TEST_URL, help=f"URL to test (default: {TEST_URL})"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)

    # Print test header
    auth_details = {"Principal": KERBEROS_PRINCIPAL}
    print_test_header(
        "🔐 Kerberos Authentication Test",
        auth_details,
        PROXY_HOST,
        PROXY_PORT,
        args.url,
    )

    client = None
    try:
        # Initialize Kerberos client
        logger.info("🚀 Initializing Kerberos client...")
        client = ProxyKerberosClient(
            KERBEROS_PRINCIPAL, KEYTAB_FILE_PATH, KRB5_CONF_PATH
        )

        # Create authenticated session
        logger.info("🔐 Creating authenticated session...")
        client.create_authenticated_session()
        logger.info("✅ Authentication successful!")

        # Run the test suite
        return run_test_suite(client, args.url, "Kerberos")

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
