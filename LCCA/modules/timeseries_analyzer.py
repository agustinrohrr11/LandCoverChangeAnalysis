# TimeSeriesAnalyzer es un módulo que analiza series temporales de imágenes satelitales para detectar cambios. #

import numpy as np
from datetime import datetime
from scipy import stats

class TimeSeriesAnalyzer:
    """
    Analiza cambios multitemporales en cobertura terrestre.
    Recibe un diccionario de series temporales: {fecha: {banda: matriz}}
    """
    
    def __init__(self, series_dict, fechas_ordenadas):
        """
        Args:
            series_dict: {fecha_string: {banda_string: matriz_numpy}}
            fechas_ordenadas: lista de fechas en orden cronológico (strings o datetime)
        """
        self.series_dict = series_dict
        self.fechas = fechas_ordenadas
        self.num_imagenes = len(fechas_ordenadas)
        
    def calcular_ndbi_serie(self):
        """
        Calcula NDBI (Normalized Difference Built-up Index) para cada fecha.
        NDBI = (B11 - B04) / (B11 + B04)
        
        Nota: B04 (10m) y B11 (20m) tienen diferente resolución en Sentinel-2,
        por lo que se reescala B11 al tamaño de B04.
        """
        from scipy.ndimage import zoom
        
        ndbi_dict = {}
        for fecha in self.fechas:
            if fecha not in self.series_dict:
                continue
                
            bandas = self.series_dict[fecha]
            if "B04" not in bandas or "B11" not in bandas:
                raise ValueError(f"Faltan bandas B04 o B11 para la fecha {fecha}")
            
            b04 = bandas["B04"].astype(np.float32)
            b11 = bandas["B11"].astype(np.float32)
            
            # Si B11 tiene diferente tamaño que B04, reescalarlo
            if b11.shape != b04.shape:
                # Calcular factor de escala
                scale_factor = np.array(b04.shape) / np.array(b11.shape)
                b11 = zoom(b11, scale_factor, order=1)  # Interpolación bilineal
            
            # Evitar división por cero
            denominador = b11 + b04
            denominador[denominador == 0] = 1e-8
            
            ndbi = (b11 - b04) / denominador
            ndbi_dict[fecha] = ndbi
            
        return ndbi_dict
    
    def detectar_cambios_acumulativo(self, ndbi_dict):
        """
        Calcula el cambio acumulativo: última imagen - primera imagen.
        Retorna: matriz con cambios (valores positivos = mayor reflectancia)
        """
        if len(ndbi_dict) < 2:
            raise ValueError("Se necesitan al menos 2 imágenes para análisis de cambios")
        
        fechas_sorted = sorted(ndbi_dict.keys())
        primera = ndbi_dict[fechas_sorted[0]]
        ultima = ndbi_dict[fechas_sorted[-1]]
        
        cambio_acumulativo = ultima - primera
        return cambio_acumulativo
    
    def detectar_cambios_tendencia(self, ndbi_dict):
        """
        Calcula la pendiente (tasa de cambio) pixel-a-pixel a lo largo del tiempo.
        Usa regresión lineal: pendiente de (tiempo vs valor_pixel)
        Retorna: matriz con pendientes (cambio por unidad de tiempo)
        """
        if len(ndbi_dict) < 2:
            raise ValueError("Se necesitan al menos 2 imágenes para análisis de tendencia")
        
        fechas_sorted = sorted(ndbi_dict.keys())
        
        # Convertir fechas a días desde la primera
        tiempos_numericos = []
        for fecha_str in fechas_sorted:
            # Suponemos formato ISO: "2024-01-15" o similar
            try:
                fecha_obj = datetime.fromisoformat(fecha_str.split("T")[0])
            except:
                # Si no es ISO, intentar otros formatos
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
            tiempos_numericos.append(fecha_obj)
        
        # Calcular días desde la primera imagen
        dias = np.array([(t - tiempos_numericos[0]).days for t in tiempos_numericos])
        
        # Obtener forma de una imagen
        primera_img = ndbi_dict[fechas_sorted[0]]
        shape = primera_img.shape
        
        # Para cada píxel, calcular la pendiente
        pendiente_map = np.zeros(shape, dtype=np.float32)
        
        for i in range(shape[0]):
            for j in range(shape[1]):
                valores = np.array([ndbi_dict[f][i, j] for f in fechas_sorted], dtype=np.float32)
                # Regresión lineal: y = a + b*x, donde x=días, y=valor
                slope, _, _, _, _ = stats.linregress(dias, valores)
                pendiente_map[i, j] = slope
        
        return pendiente_map
    
    def obtener_estadisticas_temporal(self, ndbi_dict):
        """
        Retorna estadísticas por fecha.
        """
        stats_dict = {}
        for fecha in sorted(ndbi_dict.keys()):
            ndbi = ndbi_dict[fecha]
            stats_dict[fecha] = {
                "media": np.mean(ndbi),
                "std": np.std(ndbi),
                "min": np.min(ndbi),
                "max": np.max(ndbi)
            }
        return stats_dict
    
    def obtener_resumen_cambios(self, cambio_acumulativo, cambio_tendencia):
        """
        Proporciona un resumen de estadísticas de los dos mapas de cambio.
        """
        return {
            "acumulativo": {
                "media": np.mean(cambio_acumulativo),
                "std": np.std(cambio_acumulativo),
                "min": np.min(cambio_acumulativo),
                "max": np.max(cambio_acumulativo)
            },
            "tendencia": {
                "media": np.mean(cambio_tendencia),
                "std": np.std(cambio_tendencia),
                "min": np.min(cambio_tendencia),
                "max": np.max(cambio_tendencia)
            }
        }
