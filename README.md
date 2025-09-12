# Kerberos POC - Python Implementation

A Python implementation for testing Kerberos authentication through proxy servers. This package replicates Java Kerberos functionality for proxy connection testing.

## 📋 Overview

This package provides:

- **Kerberos Service**: Handles authentication using keytab files
- **Proxy Client**: HTTP client with Kerberos authentication and proxy support
- **Test Runner**: Command-line tool for testing authentication and connectivity
- **Configuration Management**: Environment-based configuration

## 🏗️ Architecture

The package consists of four main components:

```
kerberos_poc/
├── __init__.py          # Package initialization
├── config.py            # Configuration management with environment variables
├── kerberos_service.py  # Core Kerberos authentication service
└── proxy_client.py      # HTTP client with Kerberos auth and proxy support

kerberos_tester.py       # Main test runner and CLI interface
```

## 🔧 Prerequisites

- **Python**: >= 3.10
- **Poetry**: For dependency management
- **Kerberos files**: Service keytab and krb5.conf configuration

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
cp .env.example .env

# Edit the configuration file
nano .env  # or your preferred editor
```

### Required Environment Variables

```env
# Proxy Configuration
PROXY_HOST=your-proxy-host.domain.com
PROXY_PORT=8080

# Kerberos Configuration
KERBEROS_REALM=YOUR.REALM.COM
KERBEROS_PRINCIPAL=your-service@YOUR.REALM.COM
KEYTAB_FILE_PATH=/path/to/your/service.keytab
KRB5_CONF_PATH=/path/to/your/krb5.conf

# Test Configuration
TEST_URL=https://httpbin.org/get
APPLICATION_NAME=KerberosPOC

# Optional Configuration
DRY_RUN=false
NO_TEST=false
DEBUG=false
LOG_LEVEL=INFO
```

### Place Your Kerberos Files

```bash
# Copy your keytab and krb5.conf files to the project directory
cp /path/to/your/service.keytab ./svcfracube-jdk17.keytab
cp /path/to/your/krb5.conf ./krb5.conf

# Update the paths in .env to match your files
```

## 🧪 Testing

### Running the Tests

#### 1. Dry Run (No Authentication)
```bash
# Test the script without real Kerberos authentication
poetry run python kerberos_tester.py --dry-run
```

#### 2. Authentication Only
```bash
# Test Kerberos authentication without HTTP requests
poetry run python kerberos_tester.py --no-test
```

#### 3. Full Test
```bash
# Test authentication and HTTP connectivity through proxy
poetry run python kerberos_tester.py

# Test with custom URL
poetry run python kerberos_tester.py --url https://httpbin.org/get

# Enable debug logging
poetry run python kerberos_tester.py --debug
```

### Command Line Options

```bash
# Available options:
--url URL        # Custom test URL (default from .env)
--debug          # Enable debug logging
--no-test        # Skip HTTP connection test
--dry-run        # Simulate execution without authentication
```

## 🔍 Troubleshooting

### Common Issues

- **Configuration Error**: Check `.env` file exists and contains all required variables
- **Keytab File Not Found**: Verify keytab file path in `.env` is correct
- **Authentication Failed**: Enable debug mode with `--debug` flag
- **Network Issues**: Test proxy connectivity separately

### Debug Mode

```bash
# Enable debug logging
poetry run python kerberos_tester.py --debug

# Or set in .env file
echo "DEBUG=true" >> .env
```

### Log Files

Check `kerberos_test.log` for detailed execution logs.

## 📚 Package Usage

### Using the Components

```python
from kerberos_poc.kerberos_service import KerberosService
from kerberos_poc.proxy_client import ProxyKerberosClient

# Authenticate with Kerberos
service = KerberosService()
credentials = service.authenticate()

# Create HTTP client with proxy support
client = ProxyKerberosClient()
client.create_authenticated_session()

# Make authenticated requests
response = client.make_request("https://example.com")
client.close()
```
