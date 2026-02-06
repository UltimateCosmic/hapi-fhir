#!/usr/bin/env python3
"""
Script para poblar el servidor HAPI FHIR con datos completos del sistema Dyaku
Incluye: Pacientes, Condiciones (diagnósticos), Medicamentos, Alergias, Organizaciones, y Profesionales
"""

import requests
import json
import random
from datetime import datetime, timedelta

# Configuración del servidor FHIR
FHIR_BASE_URL = "http://localhost:8081/fhir"

# Datos realistas peruanos
NOMBRES_MASCULINOS = [
    "Juan Carlos", "José Luis", "Miguel Angel", "Carlos Alberto", "Luis Fernando",
    "Pedro Pablo", "Jorge Luis", "Francisco Javier", "Roberto Carlos", "Diego Armando",
    "Andrés Felipe", "Daniel Eduardo", "Marco Antonio", "César Augusto", "Raúl Enrique"
]

NOMBRES_FEMENINOS = [
    "María Elena", "Ana Lucía", "Rosa María", "Carmen Julia", "Patricia Isabel",
    "Gloria Estela", "Silvia Beatriz", "Martha Cecilia", "Teresa de Jesús", "Claudia Alejandra",
    "Gabriela Sofia", "Mónica Andrea", "Verónica Paola", "Sandra Milena", "Diana Carolina"
]

APELLIDOS_PATERNOS = [
    "García", "Rodríguez", "González", "Fernández", "López",
    "Martínez", "Sánchez", "Pérez", "Ramírez", "Torres",
    "Flores", "Rivera", "Gómez", "Díaz", "Cruz",
    "Morales", "Reyes", "Gutiérrez", "Ortiz", "Chávez"
]

APELLIDOS_MATERNOS = [
    "Silva", "Mendoza", "Castillo", "Vargas", "Herrera",
    "Medina", "Rojas", "Paredes", "Vega", "Castro",
    "Quispe", "Mamani", "Huamán", "Condori", "Yana",
    "Puma", "Apaza", "Ccahuana", "Túpac", "Yupanqui"
]

# UBIGEOs de ciudades principales de Perú
UBIGEOS = {
    "Lima": "150101",
    "Callao": "070101",
    "Arequipa": "040101",
    "Trujillo": "130101",
    "Chiclayo": "140101",
    "Piura": "200101",
    "Cusco": "080101",
    "Iquitos": "160101",
    "Huancayo": "120101",
    "Tacna": "230101"
}

# Condiciones médicas comunes con códigos ICD-10
CONDICIONES_ICD10 = [
    {"code": "E11.9", "display": "Diabetes mellitus tipo 2 sin complicaciones"},
    {"code": "I10", "display": "Hipertensión esencial (primaria)"},
    {"code": "J45.9", "display": "Asma no especificada"},
    {"code": "M54.5", "display": "Dolor lumbar"},
    {"code": "E78.5", "display": "Hiperlipidemia no especificada"},
    {"code": "K21.9", "display": "Enfermedad por reflujo gastroesofágico sin esofagitis"},
    {"code": "M79.3", "display": "Paniculitis no especificada"},
    {"code": "E66.9", "display": "Obesidad no especificada"},
    {"code": "F32.9", "display": "Episodio depresivo no especificado"},
    {"code": "F41.9", "display": "Trastorno de ansiedad no especificado"},
    {"code": "K29.7", "display": "Gastritis no especificada"},
    {"code": "M25.5", "display": "Dolor articular"},
    {"code": "R51", "display": "Cefalea"},
    {"code": "J06.9", "display": "Infección aguda de las vías respiratorias superiores"},
    {"code": "N39.0", "display": "Infección de vías urinarias"},
    {"code": "E04.9", "display": "Bocio no tóxico no especificado"},
    {"code": "D50.9", "display": "Anemia por deficiencia de hierro"},
    {"code": "B35.9", "display": "Dermatofitosis no especificada"},
    {"code": "L20.9", "display": "Dermatitis atópica no especificada"},
    {"code": "H52.1", "display": "Miopía"}
]

