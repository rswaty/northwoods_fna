# Hex outputs for GitHub Pages / Quarto

Scripts write scored hex layers here. **Commit these** (GeoJSON preferred).

Expected v1 products:
- `faa_hex_scores.geojson` — geometry + `ACTION_CLASS`, `TREATMENT_HINT`, scores, Goldilocks flags
- `faa_hex_scores.csv` — attribute table only (optional companion)

Key fields: `SCORE_PEOPLE` (default ranking), `SCORE_PLANTATION`, `SCORE_PAD`, `SCORE_BALANCED`, `GOLDILOCKS_5`, `GOLDILOCKS_10`, `PEAT_HEX`, `PLANTATION_HEX`, `PADUS_FRAC`, `WRTC_HU_RISK_MEAN`.

Do not put rasters in this folder.
