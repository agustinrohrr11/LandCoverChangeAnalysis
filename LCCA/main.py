from modules.area_manager import AreaManager
from modules.satellite_provider import SatelliteProvider
from modules.raster_analyzer import RasterAnalyzer # <--- Nuevo
import imageio
import numpy as np


def generar_imagen_analisis():
    ##### imagen satelital de un área específica #####

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



def imprimir_resumen_pixeles():

    # 1. Ubicación
    mi_zona = AreaManager(lat=-31.82, lon=-60.51, radio_km=1)
    
    # 2. Obtención de datos
    prov = SatelliteProvider()
    item = prov.buscar_imagen_reciente(mi_zona.obtener_bbox_latlon())
    matriz_cruda = prov.descargar_ventana(item, mi_zona, banda="B04")
    
    # 3. ANÁLISIS (Aquí empieza la magia)
    analyzer = RasterAnalyzer(matriz_cruda)
        
    #####    Para no saturar la consola, imprimimos solo un resumen de los valores    #####
    #        Tomamos una muestra de los valores para no saturar la consola
    print(f"Valor mínimo de reflexión: {np.min(analyzer.data)}")
    print(f"Valor máximo de reflexión: {np.max(analyzer.data)}")
    print(f"Promedio de brillo en Oro Verde: {np.mean(analyzer.data):.2f}")


if __name__ == "__main__":

   generar_imagen_analisis()
   imprimir_resumen_pixeles()
