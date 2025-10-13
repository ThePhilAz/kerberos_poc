"""
Authentication methods for proxy client
Supports Kerberos, SSL certificate, and username/password authentication
"""

import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
from kerberos_poc.archive.kerberos_service import KerberosService


logger = logging.getLogger(__name__)


class AuthenticationMethod(ABC):
    """Base class for authentication methods"""

    @abstractmethod
    def authenticate_session(self, session: requests.Session) -> requests.Session:
        """Configure the session with authentication"""
        pass

    @abstractmethod
    def get_auth_name(self) -> str:
        """Get the name of the authentication method"""
        pass

    def get_proxy_auth(self) -> tuple[str, str] | None:
        """Get proxy authentication credentials if any"""
        return None

    def authenticate_async_client(
        self, client_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure httpx async client with authentication"""
        # Default implementation - override in subclasses for specific auth methods
        return client_kwargs


class KerberosAuthentication(AuthenticationMethod):
    """Kerberos authentication using keytab"""

    def __init__(self, principal: str, keytab_path: str, krb5_conf_path: str):
        self.principal = principal
        self.keytab_path = keytab_path
        self.krb5_conf_path = krb5_conf_path
        self.kerberos_service = KerberosService()

    def authenticate_session(self, session: requests.Session) -> requests.Session:
        """Configure session with Kerberos authentication"""
        try:
            # Authenticate with Kerberos using keytab - this populates the credential cache
            logger.info("Authenticating with Kerberos using keytab...")
            credentials = self.kerberos_service.authenticate()

            # Store credentials for potential reuse
            self.credentials = credentials
            logger.info("Successfully obtained Kerberos credentials")
            logger.info(
                f"Principal: {credentials.name if hasattr(credentials, 'name') else 'authenticated principal'}"
            )
            logger.info(
                f"Credential lifetime: {credentials.lifetime if hasattr(credentials, 'lifetime') else 'unknown'} seconds"
            )

            # Configure Kerberos authentication - requests-kerberos will use the credential cache
            kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
            session.auth = kerberos_auth

            logger.info(
                "Configured requests-kerberos to use populated credential cache"
            )
            return session

        except Exception as e:
            logger.error(f"Failed to configure Kerberos authentication: {str(e)}")
            raise

    def get_auth_name(self) -> str:
        return "Kerberos"

    def authenticate_async_client(
        self, client_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure httpx async client with Kerberos authentication"""
        try:
            # Authenticate with Kerberos using keytab - this populates the credential cache
            logger.info("Authenticating with Kerberos using keytab for async client...")
            credentials = self.kerberos_service.authenticate()

            # Store credentials for potential reuse
            self.credentials = credentials
            logger.info("Successfully obtained Kerberos credentials for async client")
            logger.info(
                f"Principal: {credentials.name if hasattr(credentials, 'name') else 'authenticated principal'}"
            )
            logger.info(
                f"Credential lifetime: {credentials.lifetime if hasattr(credentials, 'lifetime') else 'unknown'} seconds"
            )

            # For httpx, we need to use httpx-kerberos
            try:
                from httpx_kerberos import HTTPKerberosAuth as HttpxKerberosAuth

                client_kwargs["auth"] = HttpxKerberosAuth()
                logger.info("Configured httpx-kerberos for async client")
            except ImportError:
                logger.warning(
                    "httpx-kerberos not available, falling back to basic auth"
                )
                # Fallback: you might need to implement a custom auth handler
                pass

            return client_kwargs

        except Exception as e:
            logger.error(
                f"Failed to configure Kerberos authentication for async client: {str(e)}"
            )
            raise


class SSLCertificateAuthentication(AuthenticationMethod):
    """SSL certificate authentication"""

    def __init__(
        self,
        cert_path: str,
        key_path: str | None = None,
        ca_bundle_path: str | None = None,
    ):
        """
        Initialize SSL certificate authentication

        Args:
            cert_path: Path to client certificate file (.pem or .crt)
            key_path: Path to private key file (.key) - if None, assumes cert_path contains both cert and key
            ca_bundle_path: Path to CA bundle file for server verification - if None, uses system default
        """
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_bundle_path = ca_bundle_path

    def authenticate_session(self, session: requests.Session) -> requests.Session:
        """Configure session with SSL certificate authentication"""
        try:
            logger.info("Configuring SSL certificate authentication...")

            # Set client certificate
            if self.key_path:
                # Separate certificate and key files
                session.cert = (self.cert_path, self.key_path)
                logger.info(
                    f"Using certificate: {self.cert_path} with key: {self.key_path}"
                )
            else:
                # Certificate file contains both cert and key
                session.cert = self.cert_path
                logger.info(f"Using combined certificate file: {self.cert_path}")

            # Note: CA bundle is now handled globally by ProxyClient

            logger.info("Successfully configured SSL certificate authentication")
            return session

        except Exception as e:
            logger.error(
                f"Failed to configure SSL certificate authentication: {str(e)}"
            )
            raise

    def get_auth_name(self) -> str:
        return "SSL Certificate"

    def authenticate_async_client(
        self, client_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure httpx async client with SSL certificate authentication"""
        try:
            logger.info(
                "Configuring SSL certificate authentication for async client..."
            )

            # Set client certificate
            if self.key_path:
                # Separate certificate and key files
                client_kwargs["cert"] = (self.cert_path, self.key_path)
                logger.info(
                    f"Using certificate: {self.cert_path} with key: {self.key_path}"
                )
            else:
                # Certificate file contains both cert and key
                client_kwargs["cert"] = self.cert_path
                logger.info(f"Using combined certificate file: {self.cert_path}")

            logger.info(
                "Successfully configured SSL certificate authentication for async client"
            )
            return client_kwargs

        except Exception as e:
            logger.error(
                f"Failed to configure SSL certificate authentication for async client: {str(e)}"
            )
            raise


class UsernamePasswordAuthentication(AuthenticationMethod):
    """Username and password authentication using HTTP Basic Auth for PROXY authentication"""

    def __init__(self, username: str, password: str):
        """
        Initialize username/password authentication for PROXY

        Args:
            username: Username for PROXY authentication
            password: Password for PROXY authentication
        """
        self.username = username
        self.password = password

    def authenticate_session(self, session: requests.Session) -> requests.Session:
        """Configure session with username/password PROXY authentication"""
        try:
            logger.info("Configuring username/password PROXY authentication...")

            # No session configuration needed - credentials are provided via get_proxy_auth()

            logger.info(
                f"Successfully configured HTTP Basic PROXY Auth for user: {self.username}"
            )
            return session

        except Exception as e:
            logger.error(
                f"Failed to configure username/password PROXY authentication: {str(e)}"
            )
            raise

    def get_proxy_auth(self) -> tuple[str, str] | None:
        """Get proxy authentication credentials"""
        return (self.username, self.password)

    def get_auth_name(self) -> str:
        return "Username/Password (HTTP Basic Auth)"

    def authenticate_async_client(
        self, client_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure httpx async client with username/password PROXY authentication"""
        try:
            logger.info(
                "Configuring username/password PROXY authentication for async client..."
            )

            # No client configuration needed - credentials are provided via get_proxy_auth()
            # The proxy authentication is handled in the proxy URL construction

            logger.info(
                f"Successfully configured HTTP Basic PROXY Auth for async client user: {self.username}"
            )
            return client_kwargs

        except Exception as e:
            logger.error(
                f"Failed to configure username/password PROXY authentication for async client: {str(e)}"
            )
            raise


class DigestAuthentication(AuthenticationMethod):
    """Username and password authentication using HTTP Digest Auth"""

    def __init__(self, username: str, password: str):
        """
        Initialize username/password authentication with Digest

        Args:
            username: Username for authentication
            password: Password for authentication
        """
        self.username = username
        self.password = password

        if not username or not password:
            raise ValueError("Both username and password must be provided")

    def authenticate_session(self, session: requests.Session) -> requests.Session:
        """Configure session with username/password Digest authentication"""
        try:
            logger.info("Configuring username/password Digest authentication...")

            # Configure HTTP Digest Authentication
            from requests.auth import HTTPDigestAuth

            session.auth = HTTPDigestAuth(self.username, self.password)

            logger.info(
                f"Successfully configured HTTP Digest Auth for user: {self.username}"
            )
            return session

        except Exception as e:
            logger.error(
                f"Failed to configure username/password Digest authentication: {str(e)}"
            )
            raise

    def get_auth_name(self) -> str:
        return "Username/Password (HTTP Digest Auth)"

    def authenticate_async_client(
        self, client_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure httpx async client with username/password Digest authentication"""
        try:
            logger.info(
                "Configuring username/password Digest authentication for async client..."
            )

            # Configure HTTP Digest Authentication for httpx
            from httpx import DigestAuth

            client_kwargs["auth"] = DigestAuth(self.username, self.password)

            logger.info(
                f"Successfully configured HTTP Digest Auth for async client user: {self.username}"
            )
            return client_kwargs

        except Exception as e:
            logger.error(
                f"Failed to configure username/password Digest authentication for async client: {str(e)}"
            )
            raise


class NoAuthentication(AuthenticationMethod):
    """No authentication - CA bundle is handled globally by ProxyClient"""

    def __init__(self):
        """
        Initialize no authentication
        Note: CA bundle is now handled globally in ProxyClient for all auth methods
        """
        pass

    def authenticate_session(self, session: requests.Session) -> requests.Session:
        """Configure session with no authentication"""
        try:
            logger.info("Configuring no authentication...")

            # No authentication configuration needed
            # CA bundle verification is handled globally in ProxyClient

            logger.info("Successfully configured no authentication")
            return session

        except Exception as e:
            logger.error(f"Failed to configure no authentication: {str(e)}")
            raise

    def get_auth_name(self) -> str:
        return "No Authentication"

    def authenticate_async_client(
        self, client_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure httpx async client with no authentication"""
        try:
            logger.info("Configuring no authentication for async client...")

            # No authentication configuration needed
            # CA bundle verification is handled globally in AsyncProxyClient

            logger.info("Successfully configured no authentication for async client")
            return client_kwargs

        except Exception as e:
            logger.error(
                f"Failed to configure no authentication for async client: {str(e)}"
            )
            raise
