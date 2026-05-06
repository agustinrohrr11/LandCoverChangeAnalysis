"""
Archivo para ejecutar el ANÁLISIS MULTITEMPORAL.
Este script descarga una serie de 10 imágenes mensuales y genera dos heatmaps
para visualizar cambios en cobertura terrestre.
"""

from modules.area_manager import AreaManager
from main import procesar_analisis_multitemporal

if __name__ == "__main__":
    # Definir zona de interés (Oro Verde, Entre Ríos)
    mi_zona = AreaManager(lat=-31.82, lon=-60.51, radio_km=1)
    
    # Ejecutar análisis multitemporal con los siguientes parámetros:
    # - num_imagenes=10: descargar 10 imágenes (una por mes aprox)
    # - fecha_inicio: enero 2024
    # - fecha_fin: diciembre 2025
    procesar_analisis_multitemporal(
        mi_zona, 
        num_imagenes=10, 
        fecha_inicio="2024-01-01", 
        fecha_fin="2025-12-31"
    )
