"""
HTTP client with Kerberos authentication for proxy testing
Replicates the functionality of the Java ProxyKerberosConfiguration
"""

import requests
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
import logging
from kerberos_poc.kerberos_service import KerberosService
from kerberos_poc.config import PROXY_HOST, PROXY_PORT, CUSTOM_HEADERS

logger = logging.getLogger(__name__)


class ProxyKerberosClient:
    """
    HTTP client configured for Kerberos authentication through proxy
    Equivalent to the Java HttpClient configuration
    """

    def __init__(self):
        self.proxy_host = PROXY_HOST
        self.proxy_port = PROXY_PORT
        self.kerberos_service = KerberosService()
        self.session = None

    def create_authenticated_session(self):
        """
        Create a requests session with Kerberos authentication
        Equivalent to the Java httpClient() bean configuration
        """
        try:
            # Authenticate with Kerberos using keytab - this populates the credential cache
            logger.info("Authenticating with Kerberos using keytab...")
            credentials = self.kerberos_service.authenticate()
            
            # Store credentials for potential reuse
            self.credentials = credentials
            logger.info("Successfully obtained Kerberos credentials")
            logger.info(f"Principal: {credentials.name if hasattr(credentials, 'name') else 'authenticated principal'}")
            logger.info(f"Credential lifetime: {credentials.lifetime if hasattr(credentials, 'lifetime') else 'unknown'} seconds")

            # Create session
            session = requests.Session()

            # Configure Kerberos authentication - requests-kerberos will use the credential cache
            # that was populated by our gssapi authentication above
            kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
            session.auth = kerberos_auth
            
            logger.info("Configured requests-kerberos to use populated credential cache")

            # Configure proxy
            proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
            session.proxies = {"http": proxy_url, "https": proxy_url}

            # Add custom headers (equivalent to the Java HttpRequestInterceptor)
            session.headers.update(CUSTOM_HEADERS)

            # Configure session for Kerberos
            session.trust_env = False  # Don't use environment proxy settings

            logger.info(f"Created authenticated session with proxy: {proxy_url}")
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
