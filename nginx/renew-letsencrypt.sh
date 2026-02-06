#!/bin/bash
# Script para renovar certificados de Let's Encrypt
# Los certificados de Let's Encrypt expiran cada 90 días

DOMAIN="hiisc-dev.inf.pucp.edu.pe"

echo "=========================================="
echo "Renovación de certificados Let's Encrypt"
echo "=========================================="
echo "Dominio: $DOMAIN"
echo ""

# Verificar si existen certificados
if [ ! -d "certbot/conf/live/$DOMAIN" ]; then
    echo "✗ No se encontraron certificados para $DOMAIN"
    echo "Ejecuta primero: bash nginx/setup-letsencrypt.sh"
    exit 1
fi

echo "Deteniendo nginx temporalmente..."
docker-compose stop nginx-gateway

echo "Renovando certificados..."
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot renew

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Certificados renovados exitosamente!"
    echo ""
    echo "Copiando certificados actualizados..."
    cp certbot/conf/live/$DOMAIN/fullchain.pem ssl/server.crt
    cp certbot/conf/live/$DOMAIN/privkey.pem ssl/server.key
    chmod 644 ssl/server.crt
    chmod 600 ssl/server.key

    echo "Reiniciando nginx..."
    docker-compose up -d nginx-gateway

    echo ""
    echo "=========================================="
    echo "✓ Renovación completada!"
    echo "=========================================="
    echo "Los certificados han sido renovados y nginx reiniciado."
else
    echo ""
    echo "✗ Error al renovar los certificados."
    echo "Verifica que el puerto 80 esté disponible."

    echo "Reiniciando nginx..."
    docker-compose up -d nginx-gateway
    exit 1
fi
