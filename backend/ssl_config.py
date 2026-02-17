"""SSL/HTTPS Configuration for Production."""
import os
from pathlib import Path

# SSL Certificate paths
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", "/etc/ssl/certs/cyber-sensei.crt")
SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", "/etc/ssl/private/cyber-sensei.key")

# SSL Configuration for Uvicorn
SSL_CONFIG = {
    "ssl_keyfile": SSL_KEY_PATH,
    "ssl_certfile": SSL_CERT_PATH,
    "ssl_version": 2,  # TLS 1.2+
    "ssl_cert_reqs": 0,  # No client cert required
}

def get_ssl_config():
    """
    Get SSL configuration if certificates exist.
    Returns None if certificates don't exist (development mode).
    """
    cert_path = Path(SSL_CERT_PATH)
    key_path = Path(SSL_KEY_PATH)
    
    if cert_path.exists() and key_path.exists():
        return SSL_CONFIG
    return None


def generate_self_signed_cert():
    """
    Generate self-signed certificate for development/testing.
    
    Usage:
        python -c "from ssl_config import generate_self_signed_cert; generate_self_signed_cert()"
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cyber Sensei"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Create directory if it doesn't exist
        cert_dir = Path("./ssl")
        cert_dir.mkdir(exist_ok=True)
        
        # Write certificate
        cert_path = cert_dir / "cert.pem"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        key_path = cert_dir / "key.pem"
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✅ Self-signed certificate generated:")
        print(f"   Certificate: {cert_path}")
        print(f"   Private Key: {key_path}")
        print(f"\n⚠️  This is for development only. Use proper certificates in production!")
        print(f"\nTo use these certificates, set environment variables:")
        print(f"   SSL_CERT_PATH={cert_path.absolute()}")
        print(f"   SSL_KEY_PATH={key_path.absolute()}")
        
    except ImportError:
        print("❌ cryptography package not installed.")
        print("Install it with: pip install cryptography")
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")


if __name__ == "__main__":
    generate_self_signed_cert()
