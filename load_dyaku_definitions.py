#!/usr/bin/env python3
"""
Script para cargar definiciones de Dyaku (Perfiles, CodeSystems, ValueSets) al servidor HAPI FHIR
"""

import requests
import json
import os

# Configuración del servidor FHIR
FHIR_BASE_URL = "http://localhost:8081/fhir"

# Rutas a los archivos de definición
DYAKU_DIR = "/home/u.hsc.dev/hapi-fhir/dyaku"
CODESYSTEM_FILE = os.path.join(DYAKU_DIR, "CodeSystem.json")
VALUESET_FILE = os.path.join(DYAKU_DIR, "ValueSet.json")
STRUCTUREDEFINITION_FILE = os.path.join(DYAKU_DIR, "StructureDefinition.json")


def load_json_file(filepath):
    """Carga un archivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"✗ Error al leer {filepath}: {str(e)}")
        return None


def post_resource(resource):
    """Envía un recurso al servidor FHIR usando PUT para permitir actualizaciones"""
    resource_type = resource.get("resourceType")
    resource_id = resource.get("id")

    if not resource_type or not resource_id:
        print(f"✗ Recurso inválido: falta resourceType o id")
        return False

    # Usar PUT para crear/actualizar con ID específico
    url = f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"

    headers = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }

    try:
        response = requests.put(url, json=resource, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✓ {resource_type}/{resource_id} cargado exitosamente")
            return True
        else:
            print(f"✗ Error al cargar {resource_type}/{resource_id}: {response.status_code}")
            print(f"  Respuesta: {response.text[:300]}")
            return False
    except Exception as e:
        print(f"✗ Excepción al cargar {resource_type}/{resource_id}: {str(e)}")
        return False


def load_bundle(bundle_data):
    """Procesa un Bundle y carga cada recurso individualmente"""
    if bundle_data.get("resourceType") != "Bundle":
        print("✗ El archivo no contiene un Bundle")
        return 0

    entries = bundle_data.get("entry", [])
    total = len(entries)
    success = 0

    for entry in entries:
        resource = entry.get("resource")
        if resource:
            if post_resource(resource):
                success += 1

    return success, total


def main():
    print("=" * 80)
    print("CARGANDO DEFINICIONES DYAKU AL SERVIDOR HAPI FHIR")
    print("=" * 80)
    print(f"Servidor: {FHIR_BASE_URL}")
    print("=" * 80)

    total_success = 0
    total_resources = 0

    # 1. Cargar CodeSystems
    print("\n1. Cargando CodeSystems...")
    print("-" * 80)
    codesystems = load_json_file(CODESYSTEM_FILE)
    if codesystems:
        success, total = load_bundle(codesystems)
        total_success += success
        total_resources += total
        print(f"\n   CodeSystems cargados: {success}/{total}")
    else:
        print("   No se pudieron cargar los CodeSystems")

    # 2. Cargar ValueSets
    print("\n2. Cargando ValueSets...")
    print("-" * 80)
    valuesets = load_json_file(VALUESET_FILE)
    if valuesets:
        success, total = load_bundle(valuesets)
        total_success += success
        total_resources += total
        print(f"\n   ValueSets cargados: {success}/{total}")
    else:
        print("   No se pudieron cargar los ValueSets")

    # 3. Cargar StructureDefinitions
    print("\n3. Cargando StructureDefinitions (Perfiles)...")
    print("-" * 80)
    structuredefs = load_json_file(STRUCTUREDEFINITION_FILE)
    if structuredefs:
        success, total = load_bundle(structuredefs)
        total_success += success
        total_resources += total
        print(f"\n   StructureDefinitions cargados: {success}/{total}")
    else:
        print("   No se pudieron cargar los StructureDefinitions")

    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE CARGA")
    print("=" * 80)
    print(f"Total de recursos cargados: {total_success}/{total_resources}")
    if total_success == total_resources:
        print("✓ Todas las definiciones se cargaron exitosamente!")
    else:
        print(f"⚠ Algunos recursos fallaron: {total_resources - total_success} errores")
    print("=" * 80)
    print(f"\nPuedes verificar las definiciones en: {FHIR_BASE_URL}/metadata")
    print("=" * 80)


if __name__ == "__main__":
    main()
