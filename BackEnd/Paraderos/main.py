from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="API Paraderos Bogotá", 
              description="Consulta paraderos de Puente Aranda")

# Configurar CORS para que el frontend pueda consumir la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambia esto por tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo Pydantic para los paraderos
class Paradero(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float
    direccion: Optional[str] = None
    via: Optional[str] = None
    cenefa: Optional[str] = None

# Cargar datos al iniciar la API
def cargar_paraderos():
    try:
        with open('paraderos.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"features": []}

datos_bogota = cargar_paraderos()

@app.get("/")
def read_root():
    return {
        "mensaje": "API de Paraderos de Bogotá",
        "endpoints": {
            "puente_aranda": "/api/paraderos/puente-aranda",
            "puente_aranda_mapa": "/api/paraderos/puente-aranda/mapa",
            "buscar": "/api/paraderos/buscar?nombre=xxx"
        }
    }

def buscar_paraderos_por_localidad(localidad_codigo: int) -> List[Paradero]:
    paraderos = []
    
    for feature in datos_bogota.get('features', []):
        attrs = feature.get('attributes', {})
        
        if attrs.get('localidad_') == localidad_codigo:
            paradero = Paradero(
                id=attrs.get('objectid', 0),
                nombre=attrs.get('nombre_par', 'Sin nombre'),
                latitud=attrs.get('latitud_pa', 0.0),
                longitud=attrs.get('longitud_p', 0.0),
                direccion=attrs.get('direccion_'),
                via=attrs.get('via_parade'),
                cenefa=attrs.get('cenefa_par')
            )
            paraderos.append(paradero)
    
    return paraderos

@app.get("/api/paraderos/puente-aranda", response_model=List[Paradero])
def get_paraderos_puente_aranda():
    """
    Devuelve todos los paraderos de Puente Aranda (localidad 16)
    """
    paraderos = buscar_paraderos_por_localidad(16)
    
    if not paraderos:
        raise HTTPException(status_code=404, detail="No se encontraron paraderos en Puente Aranda")
    
    return paraderos

@app.get("/api/paraderos/teusaquillo", response_model=List[Paradero])
def get_paraderos_teusaquillo():
    """
    Devuelve todos los paraderos de Teusaquillo (localidad 13)
    """
    paraderos = buscar_paraderos_por_localidad(13)
    
    if not paraderos:
        raise HTTPException(status_code=404, detail="No se encontraron paraderos en Teusaquillo")
    
    return paraderos

@app.get("/api/paraderos/martires", response_model=List[Paradero])
def get_paraderos_martires():
    """
    Devuelve todos los paraderos de Martires (localidad 14)
    """
    paraderos = buscar_paraderos_por_localidad(14)
    
    if not paraderos:
        raise HTTPException(status_code=404, detail="No se encontraron paraderos en Martires")
    
    return paraderos

@app.get("/api/paraderos/puente-aranda/mapa")
def get_paraderos_mapa():
    """
    Formato GeoJSON listo para usar en mapas (Leaflet, Mapbox, etc)
    """
    features = []
    
    for feature in datos_bogota.get('features', []):
        attrs = feature.get('attributes', {})
        
        if attrs.get('localidad_') == 16:
            geo_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        attrs.get('longitud_p', 0.0),
                        attrs.get('latitud_pa', 0.0)
                    ]
                },
                "properties": {
                    "id": attrs.get('objectid'),
                    "nombre": attrs.get('nombre_par'),
                    "direccion": attrs.get('direccion_'),
                    "cenefa": attrs.get('cenefa_par'),
                    "tiene_panel": attrs.get('panel_para') == "SI",
                    "tiene_audio": attrs.get('audio_para') == "SI"
                }
            }
            features.append(geo_feature)
    
    return {
        "type": "FeatureCollection",
        "name": "Paraderos_Puente_Aranda",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features
    }

@app.get("/api/paraderos/buscar")
def buscar_paraderos(nombre: str = ""):
    """
    Busca paraderos por nombre en Puente Aranda
    """
    if not nombre:
        raise HTTPException(status_code=400, detail="Debes especificar un nombre para buscar")
    
    resultados = []
    
    for feature in datos_bogota.get('features', []):
        attrs = feature.get('attributes', {})
        
        if attrs.get('localidad_') == 16:
            nombre_paradero = attrs.get('nombre_par', '').lower()
            if nombre.lower() in nombre_paradero:
                resultados.append({
                    "id": attrs.get('objectid'),
                    "nombre": attrs.get('nombre_par'),
                    "latitud": attrs.get('latitud_pa'),
                    "longitud": attrs.get('longitud_p'),
                    "direccion": attrs.get('direccion_')
                })
    
    return {
        "resultados": resultados,
        "total": len(resultados)
    }

@app.get("/api/paraderos/estadisticas/puente-aranda")
def get_estadisticas():
    """
    Estadísticas básicas de los paraderos en Puente Aranda
    """
    total = 0
    con_panel = 0
    con_audio = 0
    
    for feature in datos_bogota.get('features', []):
        attrs = feature.get('attributes', {})
        
        if attrs.get('localidad_') == 16:
            total += 1
            if attrs.get('panel_para') == "SI":
                con_panel += 1
            if attrs.get('audio_para') == "SI":
                con_audio += 1
    
    return {
        "localidad": "Puente Aranda",
        "codigo": 16,
        "total_paraderos": total,
        "con_panel_informativo": con_panel,
        "con_audio": con_audio,
        "sin_panel": total - con_panel
    }

# Esta parte es para ejecutar con "python main.py"
if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API de Paraderos de Puente Aranda...")
    print("📝 Documentación disponible en: http://localhost:8000/docs")
    print("📍 Endpoint principal: http://localhost:8000/api/paraderos/puente-aranda")
    uvicorn.run(app, host="0.0.0.0", port=8000)