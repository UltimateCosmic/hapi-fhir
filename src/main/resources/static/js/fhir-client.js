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
