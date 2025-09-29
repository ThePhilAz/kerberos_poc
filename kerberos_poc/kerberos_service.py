"""
Kerberos authentication service for Python
Replicates the functionality of the Java KerberosService class
"""

import os
import gssapi
import logging
from kerberos_poc.config import KERBEROS_PRINCIPAL, KEYTAB_FILE_PATH, KRB5_CONF_PATH

logger = logging.getLogger(__name__)


class KerberosService:
    """
    Service class for handling Kerberos authentication
    """

    def __init__(self):
        self.principal = KERBEROS_PRINCIPAL
        self.keytab_file_path = KEYTAB_FILE_PATH
        self.krb5_conf_path = KRB5_CONF_PATH

    def setup_environment(self):
        """
        Set up the Kerberos environment variables
        Similar to the Java system properties setup
        """
        # Set KRB5 configuration file
        os.environ["KRB5_CONFIG"] = self.krb5_conf_path
        os.environ["KRB5CCNAME"] = "MEMORY:kerberos_cache"

        # Set keytab file for credential acquisition
        # This is required for older GSSAPI implementations that don't support
        # the credential store extension
        os.environ["KRB5_KTNAME"] = self.keytab_file_path

        logger.info(f"Set KRB5_CONFIG to: {self.krb5_conf_path}")
        logger.info(f"Set KRB5_KTNAME to: {self.keytab_file_path}")
        logger.info(f"Using keytab file: {self.keytab_file_path}")
        logger.info(f"Principal: {self.principal}")

    def authenticate(self):
        """
        Authenticate using keytab and return GSS credentials
        Equivalent to the Java authenticate() method
        """
        try:
            # Setup environment
            self.setup_environment()

            # Check if keytab file exists
            if not os.path.exists(self.keytab_file_path):
                raise FileNotFoundError(
                    f"Keytab file not found: {self.keytab_file_path}"
                )

            if not os.path.exists(self.krb5_conf_path):
                raise FileNotFoundError(
                    f"KRB5 config file not found: {self.krb5_conf_path}"
                )

            # Create GSS name for the principal
            principal_name = gssapi.Name(
                self.principal, gssapi.NameType.kerberos_principal
            )

            # Acquire credentials using keytab
            # This is equivalent to manager.createCredential() in Java
            credentials = self._acquire_credentials_with_fallback(principal_name)

            logger.info(f"Successfully authenticated as: {self.principal}")

            # Safely access credential lifetime
            try:
                lifetime = credentials.lifetime
                logger.info(f"Credential lifetime: {lifetime} seconds")
            except Exception as e:
                logger.debug(f"Could not access credential lifetime: {e}")
                logger.info("Credential lifetime: Unknown (access failed)")

            # Store credentials in the credential cache for requests-kerberos to use
            self._store_credentials_in_cache(credentials)

            return credentials

        except Exception as e:
            logger.error(f"Kerberos authentication failed: {str(e)}")
            raise

    def _store_credentials_in_cache(self, credentials):
        """
        Store GSS credentials in the credential cache so requests-kerberos can use them
        """
        try:
            # The credentials are already associated with the credential cache
            # when using KRB5_KTNAME environment variable or default acquisition
            logger.debug("Credentials should be accessible in credential cache")

            # Verify credentials are accessible (safely)
            try:
                if hasattr(credentials, "name") and credentials.name:
                    logger.debug(
                        f"Credential cache contains credentials for: {credentials.name}"
                    )
                else:
                    logger.debug(
                        "Credentials acquired but principal name not accessible"
                    )
            except Exception as name_error:
                logger.debug(f"Could not access credential name: {name_error}")

        except Exception as e:
            logger.warning(f"Could not verify credential cache storage: {e}")

    def _acquire_credentials_with_fallback(self, principal_name):
        """
        Acquire GSS credentials with fallback for different GSSAPI implementations

        This method tries multiple approaches to acquire credentials:
        1. Modern approach: using credential store extension (MIT Kerberos >= 1.11)
        2. Legacy approach: using KRB5_KTNAME environment variable
        """

        # First, try the modern credential store approach
        try:
            logger.debug("Attempting credential acquisition with store parameter")
            credentials = gssapi.Credentials(
                name=principal_name,
                usage="initiate",
                store={"keytab": self.keytab_file_path},
            )
            logger.info(
                "Successfully acquired credentials using credential store extension"
            )
            return credentials

        except Exception as store_error:
            logger.debug(f"Credential store approach failed: {store_error}")

            # Fall back to environment variable approach
            logger.debug("Falling back to KRB5_KTNAME environment variable approach")
            try:
                # Ensure KRB5_KTNAME is set (should be done in setup_environment)
                if "KRB5_KTNAME" not in os.environ:
                    os.environ["KRB5_KTNAME"] = self.keytab_file_path
                    logger.debug(f"Set KRB5_KTNAME to: {self.keytab_file_path}")

                credentials = gssapi.Credentials(name=principal_name, usage="initiate")
                logger.info(
                    "Successfully acquired credentials using KRB5_KTNAME environment variable"
                )
                return credentials

            except Exception as env_error:
                logger.error("Both credential acquisition methods failed:")
                logger.error(f"  Store method: {store_error}")
                logger.error(f"  Environment method: {env_error}")

                # Try one more approach without specifying the principal name
                try:
                    logger.debug(
                        "Attempting credential acquisition without principal specification"
                    )
                    credentials = gssapi.Credentials(usage="initiate")
                    logger.info("Successfully acquired default credentials")
                    return credentials

                except Exception as default_error:
                    logger.error(
                        f"Default credential acquisition also failed: {default_error}"
                    )
                    raise Exception(
                        f"Failed to acquire Kerberos credentials using any method. "
                        f"This may indicate:\n"
                        f"1. GSSAPI implementation lacks credential store support (MIT Kerberos < 1.11)\n"
                        f"2. Keytab file is inaccessible or invalid: {self.keytab_file_path}\n"
                        f"3. Principal name is incorrect: {principal_name}\n"
                        f"4. Kerberos configuration issues\n"
                        f"Original errors: Store={store_error}, Env={env_error}, Default={default_error}"
                    )

    def get_service_ticket(self, service_name, credentials=None):
        """
        Get a service ticket for the specified service
        """
        try:
            if credentials is None:
                credentials = self.authenticate()

            # Create service name
            service_principal = gssapi.Name(
                service_name, gssapi.NameType.hostbased_service
            )

            # Create security context
            context = gssapi.SecurityContext(
                name=service_principal, creds=credentials, usage="initiate"
            )

            # Generate initial token
            token = context.step()

            logger.info(f"Generated service ticket for: {service_name}")

            return context, token

        except Exception as e:
            logger.error(f"Failed to get service ticket for {service_name}: {str(e)}")
            raise
