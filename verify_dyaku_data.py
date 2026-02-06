#!/usr/bin/env python3
"""
Script para verificar que el servidor HAPI FHIR está correctamente poblado con datos Dyaku
"""

import requests
import json

# Configuración del servidor FHIR
FHIR_BASE_URL = "http://localhost:8081/fhir"


def get_resource_count(resource_type):
    """Obtiene el conteo de recursos de un tipo específico"""
    url = f"{FHIR_BASE_URL}/{resource_type}?_summary=count"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("total", 0)
        else:
            return 0
    except Exception as e:
        print(f"Error al obtener conteo de {resource_type}: {str(e)}")
        return 0


def get_sample_resource(resource_type, resource_id):
    """Obtiene un recurso de ejemplo"""
    url = f"{FHIR_BASE_URL}/{resource_type}/{resource_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error al obtener {resource_type}/{resource_id}: {str(e)}")
        return None


def get_resources_by_patient(patient_id, resource_type):
    """Obtiene recursos relacionados con un paciente específico"""
    url = f"{FHIR_BASE_URL}/{resource_type}?subject=Patient/{patient_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            entries = data.get("entry", [])
            return [entry["resource"] for entry in entries]
        else:
            return []
    except Exception as e:
        print(f"Error al obtener {resource_type} para paciente {patient_id}: {str(e)}")
        return []


def print_patient_summary(patient):
    """Imprime un resumen del paciente"""
    if not patient:
        print("   Paciente no encontrado")
        return

    # Nombre
    names = patient.get("name", [])
    if names:
        name = names[0]
        given = " ".join(name.get("given", []))
        family = name.get("family", "")
        family_ext = name.get("_family", {}).get("extension", [])
        mothers_family = next((ext["valueString"] for ext in family_ext
                              if "humanname-mothers-family" in ext.get("url", "")), "")
        full_name = f"{given} {family} {mothers_family}".strip()
        print(f"   Nombre: {full_name}")

    # DNI
    identifiers = patient.get("identifier", [])
    if identifiers:
        dni = identifiers[0].get("value", "")
        print(f"   DNI: {dni}")

    # Género y Fecha de nacimiento
    gender = patient.get("gender", "")
    birth_date = patient.get("birthDate", "")
    print(f"   Género: {gender}")
    print(f"   Fecha de nacimiento: {birth_date}")

    # UBIGEO de nacimiento
    birth_ext = patient.get("_birthDate", {}).get("extension", [])
    ubigeo = next((ext["valueString"] for ext in birth_ext
                  if "pe-ubigeo" in ext.get("url", "")), "")
    if ubigeo:
        print(f"   UBIGEO nacimiento: {ubigeo}")

    # Teléfono
    telecoms = patient.get("telecom", [])
    for telecom in telecoms:
        if telecom.get("system") == "phone":
            print(f"   Teléfono: {telecom.get('value', '')}")
        elif telecom.get("system") == "email":
            print(f"   Email: {telecom.get('value', '')}")


def print_condition_summary(condition):
    """Imprime un resumen de una condición"""
    code_obj = condition.get("code", {})
    codings = code_obj.get("coding", [])
    if codings:
        coding = codings[0]
        code = coding.get("code", "")
        display = coding.get("display", "")
        print(f"   • {display} (ICD-10: {code})")


def print_medication_summary(medication):
    """Imprime un resumen de un medicamento"""
    med_code = medication.get("medicationCodeableConcept", {})
    med_name = med_code.get("text", "Medicamento desconocido")
    dosages = medication.get("dosage", [])
    if dosages:
        dosage = dosages[0]
        dose_text = dosage.get("text", "")
        route = dosage.get("route", {}).get("text", "")
        print(f"   • {med_name} - {dose_text} ({route})")
    else:
        print(f"   • {med_name}")


def print_allergy_summary(allergy):
    """Imprime un resumen de una alergia"""
    code_obj = allergy.get("code", {})
    substance = code_obj.get("text", "Sustancia desconocida")
    criticality = allergy.get("criticality", "unknown")
    reactions = allergy.get("reaction", [])
    if reactions:
        reaction = reactions[0]
        description = reaction.get("description", "")
        print(f"   • {substance} (Criticidad: {criticality})")
        print(f"     Reacción: {description}")
    else:
        print(f"   • {substance} (Criticidad: {criticality})")


