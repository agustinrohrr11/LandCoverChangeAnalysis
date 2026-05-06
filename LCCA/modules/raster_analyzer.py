# RasterAnalyzer es un módulo que se encarga de analizar las imágenes satelitales obtenidas por el SatelliteProvider en el bounding box obtenido por el AreaManager. #

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

class RasterAnalyzer:
    def __init__(self, matriz):
        # Guardamos la matriz original
        self.data = matriz.astype(np.float32)

    def normalizar(self):
        """
        Transforma los valores de 0-65535 a 0.0-1.0 para que sean 
        más fáciles de procesar y visualizar.
        """
        mini = np.min(self.data)
        maxi = np.max(self.data)
        if maxi - mini == 0:
            return self.data
        return (self.data - mini) / (maxi - mini)

    def generar_mascara_umbral(self, umbral):
        """
        Crea una matriz binaria (0 y 1). 
        Sirve para detectar cosas: 'Si el valor es mayor a X, es cemento'.
        """
        # Esto devuelve True donde se cumple y False donde no
        mascara = self.data > umbral
        return mascara.astype(np.uint8) * 255

    def obtener_estadisticas(self):
        return {
            "media": np.mean(self.data),
            "max": np.max(self.data),
            "min": np.min(self.data),
            "desviacion": np.std(self.data)
        }
    
    def generar_heatmap_colorizado(self, matriz, colormap="hot", normalizar=True):
        """
        Convierte una matriz en imagen RGB colorizadas usando un colormap.
        
        Args:
            matriz: array numpy 2D con valores numéricos
            colormap: nombre del colormap matplotlib ('hot', 'viridis', 'RdYlGn', etc)
            normalizar: si True, normaliza la matriz a rango [0, 1]
            
        Returns:
            imagen RGB uint8 (H x W x 3)
        """
        matriz = matriz.astype(np.float32)
        
        if normalizar:
            mini = np.min(matriz)
            maxi = np.max(matriz)
            if maxi - mini > 0:
                matriz_norm = (matriz - mini) / (maxi - mini)
            else:
                matriz_norm = np.zeros_like(matriz)
        else:
            matriz_norm = matriz
        
        # Obtener el colormap
        cmap = cm.get_cmap(colormap)
        
        # Aplicar el colormap
        # cmap toma valores en [0, 1] y retorna RGBA
        imagen_rgba = cmap(matriz_norm)
        
        # Convertir a RGB uint8 (ignorar canal alpha)
        imagen_rgb = (imagen_rgba[:, :, :3] * 255).astype(np.uint8)
        
        return imagen_rgb