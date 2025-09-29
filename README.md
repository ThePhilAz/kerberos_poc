# Authentication POC - Python Implementation

A Python implementation for testing multiple authentication methods through proxy servers. This package supports Kerberos, SSL certificate, and username/password authentication for proxy connection testing.

## 📋 Overview

This package provides:

- **Multiple Authentication Methods**: Kerberos (keytab), SSL certificates, and username/password
- **Proxy Client**: HTTP client with configurable authentication and proxy support  
- **Individual Test Scripts**: Dedicated test files for each authentication method
- **Google Search Integration**: Optional Google Custom Search API testing
- **Configuration Management**: Environment-based configuration with comprehensive examples

## 🏗️ Architecture

The package consists of the following components:

```
kerberos_poc/
├── __init__.py          # Package initialization
├── config.py            # Configuration management with environment variables
├── auth_methods.py      # Authentication method implementations
├── kerberos_service.py  # Core Kerberos authentication service
└── proxy_client.py      # HTTP client with multiple auth methods and proxy support

# Test Scripts
test_kerberos.py         # Kerberos authentication test
test_ssl.py              # SSL certificate authentication test  
test_basic_auth.py       # Username/password authentication test
test_utils.py            # Shared test utilities and functions

# Configuration
env.example              # Comprehensive configuration template
AUTHENTICATION_TESTS.md  # Detailed testing documentation
```

## 🔧 Prerequisites

- **Python**: >= 3.10
- **Poetry**: For dependency management
- **Authentication credentials**: Depending on method:
  - **Kerberos**: Service keytab and krb5.conf configuration
  - **SSL**: Client certificate, private key, and CA bundle
  - **Basic Auth**: Username and password

## 🚀 Installation

```bash
# Clone the repository
git clone <repository-url>
cd kerberos_poc

# Install dependencies with Poetry
poetry install
```

## ⚙️ Configuration

```bash
# Copy the example environment file
cp env.example .env

# Edit the configuration file with your actual values
nano .env  # or your preferred editor
```

### Configuration Variables

The configuration supports multiple authentication methods. See `env.example` for the complete list.

**Required for all methods:**
```env
# Proxy and Test Configuration
PROXY_HOST=your-proxy-host.domain.com
PROXY_PORT=8080
TEST_URL=https://httpbin.org/get
APPLICATION_NAME=auth-poc-tester
```

**Authentication Method Selection:**
```env
# Choose your authentication method
AUTH_METHOD=kerberos  # Options: kerberos, ssl, basic
```

**Method-specific configuration:**
```env
# Kerberos (when AUTH_METHOD=kerberos)
KERBEROS_REALM=YOUR.REALM.COM
KERBEROS_PRINCIPAL=svcuser@YOUR.REALM.COM
KEYTAB_FILE_PATH=./svcfracube-jdk17.keytab
KRB5_CONF_PATH=./krb5.conf

# SSL Certificate (when AUTH_METHOD=ssl)
SSL_CERT_PATH=./certs/client.pem
SSL_KEY_PATH=./certs/client.key
SSL_CA_BUNDLE_PATH=./certs/ca-bundle.pem

# Username/Password (when AUTH_METHOD=basic)
AUTH_USERNAME=your-username
AUTH_PASSWORD=your-password

# Optional: Google Search API Testing
GOOGLE_SEARCH_API_KEY=your-api-key
GOOGLE_SEARCH_ENGINE_ID=your-engine-id
```

### Setting Up Authentication Files

**For Kerberos Authentication:**
```bash
# Copy your keytab and krb5.conf files to the project directory
cp /path/to/your/service.keytab ./svcfracube-jdk17.keytab
cp /path/to/your/krb5.conf ./krb5.conf

# Set appropriate permissions
chmod 600 ./svcfracube-jdk17.keytab
```

**For SSL Certificate Authentication:**
```bash
# Create certs directory and copy certificate files
mkdir -p certs
cp /path/to/your/client.pem ./certs/
cp /path/to/your/client.key ./certs/
cp /path/to/your/ca-bundle.pem ./certs/

# Set appropriate permissions
chmod 600 ./certs/client.key
```

## 🧪 Authentication Testing

Each authentication method has its own dedicated test script that performs two tests:
1. **Google Search API Test** (optional, if configured)
2. **URL Fetch Test** (connectivity verification)

### Test Scripts Overview

