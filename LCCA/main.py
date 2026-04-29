from modules.area_manager import AreaManager
from modules.satellite_provider import SatelliteProvider
from modules.raster_analyzer import RasterAnalyzer # <--- Nuevo
import imageio

def run():
    # 1. Ubicación
    mi_zona = AreaManager(lat=-31.82, lon=-60.51, radio_km=1)
    
    # 2. Obtención de datos
    prov = SatelliteProvider()
    item = prov.buscar_imagen_reciente(mi_zona.obtener_bbox_latlon())
    matriz_cruda = prov.descargar_ventana(item, mi_zona, banda="B04")
    
    # 3. ANÁLISIS (Aquí empieza la magia)
    analyzer = RasterAnalyzer(matriz_cruda)
    stats = analyzer.obtener_estadisticas()
    
    print(f"Estadísticas del área: {stats}")

    # 4. Generar una imagen para "ver" (Normalizada)
    # Convertimos a 0-255 para que Windows/Mac puedan abrir el archivo
    matriz_norm = analyzer.normalizar()
    imagen_final = (matriz_norm * 255).astype('uint8')
    
    imageio.imwrite('resultado_analisis.png', imagen_final)
    print("Imagen 'resultado_analisis.png' generada con éxito.")

if __name__ == "__main__":
    run()