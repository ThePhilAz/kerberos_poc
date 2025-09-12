#!/usr/bin/env python3
"""
Kerberos Authentication Tester - Python Version
Replicates the functionality of the Java ProxyKerberosTester

This script tests Kerberos authentication through a proxy server
by attempting to authenticate with the configured Kerberos realm
and making a test HTTP request.
"""

import sys
import logging
import argparse
from kerberos_poc.proxy_client import ProxyKerberosClient
from kerberos_poc.config import TEST_URL, PROXY_HOST, PROXY_PORT, KERBEROS_PRINCIPAL, KRB5_CONF_PATH, KEYTAB_FILE_PATH, APPLICATION_NAME
from kerberos_poc.kerberos_service import KerberosService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("kerberos_test.log"),
    ],
)

logger = logging.getLogger(__name__)


def simulate_dry_run(args):
    """
    Simulate the execution without real authentication
    Useful for testing the script logic without Kerberos infrastructure
    """
    import time
    import os

    logger.info("🧪 DRY RUN MODE - Simulating execution")
    logger.info("-" * 40)

    # Simulate file checks
    logger.info("📁 Checking configuration files...")
    time.sleep(0.5)

    config_files = [
        (KRB5_CONF_PATH, "Kerberos configuration"),
        (KEYTAB_FILE_PATH, "Service keytab"),
        ("config.py", "Python configuration"),
    ]

    for filename, description in config_files:
        if os.path.exists(filename) or os.path.exists(f"kerberos_poc/{filename}"):
            logger.info(f"✅ Found {description}: {filename}")
        else:
            logger.warning(f"⚠️  Missing {description}: {filename}")
        time.sleep(0.2)

    # Simulate Kerberos authentication
    logger.info("\n🔐 Simulating Kerberos authentication...")
    time.sleep(1)
    logger.info(
        "✅ [SIMULATED] Successfully authenticated as: svcfracube@FRA.NET.INTRA"
    )
    logger.info("✅ [SIMULATED] Credential lifetime: 36000 seconds")

    # Simulate session creation
    logger.info("\n🌐 Simulating HTTP session creation...")
    time.sleep(0.5)
    logger.info(f"✅ [SIMULATED] Created session with proxy: {PROXY_HOST}:{PROXY_PORT}")
    logger.info(f"✅ [SIMULATED] Added custom headers: ApplicationName={APPLICATION_NAME}")

    if not args.no_test:
        # Simulate HTTP request
        logger.info(f"\n🚀 Simulating HTTP request to: {args.url}")
        time.sleep(1)
        logger.info("✅ [SIMULATED] Response status: 200")
        logger.info("✅ [SIMULATED] Response length: 15234 characters")

        # Show simulated response
        simulated_response = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Response</title>
</head>
<body>
    <h1>Simulated Response from {args.url}</h1>
    <p>This is a simulated response for dry-run testing.</p>
</body>
</html>"""

        logger.info("\n📄 [SIMULATED] Response preview:")
        logger.info("-" * 40)
        print(simulated_response[:200] + "...")
        logger.info("-" * 40)

    logger.info("\n✅ DRY RUN COMPLETED SUCCESSFULLY!")
    logger.info("💡 To run with real authentication, remove --dry-run flag")

    return 0


def main():
    """
    Main function - equivalent to the Java main method and CommandLineRunner
    """
    parser = argparse.ArgumentParser(
        description="Test Kerberos authentication through proxy"
    )
    parser.add_argument(
        "--url", default=TEST_URL, help=f"Test URL (default: {TEST_URL})"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--no-test", action="store_true", help="Skip the connection test"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without real authentication",
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    logger.info("=" * 60)
    logger.info("Kerberos Authentication Tester - Python Version")
    logger.info("=" * 60)
    logger.info(f"Principal: {KERBEROS_PRINCIPAL}")
    logger.info(f"Proxy: {PROXY_HOST}:{PROXY_PORT}")
    logger.info(f"Test URL: {args.url}")
    logger.info("=" * 60)

    client = None
    try:
        if args.dry_run:
            return simulate_dry_run(args)

        # Create the Kerberos client
        logger.info("🚀 Initializing Kerberos client...")
        client = ProxyKerberosClient()

        # Create authenticated session
        logger.info("🔐 Creating authenticated session...")
        client.create_authenticated_session()

        if not args.no_test:
            # Test the connection
            logger.info("🌐 Testing connection...")
            success, response = client.test_connection(args.url)

            if success:
                logger.info("✅ SUCCESS: Kerberos authentication working!")
                logger.info("📄 Response preview (first 200 chars):")
                logger.info("-" * 40)
                print(response[:200] + "..." if len(response) > 200 else response)
                logger.info("-" * 40)
                return 0
            else:
                logger.error("❌ FAILED: Kerberos authentication not working!")
                logger.error(f"Error: {response}")
                return 1
        else:
            logger.info("✅ Session created successfully (test skipped)")
            return 0

    except FileNotFoundError as e:
        logger.error(f"❌ Configuration file missing: {e}")
        logger.error("Please ensure keytab and krb5.conf files are present")
        return 1

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if args.debug:
            import traceback

            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
        return 1

    finally:
        # Clean up
        if client:
            client.close()
        logger.info("🧹 Cleanup completed")


def test_authentication_only():
    """
    Test only the Kerberos authentication without making HTTP requests
    """
    logger.info("Testing Kerberos authentication only...")

    try:

        kerberos_service = KerberosService()
        credentials = kerberos_service.authenticate()

        logger.info("✅ Kerberos authentication successful!")
        logger.info(f"Principal: {credentials.name}")
        logger.info(f"Lifetime: {credentials.lifetime}")

        return True

    except Exception as e:
        logger.error(f"❌ Kerberos authentication failed: {e}")
        return False


if __name__ == "__main__":
    """
    Entry point - equivalent to SpringApplication.run() in Java
    """
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n🛑 Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
