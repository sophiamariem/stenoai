"""Point packaged Python HTTPS clients at a CA bundle.

PyInstaller's `_ssl` may retain a build-machine OpenSSL directory that does not
exist on a customer's computer. Certifi provides a portable public CA bundle.
An operator can supply a managed-network CA bundle with SSL_CERT_FILE or
REQUESTS_CA_BUNDLE; an explicit value always wins. We do not export macOS
Keychain certificates into OpenSSL because `security find-certificate` does not
apply Keychain's trust settings, including explicit distrust decisions.
"""

from __future__ import annotations

import os


def configure() -> None:
    """Configure stdlib SSL and requests without overriding an operator's CA.

    Mirror a single explicit CA file to the other client. Distinct explicit
    values are preserved. Missing or broken explicit paths remain in place so
    TLS verification fails instead of silently broadening trust to certifi.
    """
    ssl_ca = os.environ.get("SSL_CERT_FILE")
    requests_ca = os.environ.get("REQUESTS_CA_BUNDLE")
    if ssl_ca or requests_ca:
        if ssl_ca and not requests_ca:
            os.environ["REQUESTS_CA_BUNDLE"] = ssl_ca
        elif requests_ca and not ssl_ca:
            os.environ["SSL_CERT_FILE"] = requests_ca
        return

    try:
        import certifi
    except ImportError:
        return
    ca_file = certifi.where()
    if not os.path.isfile(ca_file):
        return
    os.environ["SSL_CERT_FILE"] = ca_file
    os.environ["REQUESTS_CA_BUNDLE"] = ca_file


configure()
