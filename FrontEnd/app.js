let map;
let mapInitialized = false;
let paraderosData = null;
let primerPuntoSeleccionado = null;

document.addEventListener("DOMContentLoaded", () => {
    // Elementos del DOM
    const toggleBtn = document.getElementById("toggleMapBtn");
    const mapContainer = document.getElementById("map-container");
    const paraderoCount = document.getElementById("paraderoCount");
    
    // Precargar datos de paraderos
    precargarParaderos();
    
    // Evento del botón para mostrar/ocultar mapa
    toggleBtn.addEventListener("click", () => {

        if (mapContainer.classList.contains("map-hidden")) {
            // Mostrar mapa
            mapContainer.classList.remove("map-hidden");
            mapContainer.classList.add("map-visible");
            toggleBtn.textContent = "Ocultar Mapa";
            
            // Inicializar mapa si no existe
            if (!mapInitialized) {
                inicializarMapa();
            } else {
                // Forzar actualización del tamaño del mapa
                setTimeout(() => {
                    if (map) map.invalidateSize();
                }, 100);
            }
        } else {
            // Ocultar mapa
            mapContainer.classList.remove("map-visible");
            mapContainer.classList.add("map-hidden");
            toggleBtn.textContent = "🗺️ Ver Mapa de Paraderos";
        }
    });
    
    // Actualizar contador cuando se carguen los datos
    setTimeout(() => {
        if (paraderosData && paraderosData.features) {
            paraderoCount.textContent = paraderosData.features.length;
        }
    }, 1000);
});

async function precargarParaderos() {
    try {
        const response = await fetch("http://localhost:8000/api/paraderos/puente-aranda/mapa");
        paraderosData = await response.json();
        
        // Actualizar contador
        const paraderoCount = document.getElementById("paraderoCount");
        if (paraderoCount && paraderosData.features) {
            paraderoCount.textContent = paraderosData.features.length;
        }
    } catch (e) {
        console.error("Error precargando datos:", e);
        document.getElementById("paraderoCount").textContent = "Error";
    }
}

function inicializarMapa() {
    // Tu código original del mapa
    map = L.map("map").setView([4.6097, -74.0817], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
    }).addTo(map);

    // Si ya tenemos los datos precargados, usarlos
    if (paraderosData) {
        cargarParaderosAlMapa();
    } else {
        // Si no, cargarlos ahora
        cargarParaderos();
    }
    
    mapInitialized = true;
}

// Tu función cargarParaderos modificada
async function cargarParaderos() {
    try {
        if (!paraderosData) {
            const response = await fetch("http://localhost:8000/api/paraderos/puente-aranda/mapa");
            paraderosData = await response.json();
        }
        
        cargarParaderosAlMapa();

    } catch (e) {
        console.error("Error cargando GeoJSON:", e);
    }
}

// Nueva función para agregar paraderos al mapa
function cargarParaderosAlMapa() {
    // Es buena práctica limpiar capas previas si la función se llama varias veces
    if (window.capaParaderos) {
        map.removeLayer(window.capaParaderos);
    }

    window.capaParaderos = L.geoJSON(paraderosData, {
        pointToLayer: (feature, latlng) => {
            return L.circleMarker(latlng, {
                radius: 7,
                fillColor: "#8604ea",
                color: "#000",
                weight: 1,
                fillOpacity: 0.9
            });
        },
       onEachFeature: (feature, layer) => {
    // Mantienes tu tooltip pequeño
    layer.bindTooltip(`${feature.properties.nombre}`, {
        permanent: true,
        direction: 'top',
        className: 'label-paradero-mini',
        offset: [0, -1],
        opacity: 0.8
    });

    // Nueva lógica de clic para distancia
    layer.on('click', async (e) => {
    const nombreActual = feature.properties.nombre;
    const coordsActuales = e.latlng;

    if (!primerPuntoSeleccionado) {
        // --- PRIMER PUNTO ---
        primerPuntoSeleccionado = { nombre: nombreActual, coords: coordsActuales };
        layer.setStyle({ fillColor: '#00FF00', radius: 10 }); // Resaltar en verde
        alert(`Origen fijado: ${nombreActual}\nAhora selecciona el destino.`);
    } else {
        // --- SEGUNDO PUNTO: CÁLCULO REAL ---
        const start = primerPuntoSeleccionado.coords;
        const end = coordsActuales;

        // Llamada al API de OSRM para obtener la ruta por calles
        const url = `https://router.project-osrm.org/route/v1/driving/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full&geometries=geojson`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.routes && data.routes.length > 0) {
                const ruta = data.routes[0];
                const distanciaKm = (ruta.distance / 1000).toFixed(2);
                const duracionMin = Math.round(ruta.duration / 60);

                // Dibujar la línea de la ruta en el mapa (opcional)
                const routeLine = L.geoJSON(ruta.geometry, {
                    style: { color: '#8604ea', weight: 5, opacity: 0.7 }
                }).addTo(map);

                alert(`📍 Distancia Real por Calles:\n\n` +
                      `De: ${primerPuntoSeleccionado.nombre}\n` +
                      `A: ${nombreActual}\n\n` +
                      `🚗 Distancia: ${distanciaKm} km\n` +
                      `⏱️ Tiempo estimado: ${duracionMin} min`);
            }
        } catch (error) {
            console.error("Error al calcular ruta:", error);
            alert("No se pudo calcular la ruta por calles.");
        }


        primerPuntoSeleccionado = null;
    }
});
    
}
    }).addTo(map);
}