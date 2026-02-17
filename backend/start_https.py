"""Start the application with HTTPS support."""
import uvicorn
import os
from ssl_config import get_ssl_config

def main():
    """Start Uvicorn with SSL if certificates are available."""
    ssl_config = get_ssl_config()
    
    # Base configuration
    config = {
        "app": "app.main:app",
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": "info",
    }
    
    # Add SSL configuration if available
    if ssl_config:
        config.update(ssl_config)
        print("🔒 Starting server with HTTPS enabled")
        print(f"   URL: https://{config['host']}:{config['port']}")
    else:
        print("⚠️  SSL certificates not found. Starting with HTTP")
        print(f"   URL: http://{config['host']}:{config['port']}")
        print("\nTo enable HTTPS:")
        print("1. Generate self-signed cert: python ssl_config.py")
        print("2. Or set SSL_CERT_PATH and SSL_KEY_PATH environment variables")
    
    uvicorn.run(**config)


if __name__ == "__main__":
    main()