| Script | Authentication Method | Required Configuration |
|--------|----------------------|----------------------|
| `test_kerberos.py` | Kerberos (keytab) | Keytab file, krb5.conf |
| `test_ssl.py` | SSL Certificate | Client cert, private key, CA bundle |
| `test_basic_auth.py` | Username/Password | Username, password |

### Running Tests

#### 1. Kerberos Authentication Test
```bash
# Basic test
poetry run python test_kerberos.py

# With debug logging
poetry run python test_kerberos.py --debug

# Custom test URL
poetry run python test_kerberos.py --url https://httpbin.org/get
```

#### 2. SSL Certificate Authentication Test
```bash
# Using configuration from .env
poetry run python test_ssl.py

# With explicit certificate paths
poetry run python test_ssl.py --cert-path ./certs/client.pem --key-path ./certs/client.key --ca-bundle ./certs/ca-bundle.pem

# With debug logging
poetry run python test_ssl.py --debug
```

#### 3. Username/Password Authentication Test
```bash
# Using configuration from .env
poetry run python test_basic_auth.py

# With explicit credentials
poetry run python test_basic_auth.py --username myuser --password mypass

# Interactive password prompt
poetry run python test_basic_auth.py --username myuser

# Test with httpbin basic auth endpoint
poetry run python test_basic_auth.py --username testuser --password testpass --url https://httpbin.org/basic-auth/testuser/testpass
```

### Common Options

All test scripts support these options:
```bash
--debug          # Enable debug logging
--url URL        # Custom test URL (default from .env)
```

### Test Output

Each test provides detailed logging with clear indicators:
- 🚀 Initialization steps
- 🔐 Authentication process  
- 🔍 Google Search API test (if configured)
- 🌐 URL fetch test
- ✅ Success indicators
- ❌ Error indicators
- 📊 Test summary

## 🔍 Troubleshooting

### Common Issues

**Configuration Issues:**
- **Missing .env file**: Copy `env.example` to `.env` and configure
- **Missing required variables**: Check error messages for specific variables
- **Invalid file paths**: Verify all certificate/keytab file paths exist

**Authentication Issues:**
- **Kerberos**: Check keytab permissions (600), verify principal and realm
- **SSL**: Verify certificate validity and CA trust chain
- **Basic Auth**: Confirm username/password are correct

**Network Issues:**
- **Proxy Connection**: Verify proxy host/port are correct and accessible
- **SSL/TLS Issues**: Check certificate trust and CA bundles

### Debug Mode

Enable debug logging for any test:
```bash
# For any authentication method
poetry run python test_kerberos.py --debug
poetry run python test_ssl.py --debug  
poetry run python test_basic_auth.py --debug

# Or set globally in .env file
echo "DEBUG=true" >> .env
```

### Log Files

Each test creates its own log file:
- `test_kerberos.py` → logs to console and `auth_test.log`
- `test_ssl.py` → logs to console and `auth_test.log`  
- `test_basic_auth.py` → logs to console and `auth_test.log`

## 📚 Package Usage

### Using the Components

```python
from kerberos_poc.proxy_client import ProxyClient, ProxyKerberosClient
from kerberos_poc.auth_methods import (
    KerberosAuthentication, 
    SSLCertificateAuthentication, 
    UsernamePasswordAuthentication
)

# Method 1: Using specific authentication classes
kerberos_auth = KerberosAuthentication("user@REALM.COM", "./service.keytab", "./krb5.conf")
ssl_auth = SSLCertificateAuthentication("./cert.pem", "./key.pem", "./ca.pem")
basic_auth = UsernamePasswordAuthentication("username", "password")

# Create client with chosen authentication
client = ProxyClient(auth_method=kerberos_auth)  # or ssl_auth, basic_auth
client.create_authenticated_session()

# Method 2: Using backward-compatible Kerberos client
kerberos_client = ProxyKerberosClient()  # Uses config from .env
kerberos_client.create_authenticated_session()

# Make authenticated requests through proxy
response = client.make_request("https://example.com")
success, content = client.test_connection("https://httpbin.org/get")

# Clean up
client.close()
```

### Google Search API Integration

```python
from test_utils import test_google_search, test_url_fetch

# Run individual tests
search_success = test_google_search(client)
fetch_success = test_url_fetch(client, "https://example.com")
```

## 📖 Additional Documentation

- **[AUTHENTICATION_TESTS.md](AUTHENTICATION_TESTS.md)** - Detailed testing guide with examples
- **[env.example](env.example)** - Complete configuration template with all options