# Medicamentos comunes
MEDICAMENTOS = [
    {"nombre": "Metformina 850mg", "dosis": "1 tableta cada 12 horas", "via": "Oral"},
    {"nombre": "Enalapril 10mg", "dosis": "1 tableta cada 24 horas", "via": "Oral"},
    {"nombre": "Atorvastatina 20mg", "dosis": "1 tableta cada 24 horas", "via": "Oral"},
    {"nombre": "Omeprazol 20mg", "dosis": "1 cápsula cada 24 horas", "via": "Oral"},
    {"nombre": "Salbutamol inhalador 100mcg", "dosis": "2 inhalaciones cada 6 horas PRN", "via": "Inhalatoria"},
    {"nombre": "Paracetamol 500mg", "dosis": "1-2 tabletas cada 8 horas PRN", "via": "Oral"},
    {"nombre": "Ibuprofeno 400mg", "dosis": "1 tableta cada 8 horas", "via": "Oral"},
    {"nombre": "Losartán 50mg", "dosis": "1 tableta cada 24 horas", "via": "Oral"},
    {"nombre": "Levotiroxina 100mcg", "dosis": "1 tableta cada 24 horas en ayunas", "via": "Oral"},
    {"nombre": "Fluoxetina 20mg", "dosis": "1 cápsula cada 24 horas", "via": "Oral"},
    {"nombre": "Amoxicilina 500mg", "dosis": "1 cápsula cada 8 horas por 7 días", "via": "Oral"},
    {"nombre": "Clotrimazol crema 1%", "dosis": "Aplicar 2 veces al día", "via": "Tópica"},
    {"nombre": "Sulfato ferroso 300mg", "dosis": "1 tableta cada 24 horas", "via": "Oral"},
    {"nombre": "Loratadina 10mg", "dosis": "1 tableta cada 24 horas", "via": "Oral"},
    {"nombre": "Insulina glargina 100UI/ml", "dosis": "20 UI cada 24 horas subcutánea", "via": "Subcutánea"}
]

# Alergias comunes
ALERGIAS = [
    {"sustancia": "Penicilina", "reaccion": "Erupción cutánea generalizada", "criticidad": "high"},
    {"sustancia": "Aspirina (AAS)", "reaccion": "Urticaria y prurito", "criticidad": "high"},
    {"sustancia": "Ibuprofeno", "reaccion": "Angioedema", "criticidad": "high"},
    {"sustancia": "Sulfonamidas", "reaccion": "Síndrome de Stevens-Johnson", "criticidad": "high"},
    {"sustancia": "Mariscos", "reaccion": "Anafilaxia", "criticidad": "high"},
    {"sustancia": "Nueces", "reaccion": "Urticaria y dificultad respiratoria", "criticidad": "high"},
    {"sustancia": "Látex", "reaccion": "Dermatitis de contacto", "criticidad": "low"},
    {"sustancia": "Polen", "reaccion": "Rinitis alérgica", "criticidad": "low"},
    {"sustancia": "Ácaros del polvo", "reaccion": "Asma bronquial", "criticidad": "low"},
    {"sustancia": "Codeína", "reaccion": "Náuseas y vómitos", "criticidad": "low"}
]

# Organizaciones de salud (IPRESS)
ORGANIZACIONES = [
    {
        "id": "00031361",
        "nombre": "Hospital Nacional Dos de Mayo",
        "ciudad": "Lima",
        "tipo": "Hospital nivel III"
    },
    {
        "id": "00012345",
        "nombre": "Centro de Salud San Juan de Miraflores",
        "ciudad": "Lima",
        "tipo": "Centro de Salud nivel I-4"
    },
    {
        "id": "00023456",
        "nombre": "Hospital Regional Honorio Delgado",
        "ciudad": "Arequipa",
        "tipo": "Hospital nivel III"
    },
    {
        "id": "00034567",
        "nombre": "Hospital Belén de Trujillo",
        "ciudad": "Trujillo",
        "tipo": "Hospital nivel III"
    },
    {
        "id": "00045678",
        "nombre": "Policlínico Santa Rosa",
        "ciudad": "Callao",
        "tipo": "Policlínico nivel II"
    }
]

