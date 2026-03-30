import geopandas as gpd
from rasterstats import zonal_stats
import os
import rasterio
import pandas as pd # On ajoute pandas pour le CSV
import numpy as np

# 1. Charger les régions (On a besoin du Shapefile pour le calcul, mais on ne l'exportera pas)
regions = gpd.read_file("Boundaries_admin_level_1/afr_g2014_2013_1_update.shp")
regions['geometry'] = regions['geometry'].buffer(0)

dossier_tiffs = './tiffs/'

# On crée un DataFrame vide qui contiendra nos résultats
# On garde les colonnes d'identification pour la future jointure
df_resultats = pd.DataFrame(regions.drop(columns='geometry')) 

for fichier in os.listdir(dossier_tiffs):
    if fichier.endswith('.tif'):
        chemin_raster = os.path.join(dossier_tiffs, fichier)
        
        with rasterio.open(chemin_raster) as src:
            nodata_val = src.nodata if src.nodata is not None else -9999
            raster_crs = src.crs
        
        # Aligner le CRS
        regions_projected = regions.to_crs(raster_crs) if regions.crs != raster_crs else regions

        print(f"Calcul pour : {fichier}...")

        stats = zonal_stats(
            regions_projected, 
            chemin_raster, 
            stats="mean", 
            nodata=nodata_val
        )
        
        nom_colonne = fichier.replace('.tif', '')
        nom_colonne = nom_colonne.replace('chirps-v2.0.', 'prec_')
        
        # Nettoyage et ajout au DataFrame
        df_resultats[nom_colonne] = [
            s['mean'] if (s['mean'] is not None and s['mean'] > -9000) else np.nan 
            for s in stats
        ]

# 2. Export final en CSV (beaucoup plus léger)
df_resultats.to_csv("stats_precipitations_afrique.csv", index=False, encoding='utf-8')
print("Terminé ! Fichier CSV généré.")