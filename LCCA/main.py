from modules.area_manager import AreaManager
from modules.satellite_provider import SatelliteProvider
from modules.raster_analyzer import RasterAnalyzer
from modules.timeseries_analyzer import TimeSeriesAnalyzer
import imageio
import numpy as np
import os


def crear_carpeta_si_no_existe(ruta):
    """Crea una carpeta si no existe."""
    if not os.path.exists(ruta):
        os.makedirs(ruta)
        print(f"📁 Carpeta creada: {ruta}")


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

def procesar_analisis_multitemporal(mi_zona, num_imagenes=10, fecha_inicio="2024-01-01", fecha_fin="2025-12-31"):
    """
    Descarga serie temporal de imágenes y genera dos heatmaps:
    - Heatmap Acumulativo: cambio total (última - primera)
    - Heatmap Tendencia: tasa de cambio a lo largo del tiempo
    """
    print(f"\n🛰️  ANÁLISIS MULTITEMPORAL - Descargando {num_imagenes} imágenes ({fecha_inicio} a {fecha_fin})")
    print(f"📍 Zona: Lat={mi_zona.lat}, Lon={mi_zona.lon}, Radio={mi_zona.radio_m/1000}km")
    print("=" * 70)
    
    # Paso 1: Descargar serie temporal
    prov = SatelliteProvider()
    bbox = mi_zona.obtener_bbox_latlon()
    
    print(f"\n📡 Buscando {num_imagenes} imágenes sin nubes...")
    items = prov.buscar_series_historicas(bbox, num_imagenes=num_imagenes, 
                                         fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    print(f"✅ Encontradas {len(items)} imágenes")
    
    print(f"\n⬇️  Descargando bandas B04 (Rojo) y B11 (SWIR)...")
    serie_dict = prov.descargar_serie_completa(items, mi_zona, bandas=["B04", "B11"])
    print(f"\n✅ Serie completa descargada: {len(serie_dict)} imágenes")
    
    # Paso 2: Analizar con TimeSeriesAnalyzer
    print(f"\n🔬 Analizando serie temporal...")
    fechas_ordenadas = sorted(serie_dict.keys())
    analyzer_ts = TimeSeriesAnalyzer(serie_dict, fechas_ordenadas)
    
    # Calcular NDBI
    print("  - Calculando NDBI (Índice Normalizado de Construcción)...")
    ndbi_dict = analyzer_ts.calcular_ndbi_serie()
    
    # Detectar cambios
    print("  - Calculando cambios acumulativos...")
    cambio_acumulativo = analyzer_ts.detectar_cambios_acumulativo(ndbi_dict)
    
    print("  - Calculando tendencias de cambio...")
    cambio_tendencia = analyzer_ts.detectar_cambios_tendencia(ndbi_dict)
    
    # Obtener estadísticas
    resumen = analyzer_ts.obtener_resumen_cambios(cambio_acumulativo, cambio_tendencia)
    
    # Paso 3: Generar heatmaps colorizados
    print(f"\n🎨 Generando heatmaps colorizados...")
    
    # Crear carpeta timeseries si no existe
    carpeta_timeseries = "LCCA/images/timeseries"
    crear_carpeta_si_no_existe(carpeta_timeseries)
    
    # Heatmap acumulativo
    analyzer_viz = RasterAnalyzer(cambio_acumulativo)
    heatmap_acum_rgb = analyzer_viz.generar_heatmap_colorizado(cambio_acumulativo, colormap="coolwarm", normalizar=True)
    ruta_acum = f"{carpeta_timeseries}/heatmap_acumulativo.png"
    imageio.imwrite(ruta_acum, heatmap_acum_rgb)
    print(f"  ✅ {ruta_acum}")
    
    # Heatmap tendencia
    heatmap_tend_rgb = analyzer_viz.generar_heatmap_colorizado(cambio_tendencia, colormap="hot", normalizar=True)
    ruta_tend = f"{carpeta_timeseries}/heatmap_tendencia.png"
    imageio.imwrite(ruta_tend, heatmap_tend_rgb)
    print(f"  ✅ {ruta_tend}")
    
    # Paso 4: Imprimir resumen
    print(f"\n📊 RESUMEN DE ANÁLISIS")
    print("=" * 70)
    print(f"Período: {fechas_ordenadas[0]} a {fechas_ordenadas[-1]}")
    print(f"Total de imágenes procesadas: {len(fechas_ordenadas)}")
    
    print(f"\n📈 Cambio Acumulativo (NDBI última - primera):")
    print(f"   Media: {resumen['acumulativo']['media']:.4f}")
    print(f"   Std:   {resumen['acumulativo']['std']:.4f}")
    print(f"   Min:   {resumen['acumulativo']['min']:.4f}")
    print(f"   Max:   {resumen['acumulativo']['max']:.4f}")
    
    print(f"\n📉 Tendencia (pendiente de cambio por día):")
    print(f"   Media: {resumen['tendencia']['media']:.6f}")
    print(f"   Std:   {resumen['tendencia']['std']:.6f}")
    print(f"   Min:   {resumen['tendencia']['min']:.6f}")
    print(f"   Max:   {resumen['tendencia']['max']:.6f}")
    
    print(f"\n📋 Fechas de imágenes descargadas:")
    for i, fecha in enumerate(fechas_ordenadas, 1):
        print(f"   {i:2d}. {fecha}")
    
    print("\n✅ Análisis multitemporal completado con éxito")
    print("=" * 70)

def run():
    """Ejecuta el análisis. Descomenta la línea que desees usar."""
    
    # Definir zona de interés
    mi_zona = AreaManager(lat=-31.82, lon=-60.51, radio_km=1)
    
    # OPCIÓN 1: Análisis simple (imagen más reciente)
    """
    Descarga la imagen más reciente y genera un análisis simple (promedios).
    """
    # print("\n🟢 ANÁLISIS SIMPLE - Imagen más reciente")
    # print("=" * 70)
    # prov = SatelliteProvider()
    # item = prov.buscar_imagen_reciente(mi_zona.obtener_bbox_latlon())
    # matriz_cruda = prov.descargar_ventana(item, mi_zona, banda="B04")
    # analyzer = RasterAnalyzer(matriz_cruda)
    # procesar_visualizacion(analyzer)
    # imprimir_metricas(analyzer)


    # OPCIÓN 2: Análisis multitemporal (descomentar para usar)
    """        
    Interpretación:

    Heatmap Acumulativo:
    🔴 Rojo intenso = Ganó mucha reflectancia en total (urbanización)
    🔵 Celeste intenso = Perdió mucha reflectancia (regeneración de vegetación)
    ⚪ Blanco = Sin cambios significativos
    Pregunta que responde: "¿Cuánto cambió la zona entre enero 2024 y diciembre 2025?"

    Heatmap Tendencia:
    🔴 Rojo = Cambio positivo consistente (urbanización gradual)
    🟤 Negro/Marrón = Estable (sin cambios)
    🟡 Amarillo claro = Cambio muy leve pero persistente
    Pregunta que responde: "¿A qué velocidad cambió la zona de forma constante?"

    """
    print("\n🟢 ANÁLISIS MULTITEMPORAL")
    procesar_analisis_multitemporal(mi_zona, num_imagenes=10, 
                                    fecha_inicio="2024-01-01", 
                                    fecha_fin="2025-12-31")

if __name__ == "__main__":
    run()