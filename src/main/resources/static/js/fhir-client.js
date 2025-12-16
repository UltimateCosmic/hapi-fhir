// Cliente FHIR para consumir la API del servidor
const fhirClient = {
    baseUrl: '/fhir',
    
    // Método para hacer búsquedas en recursos FHIR
    async search(resourceType, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `${this.baseUrl}/${resourceType}${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(url, {
            headers: {
                'Accept': 'application/fhir+json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    },
    
    // Método para obtener un recurso por ID
    async read(resourceType, id) {
        const url = `${this.baseUrl}/${resourceType}/${id}`;
        
        const response = await fetch(url, {
            headers: {
                'Accept': 'application/fhir+json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    },
    
    // Formatear fecha
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return dateString;
            
            return date.toLocaleDateString('es-PE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } catch (e) {
            return dateString;
        }
    },
    
    // Obtener nombre completo de un HumanName
    getHumanName(nameArray) {
        if (!nameArray || nameArray.length === 0) return 'Sin nombre';
        
        const name = nameArray[0];
        const given = name.given ? name.given.join(' ') : '';
        const family = name.family || '';
        
        return `${given} ${family}`.trim() || 'Sin nombre';
    }
};

// Funciones auxiliares globales para profesionales.html y otros
async function fetchFHIRResources(resourceType, params = {}) {
    try {
        return await fhirClient.search(resourceType, params);
    } catch (error) {
        console.error('Error fetching FHIR resources:', error);
        console.error('URL intentada:', `${fhirClient.baseUrl}/${resourceType}`);
        console.error('Detalles del error:', error.message);
        return null;
    }
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '<p>Cargando datos desde el servidor FHIR...</p>';
    }
}

function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
}

function showNoData(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '<div class="alert alert-info">No se encontraron registros en el servidor.</div>';
    }
}

function getIdentifier(identifiers) {
    if (!identifiers || identifiers.length === 0) return 'N/A';
    return identifiers[0].value || 'N/A';
}

function getHumanName(nameArray) {
    return fhirClient.getHumanName(nameArray);
}

// Funciones auxiliares para formatear datos
function formatName(nameArray) {
    if (!nameArray || nameArray.length === 0) return 'Sin nombre';
    const name = nameArray[0];
    const given = name.given ? name.given.join(' ') : '';
    const family = name.family || '';
    return `${given} ${family}`.trim() || name.text || 'Sin nombre';
}

function formatGender(gender) {
    const genderMap = {
        'male': 'Masculino',
        'female': 'Femenino',
        'other': 'Otro',
        'unknown': 'Desconocido'
    };
    return genderMap[gender] || gender || 'N/A';
}

function formatIdentifier(identifiers) {
    if (!identifiers || identifiers.length === 0) return 'N/A';
    
    // Buscar DNI primero
    const dni = identifiers.find(id => 
        id.system && id.system.includes('dni')
    );
    
    if (dni && dni.value) return dni.value;
    
    // Si no hay DNI, devolver el primer identificador
    return identifiers[0].value || 'N/A';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        return date.toLocaleDateString('es-PE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

function formatCodeableConcept(concept) {
    if (!concept) return 'N/A';
    if (concept.text) return concept.text;
    if (concept.coding && concept.coding.length > 0) {
        return concept.coding[0].display || concept.coding[0].code || 'N/A';
    }
    return 'N/A';
}

function formatAddress(addressArray) {
    if (!addressArray || addressArray.length === 0) return 'N/A';
    const addr = addressArray[0];
    
    // Si hay texto completo, usarlo
    if (addr.text) return addr.text;
    
    // Construir dirección desde componentes
    let parts = [];
    if (addr.line && addr.line.length > 0) {
        parts.push(addr.line.join(', '));
    }
    if (addr.city) parts.push(addr.city);
    if (addr.state) parts.push(addr.state);
    if (addr.country) parts.push(addr.country);
    
    return parts.length > 0 ? parts.join(', ') : 'N/A';
}

function formatTelecom(telecomArray, type) {
    if (!telecomArray || telecomArray.length === 0) return 'N/A';
    
    // Buscar por tipo específico (phone, email, etc.)
    if (type) {
        const filtered = telecomArray.filter(t => t.system === type);
        if (filtered.length > 0) {
            return filtered[0].value || 'N/A';
        }
    }
    
    // Si no se especifica tipo, devolver el primero disponible
    return telecomArray[0].value || 'N/A';
}

function formatStatus(status) {
    const statusMap = {
        'active': 'Activo',
        'inactive': 'Inactivo',
        'completed': 'Completado',
        'suspended': 'Suspendido'
    };
    return statusMap[status] || status || 'N/A';
}
