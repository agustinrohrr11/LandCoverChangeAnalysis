# AreaManager recibe coordenadas de dos puntos geográficos y devuelve el bounding box que los contiene. #

from pyproj import Transformer

class AreaManager:
    def __init__(self, lat: float, lon: float, radio_km: float):
        self.lat = lat
        self.lon = lon
        self.radio_m = radio_km * 1000

    def obtener_bbox_en_crs(self, crs_destino):
        """
        Calcula el cuadrado de búsqueda en el sistema de coordenadas
        que la imagen realmente usa (ej. EPSG:32720 o 32721).
        """
        # Creamos el transformador al vuelo según el CRS de la imagen
        transformer = Transformer.from_crs("EPSG:4326", crs_destino, always_xy=True)
        
        # Transformamos el centro
        x, y = transformer.transform(self.lon, self.lat)
        
        # Retornamos los 4 límites (min_x, min_y, max_x, max_y)
        return (x - self.radio_m, y - self.radio_m, x + self.radio_m, y + self.radio_m)

    def obtener_bbox_latlon(self):
        """Para el buscador (STAC) que siempre usa Lat/Lon."""
        # Un margen de ~1.1km aproximado
        return [self.lon - 0.01, self.lat - 0.01, self.lon + 0.01, self.lat + 0.01]