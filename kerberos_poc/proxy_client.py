"""
HTTP client with multiple authentication methods for proxy testing
Supports Kerberos, SSL certificate, and username/password authentication
"""

import requests
import logging
from typing import Optional
from kerberos_poc.auth_methods import AuthenticationMethod, KerberosAuthentication
from kerberos_poc.config import PROXY_HOST, PROXY_PORT, CUSTOM_HEADERS

logger = logging.getLogger(__name__)


class ProxyClient:
    """
    HTTP client configured for multiple authentication methods through proxy
    Supports Kerberos, SSL certificate, and username/password authentication
    """

    def __init__(self, auth_method: Optional[AuthenticationMethod] = None):
        self.proxy_host = PROXY_HOST
        self.proxy_port = PROXY_PORT
        self.auth_method = auth_method
        self.session = None

    def create_authenticated_session(self):
        """
        Create a requests session with the configured authentication method
        """
        try:
            if self.auth_method is None:
                raise ValueError(
                    "No authentication method configured. Please provide an AuthenticationMethod instance."
                )

            logger.info(
                f"Creating authenticated session using: {self.auth_method.get_auth_name()}"
            )

            # Create session
            session = requests.Session()

            # Configure authentication using the provided method
            session = self.auth_method.authenticate_session(session)

            # Configure proxy
            proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
            session.proxies = {"http": proxy_url, "https": proxy_url}

            # Add custom headers (equivalent to the Java HttpRequestInterceptor)
            session.headers.update(CUSTOM_HEADERS)

            # Configure session settings
            session.trust_env = False  # Don't use environment proxy settings

            logger.info(f"Created authenticated session with proxy: {proxy_url}")
            logger.info(f"Authentication method: {self.auth_method.get_auth_name()}")
            logger.info(f"Custom headers: {CUSTOM_HEADERS}")

            self.session = session

        except Exception as e:
            logger.error(f"Failed to create authenticated session: {str(e)}")
            raise

    def make_request(self, url, method="GET", **kwargs):
        """
        Make an authenticated HTTP request through the proxy
        """
        try:
            if self.session is None:
                self.create_authenticated_session()

            logger.info(f"Making {method} request to: {url}")
            logger.info(f"Using proxy: {self.proxy_host}:{self.proxy_port}")

            # Make the request
            assert self.session is not None, "Session is not created"
            response = self.session.request(method, url, **kwargs)

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")

            return response

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def test_connection(self, test_url="https://www.google.com"):
        """
        Test the Kerberos authentication by making a request to a test URL
        Equivalent to the Java commandLineRunner test
        """
        try:
            logger.info(f"Testing connection to: {test_url}")

            response = self.make_request(test_url)

            if response.status_code == 200:
                logger.info("✅ Connection test successful!")
                logger.info(f"Response length: {len(response.text)} characters")
                return True, response.text
            else:
                logger.warning(f"⚠️ Unexpected status code: {response.status_code}")
                return False, response.text

        except Exception as e:
            logger.error(f"❌ Connection test failed: {str(e)}")
            return False, str(e)

    def close(self):
        """
        Close the session
        """
        if self.session:
            self.session.close()
            logger.info("Session closed")


# Backward compatibility - create a Kerberos-specific client
class ProxyKerberosClient(ProxyClient):
    """
    Backward compatible Kerberos-specific proxy client
    """

    def __init__(self, principal: str, keytab_path: str, krb5_conf_path: str):
        """
        Initialize with Kerberos authentication

        Args:
            principal: Kerberos principal (if None, uses config)
            keytab_path: Path to keytab file (if None, uses config)
            krb5_conf_path: Path to krb5.conf file (if None, uses config)
        """

        # Create Kerberos authentication method
        auth_method = KerberosAuthentication(principal, keytab_path, krb5_conf_path)

        # Initialize parent with Kerberos authentication
        super().__init__(auth_method=auth_method)
