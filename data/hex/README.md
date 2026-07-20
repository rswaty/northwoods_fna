# WFE hexes (vectors — OK to commit)

Copy the existing Northwoods WFE hexes here (or keep them only in the Pro GDB and point `config/paths.local.yaml` at that feature class).

Expected source (prior repo, read-only): `inputs/northwoods_wfe.shp`  
Fields used in v1: `GRID_ID`, `MEAN`, `WFE_CAT` (~6,895 hexes @ ~10,000 acres).

Once copied, preferred commit form for sharing: GeoJSON or shapefile components under this folder.
Do **not** regenerate hexes for v1.
