# Simulador RENHICE/Dyaku - HAPI FHIR JPA Server

Servidor HAPI FHIR R4 configurado como simulador local de RENHICE (Registro Nacional de Historias Clínicas Electrónicas) del MINSA Perú, para desarrollo y pruebas del Módulo de Interoperabilidad SIH.SALUS.

## Hospital Santa Clotilde - Ambiente de Desarrollo

---

## Descripción

Este servidor HAPI FHIR simula el comportamiento de RENHICE/Dyaku en un ambiente local, permitiendo:
- Desarrollo y pruebas sin depender de la disponibilidad del sistema real
- Validación de implementación FHIR R4 con perfiles Dyaku
- Testing de interoperabilidad antes de despliegue en producción

## Características

- **HAPI FHIR R4**: Implementación completa HL7 FHIR 4.0.1
- **Base de Datos**: PostgreSQL 15 persistente
- **Perfiles Dyaku**: Cargados desde el servidor oficial del MINSA
- **Datos de Prueba**: Script de población con datos peruanos realistas
- **Docker**: Configuración lista para usar con Docker Compose

## Requisitos

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.8+ (para script de población)

## Instalación y Ejecución

### 1. Iniciar Servidor

```bash
docker-compose up -d
```

Servicios levantados:
- **HAPI FHIR Server**: `http://localhost:8081/fhir`
- **HAPI FHIR UI**: `http://localhost:8081/`
- **PostgreSQL**: Puerto 5432 (interno)

### 2. Verificar Estado

```bash
curl http://localhost:8081/fhir/metadata
```

Debe responder con el CapabilityStatement del servidor.

### 3. Poblar Datos de Prueba

```bash
pip install -r requirements.txt
py populate_test_data.py
```

Este script crea:
- 1 Organización (IPRESS)
- 1 Practitioner (profesional de salud)
- 10 Pacientes con DNI peruano
- Encounters, Conditions, Observations por paciente

## Configuración

### Archivo docker-compose.yml

```yaml
services:
  hapi-fhir-postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: hapi
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin

  hapi-fhir-jpaserver-start:
    build: .
    ports:
      - "8081:8080"
    environment:
      spring.datasource.url: jdbc:postgresql://hapi-fhir-postgres:5432/hapi
      spring.datasource.username: admin
      spring.datasource.password: admin
      hapi.fhir.fhir_version: R4
```

### Variables de Entorno

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `spring.datasource.url` | `jdbc:postgresql://...` | URL de conexión a PostgreSQL |
| `hapi.fhir.fhir_version` | `R4` | Versión FHIR a utilizar |
| `hapi.fhir.narrative_enabled` | `true` | Habilitar narrativas HTML |

## Endpoints Principales

### API FHIR

- **Base**: `http://localhost:8081/fhir`
- **Metadata**: `GET /metadata`
- **Patients**: `GET /Patient`, `POST /Patient`
- **Bundles**: `POST /` (transacciones)

### Interfaz Web

- **UI HAPI**: `http://localhost:8081/`
- **Swagger**: `http://localhost:8081/swagger-ui/`

## Uso

### Buscar Paciente por DNI

```bash
curl "http://localhost:8081/fhir/Patient?identifier=74176968"
```

### Crear Paciente

```bash
curl -X POST "http://localhost:8081/fhir/Patient" \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "identifier": [{
      "system": "urn:oid:2.16.840.1.113883.4.904",
      "value": "12345678"
    }],
    "name": [{
      "family": "Fernández",
      "given": ["José"]
    }]
  }'
```

### Enviar Bundle (Transacción)

```bash
curl -X POST "http://localhost:8081/fhir" \
  -H "Content-Type: application/fhir+json" \
  -d @bundle.json
```

## Datos de Prueba

### Pacientes Generados

El script `populate_test_data.py` crea 10 pacientes con:
- DNI válido peruano (8 dígitos)
- Datos demográficos realistas
- Dirección con UBIGEO
- Historia clínica básica (diagnósticos, observaciones)

Ejemplo de DNI generado: `74176968`, `85234190`, `63298471`

### Estructura de Datos

Cada paciente incluye:
- **Patient**: Recurso con perfil PacientePe
- **Encounter**: Consulta ambulatoria
- **Condition**: Diagnóstico CIE-10
- **Observation**: Signos vitales (presión arterial, frecuencia cardíaca, etc.)

## Mantenimiento

### Ver Logs

```bash
docker logs hapi-fhir-jpaserver-start --tail 100
```

### Reiniciar Servidor

```bash
docker-compose restart hapi-fhir-jpaserver-start
```

### Limpiar Base de Datos

```bash
docker-compose down -v
docker-compose up -d
py populate_test_data.py
```

## Troubleshooting

### Puerto 8081 en uso

Cambiar en `docker-compose.yml`:
```yaml
ports:
  - "8082:8080"  # Usar otro puerto externo
```

### Error de conexión a PostgreSQL

Verificar que el contenedor de PostgreSQL esté ejecutándose:
```bash
docker ps | grep postgres
```

### Datos no persisten

Verificar que el volumen de PostgreSQL esté creado:
```bash
docker volume ls | grep hapi
```

## Integración con SIH.SALUS

### Configuración en Módulo de Interoperabilidad

En OpenMRS, configurar propiedad global:
```
sihsalusinterop.renhice.endpoint = http://hapi-fhir-jpaserver-start:8080/fhir
```

**Nota**: Usar nombre de contenedor Docker, no `localhost`.

### Red Docker

Asegurar que ambos contenedores estén en la misma red:
```bash
docker network connect sihsalus-distro-referenceapplication_default hapi-fhir-jpaserver-start
```

## Diferencias con RENHICE Real

Este simulador difiere del sistema real en:
- **Autenticación**: No requiere credenciales
- **Seguridad**: HTTP en lugar de HTTPS
- **Validación**: Menos restrictiva que el sistema real
- **Perfiles**: Subconjunto de perfiles Dyaku cargados

**IMPORTANTE**: No utilizar este servidor en producción. Solo para desarrollo y pruebas.

## Perfiles FHIR Dyaku Incluidos

- PacientePe
- OrganizacionPe
- PractitionerPe
- EncounterPe
- ConditionPe
- AlergiaPe
- MedicationStatementPe

Ver más en: [`context/DYAKU_FHIR_CONTEXT.md`](context/DYAKU_FHIR_CONTEXT.md)

## Scripts Útiles

### populate_test_data.py

Puebla el servidor con datos de prueba realistas.

**Uso**:
```bash
py populate_test_data.py
```

### verify_cloned_data.py

Verifica los recursos cargados en el servidor.

**Uso**:
```bash
py verify_cloned_data.py
```

## Documentación

- [Contexto Dyaku FHIR](context/DYAKU_FHIR_CONTEXT.md): Perfiles y estándares peruanos
- [Contexto HAPI FHIR](context/CONTEXTO_HAPI_FHIR.md): Configuración técnica del servidor

## Referencias

- [HAPI FHIR Documentation](https://hapifhir.io/hapi-fhir/docs/)
- [HL7 FHIR R4](https://hl7.org/fhir/R4/)
- [Dyaku MINSA](https://dyaku.minsa.gob.pe/fhir)

## Licencia

Este simulador es parte del proyecto SIH.SALUS y se utiliza exclusivamente para desarrollo y testing.

---

**Versión**: 1.0.0  
**Última Actualización**: Noviembre 2025  
**Uso**: Solo Desarrollo y Pruebas
