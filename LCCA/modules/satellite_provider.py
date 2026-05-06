# SatelliteProvider es un módulo que se encarga de obtener imágenes satelitales de las fuentes. #

import pystac_client
import odc.stac
import rasterio
import planetary_computer as pc
import numpy as np
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
        
        items = list(search.items())
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
    
    def buscar_series_historicas(self, bbox_busqueda, num_imagenes=10, fecha_inicio="2024-01-01", fecha_fin="2025-12-31"):
        """
        Busca múltiples imágenes (serie temporal) en el rango de fechas especificado.
        Retorna lista de items ordenados cronológicamente.
        """
        search = self.catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox_busqueda,
            datetime=f"{fecha_inicio}/{fecha_fin}",
            query={"eo:cloud_cover": {"lt": 5}},
            sortby=[{"field": "properties.datetime", "direction": "asc"}]  # De más antiguo a más reciente
        )
        
        items = list(search.items())
        if not items:
            raise Exception(f"No se encontraron imágenes sin nubes entre {fecha_inicio} y {fecha_fin}")
        
        # Si hay más imágenes de las solicitadas, tomamos una muestra uniforme
        if len(items) > num_imagenes:
            indices = np.linspace(0, len(items) - 1, num_imagenes, dtype=int)
            items = [items[i] for i in indices]
        
        return items
    
    def descargar_serie_completa(self, items, area_manager, bandas=["B04", "B11"]):
        """
        Descarga múltiples bandas para una serie de imágenes.
        Retorna diccionario: {fecha: {banda: matriz}}
        """
        serie_dict = {}
        
        for idx, item in enumerate(items, 1):
            # Extraer fecha del item
            fecha_str = item.properties.get("datetime", "").split("T")[0]
            print(f"Descargando imagen {idx}/{len(items)} ({fecha_str})...", end=" ")
            
            try:
                item_firmado = pc.sign(item)
                bandas_descargadas = {}
                
                for banda in bandas:
                    if banda not in item_firmado.assets:
                        print(f"\n⚠️  Banda {banda} no disponible para {fecha_str}")
                        continue
                    
                    url_banda = item_firmado.assets[banda].href
                    
                    with rasterio.open(url_banda) as src:
                        crs_de_la_imagen = src.crs
                        bbox_corregido = area_manager.obtener_bbox_en_crs(crs_de_la_imagen)
                        ventana = from_bounds(*bbox_corregido, transform=src.transform)
                        data = src.read(1, window=ventana)
                        bandas_descargadas[banda] = data
                
                if bandas_descargadas:
                    serie_dict[fecha_str] = bandas_descargadas
                    print("✅")
                else:
                    print("❌ (sin bandas)")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
        
        if not serie_dict:
            raise Exception("No se pudo descargar ninguna imagen de la serie")
        
        return serie_dict