# Profesionales de salud
PROFESIONALES = [
    {"nombre": "Carlos", "apellido": "Mendoza Silva", "colegio": "01", "numero_colegio": "045231"},
    {"nombre": "Ana María", "apellido": "García Torres", "colegio": "06", "numero_colegio": "032145"},
    {"nombre": "José Luis", "apellido": "Rodríguez Pérez", "colegio": "01", "numero_colegio": "056789"},
    {"nombre": "Patricia", "apellido": "Flores Quispe", "colegio": "06", "numero_colegio": "041256"},
    {"nombre": "Miguel Angel", "apellido": "Sánchez Vargas", "colegio": "01", "numero_colegio": "067234"},
    {"nombre": "Rosa", "apellido": "Fernández Mamani", "colegio": "05", "numero_colegio": "023456"},
    {"nombre": "Luis Fernando", "apellido": "López Castro", "colegio": "02", "numero_colegio": "034567"},
    {"nombre": "Carmen", "apellido": "Martínez Huamán", "colegio": "08", "numero_colegio": "012345"}
]


def generar_dni():
    """Genera un DNI peruano de 8 dígitos"""
    return str(random.randint(10000000, 99999999))


def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento entre 1940 y 2020"""
    start_date = datetime(1940, 1, 1)
    end_date = datetime(2020, 12, 31)
    time_between = end_date - start_date
    random_days = random.randrange(time_between.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")


def generar_fecha_reciente(dias_atras=365):
    """Genera una fecha reciente (último año)"""
    fecha = datetime.now() - timedelta(days=random.randint(0, dias_atras))
    return fecha.strftime("%Y-%m-%d")


def crear_organizacion(org_data):
    """Crea un recurso Organization (OrganizacionPe)"""
    ciudad = org_data["ciudad"]
    ubigeo = UBIGEOS.get(ciudad, "150101")

    organization = {
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/OrganizacionPe"]
        },
        "identifier": [{
            "type": {
                "coding": [{
                    "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/IPRESSCS",
                    "code": org_data["id"]
                }]
            },
            "value": org_data["id"]
        }],
        "active": True,
        "type": [{
            "text": org_data["tipo"]
        }],
        "name": org_data["nombre"],
        "address": [{
            "extension": [{
                "url": "https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/pe-ubigeo",
                "valueString": ubigeo
            }],
            "city": ciudad,
            "country": "PE"
        }]
    }
    return organization


def crear_profesional(prof_data):
    """Crea un recurso Practitioner (PractitionerPe)"""
    practitioner = {
        "resourceType": "Practitioner",
        "meta": {
            "profile": ["https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/PractitionerPe"]
        },
        "identifier": [{
            "type": {
                "extension": [{
                    "url": "https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/pe-pais",
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/PaisesCS",
                            "code": "PER",
                            "display": "Perú"
                        }]
                    }
                }],
                "coding": [{
                    "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/IdspersonaPeru",
                    "code": "1",
                    "display": "DNI"
                }]
            },
            "value": generar_dni()
        }],
        "name": [{
            "family": prof_data["apellido"],
            "given": [prof_data["nombre"]]
        }],
        "qualification": [{
            "identifier": [{
                "value": prof_data["numero_colegio"]
            }],
            "code": {
                "coding": [{
                    "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/ColegiosProfesionalesSaludCS",
                    "code": prof_data["colegio"]
                }]
            }
        }]
    }
    return practitioner


def crear_paciente(genero):
    """Crea un recurso Patient (PacientePe)"""
    es_masculino = genero == "male"
    nombre = random.choice(NOMBRES_MASCULINOS if es_masculino else NOMBRES_FEMENINOS)
    apellido_paterno = random.choice(APELLIDOS_PATERNOS)
    apellido_materno = random.choice(APELLIDOS_MATERNOS)
    apellido_tercero = random.choice(APELLIDOS_MATERNOS) if random.random() > 0.7 else None

    ciudad_nacimiento = random.choice(list(UBIGEOS.keys()))
    ubigeo_nacimiento = UBIGEOS[ciudad_nacimiento]

    family_extensions = [
        {
            "url": "https://hl7.org/fhir/StructureDefinition/humanname-mothers-family",
            "valueString": apellido_materno
        }
    ]

    if apellido_tercero:
        family_extensions.append({
            "url": "https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/pe-tercerapellido",
            "valueString": apellido_tercero
        })

    patient = {
        "resourceType": "Patient",
        "meta": {
            "profile": ["https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/PacientePe"]
        },
        "identifier": [{
            "type": {
                "extension": [{
                    "url": "https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/pe-pais",
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/PaisesCS",
                            "code": "PER",
                            "display": "Perú"
                        }]
                    }
                }],
                "coding": [{
                    "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/IdspersonaPeru",
                    "code": "1",
                    "display": "DNI"
                }]
            },
            "value": generar_dni()
        }],
        "name": [{
            "family": apellido_paterno,
            "_family": {
                "extension": family_extensions
            },
            "given": nombre.split()
        }],
        "telecom": [
            {
                "system": "phone",
                "value": f"+51 9{random.randint(10000000, 99999999)}"
            },
            {
                "system": "email",
                "value": f"{nombre.lower().replace(' ', '.')}.{apellido_paterno.lower()}@email.com"
            }
        ],
        "gender": genero,
        "birthDate": generar_fecha_nacimiento(),
        "_birthDate": {
            "extension": [
                {
                    "url": "https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/pe-pais",
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "https://www.gob.pe/minsa/RENHICE/fhir/CodeSystem/PaisesCS",
                            "code": "PER",
                            "display": "Perú"
                        }]
                    }
                },
                {
                    "url": "https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/pe-ubigeo",
                    "valueString": ubigeo_nacimiento
                }
            ]
        }
    }
    return patient


def crear_condicion(patient_ref, severidad="moderate"):
    """Crea un recurso Condition (ConditionPe)"""
    condicion_data = random.choice(CONDICIONES_ICD10)
    fecha_inicio = generar_fecha_reciente(730)  # Últimos 2 años

    condition = {
        "resourceType": "Condition",
        "meta": {
            "profile": ["https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/ConditionPe"]
        },
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": "confirmed"
            }]
        },
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": condicion_data["code"],
                "display": condicion_data["display"]
            }],
            "text": condicion_data["display"]
        },
        "subject": {
            "reference": patient_ref
        },
        "onsetPeriod": {
            "start": fecha_inicio
        },
        "note": [{
            "text": f"Paciente diagnosticado con {condicion_data['display']}. En seguimiento y tratamiento."
        }]
    }
    return condition


def crear_medicamento(patient_ref):
    """Crea un recurso MedicationStatement (MedicationStatementPe)"""
    med_data = random.choice(MEDICAMENTOS)
    fecha_prescripcion = generar_fecha_reciente(180)

    medication_statement = {
        "resourceType": "MedicationStatement",
        "meta": {
            "profile": ["https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/MedicationStatementPe"]
        },
        "status": "active",
        "medicationCodeableConcept": {
            "text": med_data["nombre"]
        },
        "subject": {
            "reference": patient_ref
        },
        "effectiveDateTime": fecha_prescripcion,
        "dosage": [{
            "text": med_data["dosis"],
            "route": {
                "text": med_data["via"]
            }
        }]
    }
    return medication_statement


def crear_alergia(patient_ref):
    """Crea un recurso AllergyIntolerance (AlergiaPe)"""
    alergia_data = random.choice(ALERGIAS)
    fecha_inicio = generar_fecha_reciente(1825)  # Últimos 5 años

    allergy = {
        "resourceType": "AllergyIntolerance",
        "meta": {
            "profile": ["https://www.gob.pe/minsa/RENHICE/fhir/StructureDefinition/AlergiaPe"]
        },
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                "code": "active"
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                "code": "confirmed"
            }]
        },
        "type": "allergy",
        "category": ["medication" if "penicilina" in alergia_data["sustancia"].lower() or
                     "aspirina" in alergia_data["sustancia"].lower() else "food"],
        "criticality": alergia_data["criticidad"],
        "code": {
            "text": alergia_data["sustancia"]
        },
        "patient": {
            "reference": patient_ref
        },
        "onsetDateTime": fecha_inicio,
        "reaction": [{
            "description": alergia_data["reaccion"],
            "severity": "severe" if alergia_data["criticidad"] == "high" else "mild"
        }]
    }
    return allergy


def post_resource(resource):
    """Envía un recurso al servidor FHIR"""
    resource_type = resource["resourceType"]
    url = f"{FHIR_BASE_URL}/{resource_type}"

    headers = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json"
    }

    try:
        response = requests.post(url, json=resource, headers=headers)
        if response.status_code in [200, 201]:
            result = response.json()
            resource_id = result.get("id")
            print(f"✓ {resource_type} creado: {resource_id}")
            return f"{resource_type}/{resource_id}"
        else:
            print(f"✗ Error al crear {resource_type}: {response.status_code}")
            print(f"  Respuesta: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"✗ Excepción al crear {resource_type}: {str(e)}")
        return None


def poblar_servidor(num_pacientes=20):
    """Función principal para poblar el servidor"""
    print("=" * 80)
    print("POBLANDO SERVIDOR HAPI FHIR CON DATOS DYAKU")
    print("=" * 80)

    # 1. Crear organizaciones
    print("\n1. Creando organizaciones de salud...")
    org_refs = []
    for org_data in ORGANIZACIONES:
        org = crear_organizacion(org_data)
        org_ref = post_resource(org)
        if org_ref:
            org_refs.append(org_ref)

    print(f"\n   Total organizaciones creadas: {len(org_refs)}")

    # 2. Crear profesionales
    print("\n2. Creando profesionales de salud...")
    prof_refs = []
    for prof_data in PROFESIONALES:
        prof = crear_profesional(prof_data)
        prof_ref = post_resource(prof)
        if prof_ref:
            prof_refs.append(prof_ref)

    print(f"\n   Total profesionales creados: {len(prof_refs)}")

    # 3. Crear pacientes con datos clínicos
    print(f"\n3. Creando {num_pacientes} pacientes con datos clínicos completos...")
    patient_refs = []

    for i in range(num_pacientes):
        genero = random.choice(["male", "female"])
        print(f"\n   --- Paciente {i+1}/{num_pacientes} ---")

        # Crear paciente
        patient = crear_paciente(genero)
        patient_ref = post_resource(patient)

        if not patient_ref:
            continue

        patient_refs.append(patient_ref)

        # Crear 1-3 condiciones por paciente
        num_condiciones = random.randint(1, 3)
        for j in range(num_condiciones):
            condition = crear_condicion(patient_ref)
            post_resource(condition)

        # Crear 1-4 medicamentos por paciente
        num_medicamentos = random.randint(1, 4)
        for j in range(num_medicamentos):
            medication = crear_medicamento(patient_ref)
            post_resource(medication)

        # 50% de probabilidad de tener alergias (1-2)
        if random.random() > 0.5:
            num_alergias = random.randint(1, 2)
            for j in range(num_alergias):
                allergy = crear_alergia(patient_ref)
                post_resource(allergy)

    print("\n" + "=" * 80)
    print("RESUMEN DE DATOS CREADOS:")
    print("=" * 80)
    print(f"Organizaciones: {len(org_refs)}")
    print(f"Profesionales: {len(prof_refs)}")
    print(f"Pacientes: {len(patient_refs)}")
    print(f"Condiciones: ~{len(patient_refs) * 2} (promedio 2 por paciente)")
    print(f"Medicamentos: ~{len(patient_refs) * 2.5} (promedio 2.5 por paciente)")
    print(f"Alergias: ~{len(patient_refs) * 0.75} (promedio 0.75 por paciente)")
    print("=" * 80)
    print("\nServidor FHIR poblado exitosamente!")
    print(f"\nPuedes verificar los datos en: {FHIR_BASE_URL}")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    # Permitir especificar número de pacientes como argumento
    num_pacientes = 20
    if len(sys.argv) > 1:
        try:
            num_pacientes = int(sys.argv[1])
        except ValueError:
            print("Uso: python populate_dyaku_data.py [número_de_pacientes]")
            sys.exit(1)

    poblar_servidor(num_pacientes)
