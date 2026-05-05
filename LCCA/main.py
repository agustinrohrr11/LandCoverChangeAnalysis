from modules.area_manager import AreaManager
from modules.satellite_provider import SatelliteProvider
from modules.raster_analyzer import RasterAnalyzer
import imageio
import numpy as np


def procesar_visualizacion(analyzer):
    """Recibe el analyzer y genera el archivo visual."""
    matriz_norm = analyzer.normalizar()
    imagen_final = (matriz_norm * 255).astype('uint8')
    imageio.imwrite('LCCA/images/resultado_analisis.png', imagen_final)
    print("✅ Imagen 'resultado_analisis.png' generada con éxito.")

def imprimir_metricas(analyzer):
    """Recibe el analyzer e imprime los números."""
    print(f"\n--- RESUMEN DE PÍXELES ---")
    print(f"Mínimo: {np.min(analyzer.data)}")
    print(f"Máximo: {np.max(analyzer.data)}")
    print(f"Promedio: {np.mean(analyzer.data):.2f}")

def run():
    # descarga
    mi_zona = AreaManager(lat=-31.82, lon=-60.51, radio_km=1)
    prov = SatelliteProvider()
    item = prov.buscar_imagen_reciente(mi_zona.obtener_bbox_latlon())
    matriz_cruda = prov.descargar_ventana(item, mi_zona, banda="B04")
    
    # Analyzer
    analyzer = RasterAnalyzer(matriz_cruda)
    
    # LLAMADAS A FUNCIONES
    procesar_visualizacion(analyzer)
    imprimir_metricas(analyzer)

if __name__ == "__main__":
    run()