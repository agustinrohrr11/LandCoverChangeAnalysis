# RasterAnalyzer es un módulo que se encarga de analizar las imágenes satelitales obtenidas por el SatelliteProvider en el bounding box obtenido por el AreaManager. #

import numpy as np

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