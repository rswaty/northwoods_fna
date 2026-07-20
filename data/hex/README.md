# WFE hexes (vectors — OK to commit)

Copy the existing Northwoods WFE hexes here (or keep them only in the Pro GDB and point `config/paths.local.yaml` at that feature class).

Expected source (prior repo, read-only): `inputs/northwoods_wfe.shp`  
Fields used in v1: `GRID_ID`, `MEAN`, `WFE_CAT` (~6,895 hexes @ ~10,000 acres).

WFE is the landscape hazard/exposure surface. People risk comes from WRTC Housing Unit Risk (joined in Pro), not from regenerating hexes.

Do **not** regenerate hexes for v1.
