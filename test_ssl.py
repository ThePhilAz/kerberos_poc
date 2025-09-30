#!/usr/bin/env python3
"""
SSL Certificate Authentication Test

Simple test script that demonstrates SSL certificate authentication through a proxy.
Performs two tests:
1. Google Search API request (if configured)
2. Simple URL fetch test

Usage:
    python test_ssl.py --cert-path /path/to/cert.pem --key-path /path/to/key.pem
    python test_ssl.py --cert-path /path/to/cert.pem --key-path /path/to/key.pem --ca-bundle /path/to/ca.pem
    python test_ssl.py --cert-path /path/to/cert.pem --key-path /path/to/key.pem --debug
"""

import sys
import logging
import argparse
from kerberos_poc.proxy_client import ProxyClient
from kerberos_poc.auth_methods import SSLCertificateAuthentication
from kerberos_poc.config import (
    PROXY_HOST,
    PROXY_PORT,
    SSL_CERT_PATH,
    SSL_KEY_PATH,
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
        description="Test SSL certificate authentication through proxy"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--url", default=TEST_URL, help=f"URL to test (default: {TEST_URL})"
    )
    parser.add_argument(
        "--cert-path", help="Path to client certificate file (.pem/.crt)"
    )
    parser.add_argument("--key-path", help="Path to private key file (.key)")
    parser.add_argument(
        "--ca-bundle", help="Path to CA bundle file for server verification"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)

    # Get certificate paths from args or config
    cert_path = args.cert_path or SSL_CERT_PATH
    key_path = args.key_path or SSL_KEY_PATH
    ca_bundle_path = args.ca_bundle or SSL_CA_BUNDLE_PATH

    assert cert_path, (
        "Certificate path is required. Use --cert-path or set SSL_CERT_PATH in config."
    )
    # Note: key_path and ca_bundle_path are optional
    # CA bundle is now handled globally by ProxyClient

    # Print test header
    auth_details = {
        "Certificate": cert_path,
        "Private key": key_path if key_path else "Combined with certificate",
        "CA bundle": ca_bundle_path if ca_bundle_path else "System default (global)",
    }
    print_test_header(
        "🔒 SSL Certificate Authentication Test",
        auth_details,
        PROXY_HOST,
        PROXY_PORT,
        args.url,
    )

    client = None
    try:
        # Initialize SSL certificate authentication
        logger.info("🚀 Initializing SSL certificate authentication...")
        auth_method = SSLCertificateAuthentication(cert_path, key_path)
        client = ProxyClient(auth_method=auth_method)

        # Create authenticated session
        logger.info("🔐 Creating authenticated session...")
        client.create_authenticated_session()
        logger.info("✅ Authentication successful!")

        # Run the test suite
        return run_test_suite(client, args.url, "SSL Certificate")

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
