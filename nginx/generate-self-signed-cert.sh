#!/bin/bash
# Script to generate self-signed SSL certificates for development

# Domain configuration
DOMAIN="hiisc-dev.inf.pucp.edu.pe"
COUNTRY="PE"
STATE="Lima"
CITY="Lima"
ORG="PUCP"

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Create OpenSSL config file with SAN (Subject Alternative Names)
cat > ssl/openssl.cnf <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[dn]
C = ${COUNTRY}
ST = ${STATE}
L = ${CITY}
O = ${ORG}
CN = ${DOMAIN}

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = www.${DOMAIN}
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF

# Generate self-signed certificate with SAN
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/server.key \
  -out ssl/server.crt \
  -config ssl/openssl.cnf \
  -extensions req_ext

echo "Self-signed SSL certificates generated successfully!"
echo "Certificate: ssl/server.crt"
echo "Private key: ssl/server.key"
echo "Domain: ${DOMAIN}"
echo ""
echo "WARNING: These are self-signed certificates for DEVELOPMENT ONLY."
echo "Browsers will still show a warning because the certificate is not from a trusted CA."
echo "For production, use certificates from Let's Encrypt or another trusted Certificate Authority."

# Set proper permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt

echo "Permissions set successfully."

# Display certificate info
echo ""
echo "Certificate details:"
openssl x509 -in ssl/server.crt -text -noout | grep -E "Subject:|Issuer:|DNS:"
