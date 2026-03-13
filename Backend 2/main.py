from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
from typing import Optional  

# Crear la aplicación FastAPI (¡Esto falta!)
app = FastAPI()

# Modelo Pydantic para los paraderos
class Paradero(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float
    direccion: Optional[str] = None
    via: Optional[str] = None
    cenefa: Optional[str] = None

def cargar_geojson_paraderos_bogota():
    """
    Esta funcion carga el archivo GeoJSON con todos los paraderos de bogota por medio
    de la libreria json, se lee el archivo en codificacion utf-8
    """
    try:
        with open('paraderos.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"features": []}

datos_paraderos_bogota = cargar_geojson_paraderos_bogota()

@app.get("/api/paraderos/puente-aranda/mapa")
def procesar_paraderos_pruente_aranda_geojson():
    """
    Formato GeoJSON listo para usar en mapas (Leaflet, Mapbox, etc)
    """
    features = []
    
    for feature in datos_paraderos_bogota.get('features', []):
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