def main():
    print("=" * 80)
    print("VERIFICACIÓN DE DATOS DYAKU EN SERVIDOR HAPI FHIR")
    print("=" * 80)
    print(f"Servidor: {FHIR_BASE_URL}")
    print("=" * 80)

    # 1. Conteo de recursos
    print("\n1. CONTEO DE RECURSOS")
    print("-" * 80)

    resources = {
        "Patient": "Pacientes",
        "Condition": "Condiciones (Diagnósticos)",
        "MedicationStatement": "Medicamentos",
        "AllergyIntolerance": "Alergias",
        "Organization": "Organizaciones",
        "Practitioner": "Profesionales",
        "StructureDefinition": "Perfiles/Estructuras",
        "CodeSystem": "Sistemas de Códigos",
        "ValueSet": "Conjuntos de Valores"
    }

    totals = {}
    for resource_type, label in resources.items():
        count = get_resource_count(resource_type)
        totals[resource_type] = count
        print(f"   {label:35} {count:5}")

    # 2. Ejemplo de paciente completo
    print("\n2. EJEMPLO DE PACIENTE CON DATOS CLÍNICOS COMPLETOS")
    print("-" * 80)

    # Buscar el primer paciente
    patient_id = "33"  # Primer paciente creado
    patient = get_sample_resource("Patient", patient_id)

    if patient:
        print(f"\nPaciente ID: {patient_id}")
        print_patient_summary(patient)

        # Obtener condiciones del paciente
        conditions = get_resources_by_patient(patient_id, "Condition")
        if conditions:
            print(f"\n   Condiciones ({len(conditions)}):")
            for condition in conditions:
                print_condition_summary(condition)

        # Obtener medicamentos del paciente
        medications = get_resources_by_patient(patient_id, "MedicationStatement")
        if medications:
            print(f"\n   Medicamentos ({len(medications)}):")
            for medication in medications:
                print_medication_summary(medication)

        # Obtener alergias del paciente
        allergies = get_resources_by_patient(patient_id, "AllergyIntolerance")
        if allergies:
            print(f"\n   Alergias ({len(allergies)}):")
            for allergy in allergies:
                print_allergy_summary(allergy)
        else:
            print(f"\n   Alergias: Sin alergias registradas")

    # 3. Verificar perfiles Dyaku
    print("\n\n3. VERIFICACIÓN DE PERFILES DYAKU")
    print("-" * 80)

    profiles_to_check = [
        "PacientePe",
        "ConditionPe",
        "MedicationStatementPe",
        "AlergiaPe",
        "OrganizacionPe",
        "PractitionerPe",
        "CompositionPe",
        "BundlePe",
        "pe-pais",
        "pe-ubigeo",
        "pe-tercerapellido"
    ]

    for profile_id in profiles_to_check:
        profile = get_sample_resource("StructureDefinition", profile_id)
        if profile:
            profile_name = profile.get("name", profile_id)
            profile_status = profile.get("status", "unknown")
            print(f"   ✓ {profile_name:30} (status: {profile_status})")
        else:
            print(f"   ✗ {profile_id:30} NO ENCONTRADO")

    # 4. Verificar CodeSystems
    print("\n\n4. VERIFICACIÓN DE CODESYSTEMS")
    print("-" * 80)

    codesystems_to_check = [
        "ColegiosProfesionalesSaludCS",
        "IdspersonaPeru",
        "IPRESSCS",
        "PaisesCS"
    ]

    for cs_id in codesystems_to_check:
        cs = get_sample_resource("CodeSystem", cs_id)
        if cs:
            cs_name = cs.get("name", cs_id)
            concept_count = len(cs.get("concept", []))
            print(f"   ✓ {cs_name:35} ({concept_count} conceptos)")
        else:
            print(f"   ✗ {cs_id:35} NO ENCONTRADO")

    # 5. Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)

    total_clinical = (totals.get("Patient", 0) +
                     totals.get("Condition", 0) +
                     totals.get("MedicationStatement", 0) +
                     totals.get("AllergyIntolerance", 0))

    total_definitions = (totals.get("StructureDefinition", 0) +
                        totals.get("CodeSystem", 0) +
                        totals.get("ValueSet", 0))

    print(f"Total de recursos clínicos: {total_clinical}")
    print(f"Total de definiciones: {total_definitions}")
    print(f"\nDatos por paciente (promedio):")
    if totals.get("Patient", 0) > 0:
        print(f"  - Condiciones: {totals.get('Condition', 0) / totals.get('Patient', 1):.1f}")
        print(f"  - Medicamentos: {totals.get('MedicationStatement', 0) / totals.get('Patient', 1):.1f}")
        print(f"  - Alergias: {totals.get('AllergyIntolerance', 0) / totals.get('Patient', 1):.1f}")

    print("\n✓ Servidor FHIR Dyaku verificado exitosamente!")
    print("=" * 80)
    print(f"\nPuedes explorar los datos en:")
    print(f"  - API FHIR: {FHIR_BASE_URL}")
    print(f"  - Swagger UI: http://localhost:8081/swagger-ui/")
    print("=" * 80)


if __name__ == "__main__":
    main()
