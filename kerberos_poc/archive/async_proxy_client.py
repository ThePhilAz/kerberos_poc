"""
Async HTTP client with multiple authentication methods for proxy testing
Supports Kerberos, SSL certificate, and username/password authentication
Uses httpx for async HTTP operations
"""

import httpx
import logging
from typing import Optional
from kerberos_poc.archive.auth_methods import AuthenticationMethod, KerberosAuthentication
from kerberos_poc.archive.config import (
    PROXY_HOST,
    PROXY_PORT,
    CUSTOM_HEADERS,
    SSL_CA_BUNDLE_PATH,
)

logger = logging.getLogger(__name__)


class AsyncProxyClient:
    """
    Async HTTP client configured for multiple authentication methods through proxy
    Supports Kerberos, SSL certificate, and username/password authentication
    Uses httpx for async operations
    """

    def __init__(self, auth_method: Optional[AuthenticationMethod] = None):
        self.proxy_host = PROXY_HOST
        self.proxy_port = PROXY_PORT
        self.auth_method = auth_method
        self.client: Optional[httpx.AsyncClient] = None

    async def create_authenticated_client(self):
        """
        Create an httpx async client with the configured authentication method
        """
        try:
            if self.auth_method is None:
                raise ValueError(
                    "No authentication method configured. Please provide an AuthenticationMethod instance."
                )

            logger.info(
                f"Creating authenticated async client using: {self.auth_method.get_auth_name()}"
            )

            # Build proxy URL
            proxy_url = self._build_proxy_url()

            # Configure httpx client
            client_kwargs = {
                "proxies": {"http://": proxy_url, "https://": proxy_url},
                "headers": CUSTOM_HEADERS,
                "trust_env": False,  # Don't use environment proxy settings
            }

            # Configure SSL verification
            if SSL_CA_BUNDLE_PATH:
                client_kwargs["verify"] = SSL_CA_BUNDLE_PATH
                logger.info(
                    f"Using CA bundle for SSL verification: {SSL_CA_BUNDLE_PATH}"
                )
            else:
                client_kwargs["verify"] = True
                logger.info("Using system default CA bundle for SSL verification")

            # Configure authentication using the provided method
            client_kwargs = self.auth_method.authenticate_async_client(client_kwargs)

            # Create the async client
            self.client = httpx.AsyncClient(**client_kwargs)

            logger.info(f"Created authenticated async client with proxy: {proxy_url}")
            logger.info(f"Authentication method: {self.auth_method.get_auth_name()}")
            logger.info(f"Custom headers: {CUSTOM_HEADERS}")

        except Exception as e:
            logger.error(f"Failed to create authenticated async client: {str(e)}")
            raise

    async def make_request(self, url, method="GET", **kwargs):
        """
        Make an authenticated HTTP request through the proxy
        """
        try:
            if self.client is None:
                await self.create_authenticated_client()

            logger.info(f"Making {method} request to: {url}")
            logger.info(f"Using proxy: {self.proxy_host}:{self.proxy_port}")

            # Make the request
            assert self.client is not None, "Client is not created"
            response = await self.client.request(method, url, **kwargs)

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")

            return response

        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def test_connection(self, test_url="https://www.google.com"):
        """
        Test the authentication by making a request to a test URL
        """
        try:
            logger.info(f"Testing connection to: {test_url}")

            response = await self.make_request(test_url)

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

    async def close(self):
        """
        Close the async client
        """
        if self.client:
            await self.client.aclose()
            logger.info("Async client closed")

    def _build_proxy_url(self) -> str:
        """Build proxy URL with authentication if needed"""
        # Check if auth method provides proxy credentials
        assert self.auth_method is not None, "Authentication method is not configured"
        proxy_auth = self.auth_method.get_proxy_auth()
        if proxy_auth:
            username, password = proxy_auth
            proxy_url = (
                f"http://{username}:{password}@{self.proxy_host}:{self.proxy_port}"
            )
            logger.info(
                f"Using proxy with authentication: {username}@{self.proxy_host}:{self.proxy_port}"
            )
        else:
            proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
            logger.info(
                f"Using proxy without authentication: {self.proxy_host}:{self.proxy_port}"
            )

        return proxy_url

    async def __aenter__(self):
        """Async context manager entry"""
        await self.create_authenticated_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# Backward compatibility - create a Kerberos-specific async client
class AsyncProxyKerberosClient(AsyncProxyClient):
    """
    Backward compatible Kerberos-specific async proxy client
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
