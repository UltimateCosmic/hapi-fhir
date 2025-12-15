#!/bin/bash
# Script to generate self-signed SSL certificates for development

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/server.key \
  -out ssl/server.crt \
  -subj "/C=US/ST=State/L=City/O=HAPI-FHIR/CN=localhost"

echo "Self-signed SSL certificates generated successfully!"
echo "Certificate: ssl/server.crt"
echo "Private key: ssl/server.key"
echo ""
echo "WARNING: These are self-signed certificates for DEVELOPMENT ONLY."
echo "For production, use certificates from a trusted Certificate Authority."

# Set proper permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt

echo "Permissions set successfully."
