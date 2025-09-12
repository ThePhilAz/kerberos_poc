"""
Configuration settings for Kerberos authentication testing
All settings must be provided via environment variables (.env file)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class ConfigError(Exception):
    """Raised when required configuration is missing"""
    pass

def get_required_env(key: str) -> str:
    """Get required environment variable or raise ConfigError"""
    value = os.getenv(key)
    if value is None:
        raise ConfigError(f"Required environment variable '{key}' is not set. Please check your .env file.")
    return value

def get_optional_env(key: str, default: str | None = None) -> str | None:
    """Get optional environment variable with optional default"""
    return os.getenv(key, default)

def get_bool_env(key: str, required: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.getenv(key)
    if value is None:
        if required:
            raise ConfigError(f"Required environment variable '{key}' is not set. Please check your .env file.")
        return False
    return value.lower() in ('true', '1', 'yes', 'on')

def get_int_env(key: str, required: bool = True) -> int | None:
    """Get integer environment variable"""
    value = os.getenv(key)
    if value is None:
        if required:
            raise ConfigError(f"Required environment variable '{key}' is not set. Please check your .env file.")
        return None
    try:
        return int(value)
    except ValueError:
        raise ConfigError(f"Environment variable '{key}' must be a valid integer, got: {value}")

# Required configuration
try:
    # Proxy configuration
    PROXY_HOST = get_required_env("PROXY_HOST")
    PROXY_PORT = get_int_env("PROXY_PORT")

    # Kerberos configuration
    KERBEROS_REALM = get_required_env("KERBEROS_REALM")
    KERBEROS_PRINCIPAL = get_required_env("KERBEROS_PRINCIPAL")
    KEYTAB_FILE_PATH = get_required_env("KEYTAB_FILE_PATH")
    KRB5_CONF_PATH = get_required_env("KRB5_CONF_PATH")

    # Test configuration
    TEST_URL = get_required_env("TEST_URL")
    APPLICATION_NAME = get_required_env("APPLICATION_NAME")

    # Optional configuration with sensible defaults
    DRY_RUN = get_bool_env("DRY_RUN")
    NO_TEST = get_bool_env("NO_TEST")
    DEBUG = get_bool_env("DEBUG")
    LOG_LEVEL = get_optional_env("LOG_LEVEL", "INFO")
    if LOG_LEVEL:
        LOG_LEVEL = LOG_LEVEL.upper()
    else:
        LOG_LEVEL = "INFO"

    # Derived configuration
    CUSTOM_HEADERS = {"ApplicationName": APPLICATION_NAME}

except ConfigError as e:
    print(f"❌ Configuration Error: {e}")
    print("💡 Please create a .env file based on .env.example")
    print("   cp .env.example .env")
    print("   # Then edit .env with your values")
    raise SystemExit(1)
