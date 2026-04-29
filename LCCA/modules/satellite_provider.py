# SatelliteProvider es un módulo que se encarga de obtener imágenes satelitales de las fuentes. #

import pystac_client
import odc.stac
import rasterio
import planetary_computer as pc
from rasterio.windows import from_bounds

class SatelliteProvider:
    def __init__(self):
        # Usamos el catálogo gratuito de Microsoft (Planetary Computer)
        self.catalog_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
        self.catalog = pystac_client.Client.open(self.catalog_url)

    def buscar_imagen_reciente(self, bbox_busqueda):
        """
        Busca en el catálogo la imagen más nueva de Sentinel-2 sin nubes.
        """
        # Nota: STAC suele pedir el BBOX en Lat/Lon para la búsqueda inicial
        # Pero para simplificar este paso de "aprendizaje", vamos a usar 
        # una búsqueda directa.
        
        search = self.catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox_busqueda, # Busqueda dinamica de BBOX
            datetime="2024-01-01/2024-12-31",
            query={"eo:cloud_cover": {"lt": 5}},
            sortby=[{"field": "properties.datetime", "direction": "desc"}]
        )
        
        items = list(search.get_items())
        if not items:
            raise Exception("No se encontraron imágenes sin nubes.")
            
        return items[0] # Devolvemos la más reciente

    def descargar_ventana(self, item, area_manager, banda="B04"):
            item_firmado = pc.sign(item)
            url_banda = item_firmado.assets[banda].href
            
            with rasterio.open(url_banda) as src:
                # LE PREGUNTAMOS AL ARCHIVO: ¿Cuál es tu sistema?
                crs_de_la_imagen = src.crs
                
                # LE PEDIMOS AL MANAGER: Dame los metros en ese sistema
                bbox_corregido = area_manager.obtener_bbox_en_crs(crs_de_la_imagen)
                
                ventana = from_bounds(*bbox_corregido, transform=src.transform)
                data = src.read(1, window=ventana)
                return data