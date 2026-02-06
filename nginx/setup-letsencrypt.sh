#!/bin/bash
# Script para configurar Let's Encrypt con Certbot para HAPI FHIR
# Este script configurará certificados SSL válidos y confiables

DOMAIN="hiisc-dev.inf.pucp.edu.pe"
EMAIL="admin@pucp.edu.pe"  # Cambia esto a tu email

echo "=========================================="
echo "Configuración de Let's Encrypt"
echo "=========================================="
echo "Dominio: $DOMAIN"
echo "Email: $EMAIL"
echo ""
echo "IMPORTANTE: Antes de ejecutar este script:"
echo "1. Asegúrate de que el dominio $DOMAIN apunta a esta IP"
echo "2. El puerto 80 debe estar abierto y accesible desde internet"
echo "3. Docker debe estar corriendo"
echo "=========================================="
echo ""
read -p "¿Continuar? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelado."
    exit 1
fi

# Crear directorio para certificados de Let's Encrypt
mkdir -p certbot/conf
mkdir -p certbot/www

echo ""
echo "Paso 1: Deteniendo nginx si está corriendo..."
docker-compose stop nginx-gateway 2>/dev/null || true

echo ""
echo "Paso 2: Obteniendo certificado de Let's Encrypt..."
echo "Esto puede tardar unos minutos..."

# Ejecutar certbot para obtener certificado
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $DOMAIN

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Certificado obtenido exitosamente!"
    echo ""
    echo "Paso 3: Copiando certificados a la ubicación de nginx..."

    # Copiar certificados a la ubicación que usa nginx
    cp certbot/conf/live/$DOMAIN/fullchain.pem ssl/server.crt
    cp certbot/conf/live/$DOMAIN/privkey.pem ssl/server.key

    # Ajustar permisos
    chmod 644 ssl/server.crt
    chmod 600 ssl/server.key

    echo "✓ Certificados copiados exitosamente!"
    echo ""
    echo "Paso 4: Reiniciando nginx..."
    docker-compose up -d nginx-gateway

    echo ""
    echo "=========================================="
    echo "✓ Configuración completada!"
    echo "=========================================="
    echo "Tu sitio ahora tiene un certificado SSL válido."
    echo "Visita: https://$DOMAIN"
    echo ""
    echo "IMPORTANTE: Los certificados de Let's Encrypt expiran cada 90 días."
    echo "Para renovarlos automáticamente, ejecuta:"
    echo "  bash nginx/renew-letsencrypt.sh"
    echo "=========================================="
else
    echo ""
    echo "✗ Error al obtener el certificado."
    echo "Verifica que:"
    echo "  1. El dominio $DOMAIN apunta a esta IP"
    echo "  2. El puerto 80 está abierto"
    echo "  3. No hay otro servicio usando el puerto 80"
    echo ""
    echo "Puedes verificar la conectividad con:"
    echo "  curl http://$DOMAIN"
    exit 1
fi
