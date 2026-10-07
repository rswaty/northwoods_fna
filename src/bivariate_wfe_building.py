"""Bivariate 3×3 map: Wildfire Exposure Risk category × WRTC Building Density.

Runs without ArcGIS (geopandas + matplotlib). Reads the exported hex GeoJSON and
writes:
  - outputs/maps/bivariate_wfe_building.png   static map + 3×3 legend
  - outputs/maps/bivariate_wfe_building.gpkg  hexes with BIVAR_* fields; the
    QGIS style is embedded as the layer default, so it opens pre-symbolized
  - outputs/maps/bivariate_wfe_building.qml   same style (Layer → Load Style)

Classes:
  WFE axis      1 = Very Low + Low, 2 = Moderate, 3 = High + Very High (action gate)
  Building axis AOI tertiles of WRTC_BLDG_DENSITY_MEAN (1 = lowest third)
BIVAR_CLASS is "<wfe>-<building>", e.g. "3-3" = High/VH WFE and densest third.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import geopandas as gpd
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
HEX_GJ = REPO / "outputs" / "hex" / "faa_hex_scores.geojson"
OUT_DIR = REPO / "outputs" / "maps"
STEM = "bivariate_wfe_building"
LAYER = STEM

WFE_CLASS = {"Very Low": 1, "Low": 1, "Moderate": 2, "High": 3, "Very High": 3}
WFE_LABELS = {1: "Very Low / Low", 2: "Moderate", 3: "High / Very High"}
BLDG_LABELS = {1: "Low third", 2: "Middle third", 3: "High third"}

# Joshua Stevens 3×3: WFE runs grey → red, buildings grey → blue
COLORS = {
    "1-1": "#e8e8e8", "2-1": "#e4acac", "3-1": "#c85a5a",
    "1-2": "#b0d5df", "2-2": "#ad9ea5", "3-2": "#985356",
    "1-3": "#64acbe", "2-3": "#627f8c", "3-3": "#574249",
}
NODATA_COLOR = "#ffffff"


def classify(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, list[float]]:
    gdf = gdf.copy()
    gdf["BIVAR_WFE"] = gdf["WFE_CAT"].map(WFE_CLASS).astype("Int64")
    bldg = gdf["WRTC_BLDG_DENSITY_MEAN"].astype(float).fillna(0.0)
    cuts = [float(bldg.quantile(1 / 3)), float(bldg.quantile(2 / 3))]
    gdf["BIVAR_BLDG"] = 1 + (bldg > cuts[0]).astype(int) + (bldg > cuts[1]).astype(int)
    gdf["BIVAR_CLASS"] = [
        "nodata" if pd.isna(w) else f"{w}-{b}"
        for w, b in zip(gdf["BIVAR_WFE"], gdf["BIVAR_BLDG"])
    ]
    gdf["BIVAR_COLOR"] = gdf["BIVAR_CLASS"].map(COLORS).fillna(NODATA_COLOR)
    return gdf, cuts


def class_label(key: str) -> str:
    w, b = (int(x) for x in key.split("-"))
    return f"WFE {WFE_LABELS[w]} · Buildings {BLDG_LABELS[b]}"


def draw_png(gdf: gpd.GeoDataFrame, cuts: list[float], path: Path) -> None:
    plot = gdf.to_crs(5070)
    fig, ax = plt.subplots(figsize=(12, 10), dpi=200)
    plot.plot(ax=ax, color=plot["BIVAR_COLOR"], edgecolor="none")
    plot.dissolve().boundary.plot(ax=ax, color="#555555", linewidth=0.4)
    ax.set_axis_off()
    ax.set_title(
        "Wildfire Exposure Risk × Building Density — Northwoods hexes",
        fontsize=14,
        loc="left",
    )

    leg = fig.add_axes([0.06, 0.08, 0.2, 0.2])
    for key, color in COLORS.items():
        w, b = (int(x) for x in key.split("-"))
        leg.add_patch(Rectangle((w - 1, b - 1), 1, 1, facecolor=color, edgecolor="white"))
    leg.set_xlim(0, 3)
    leg.set_ylim(0, 3)
    leg.set_aspect("equal")
    leg.set_xticks([])
    leg.set_yticks([])
    for s in leg.spines.values():
        s.set_visible(False)
    leg.set_xlabel("Wildfire Exposure Risk →", fontsize=9)
    leg.set_ylabel("Building density →", fontsize=9)

    counts = gdf["BIVAR_CLASS"].value_counts()
    note = (
        "WFE: Very Low+Low | Moderate | High+Very High\n"
        f"Buildings (AOI thirds): ≤{cuts[0]:.2f} | ≤{cuts[1]:.2f} | >{cuts[1]:.2f}\n"
        f"High/VH WFE + high-third buildings (3-3): {int(counts.get('3-3', 0))} hexes"
    )
    fig.text(0.29, 0.09, note, fontsize=8, va="bottom", color="#333333")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def _rgba(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},255"


def build_qml() -> str:
    cats, syms = [], []
    for i, (key, color) in enumerate(COLORS.items()):
        cats.append(
            f'      <category value="{key}" symbol="{i}" label="{escape(class_label(key))}" render="true"/>'
        )
        props = {
            "color": _rgba(color),
            "outline_color": "255,255,255,90",
            "outline_style": "solid",
            "outline_width": "0.05",
            "outline_width_unit": "MM",
            "style": "solid",
        }
        opts = "\n".join(
            f'            <Option name="{k}" type="QString" value="{v}"/>' for k, v in props.items()
        )
        legacy = "\n".join(f'          <prop k="{k}" v="{v}"/>' for k, v in props.items())
        syms.append(
            f"""      <symbol type="fill" name="{i}" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" locked="0" pass="0">
          <Option type="Map">
{opts}
          </Option>
{legacy}
        </layer>
      </symbol>"""
        )
    return f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.40" styleCategories="Symbology">
  <renderer-v2 type="categorizedSymbol" attr="BIVAR_CLASS" symbollevels="0" enableorderby="0" forceraster="0">
    <categories>
{chr(10).join(cats)}
    </categories>
    <symbols>
{chr(10).join(syms)}
    </symbols>
  </renderer-v2>
</qgis>
"""


def embed_default_style(gpkg: Path, layer: str, qml: str) -> None:
    """Store the QML in the GeoPackage layer_styles table (QGIS loads it as default)."""
    con = sqlite3.connect(gpkg)
    try:
        geom_col = con.execute(
            "SELECT column_name FROM gpkg_geometry_columns WHERE table_name = ?", (layer,)
        ).fetchone()[0]
        con.execute(
            """CREATE TABLE IF NOT EXISTS layer_styles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                f_table_catalog TEXT(256), f_table_schema TEXT(256),
                f_table_name TEXT(256), f_geometry_column TEXT(256),
                styleName TEXT(30), styleQML TEXT, styleSLD TEXT,
                useAsDefault BOOLEAN, description TEXT, owner TEXT(30),
                ui TEXT(30), update_time DATETIME DEFAULT CURRENT_TIMESTAMP)"""
        )
        con.execute("DELETE FROM layer_styles WHERE f_table_name = ?", (layer,))
        con.execute(
            """INSERT INTO layer_styles (f_table_catalog, f_table_schema, f_table_name,
                f_geometry_column, styleName, styleQML, styleSLD, useAsDefault, description)
               VALUES ('', '', ?, ?, ?, ?, '', 1, 'WFE × building density 3×3')""",
            (layer, geom_col, STEM, qml),
        )
        con.commit()
    finally:
        con.close()


def main() -> None:
    if not HEX_GJ.exists():
        sys.exit(f"Missing {HEX_GJ} — run 05_export_hex_geojson.py first.")
    gdf = gpd.read_file(HEX_GJ)
    for col in ("WFE_CAT", "WRTC_BLDG_DENSITY_MEAN"):
        if col not in gdf.columns:
            sys.exit(f"{col} not in {HEX_GJ.name} — re-run 02 → 05 with building density set.")

    gdf, cuts = classify(gdf)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    keep = [
        "GRID_ID", "WFE_CAT", "MEAN", "WRTC_BLDG_DENSITY_MEAN", "PEOPLE_CAT",
        "ACTION_CLASS", "GOLDILOCKS_PRIORITY",
        "BIVAR_WFE", "BIVAR_BLDG", "BIVAR_CLASS", "BIVAR_COLOR", "geometry",
    ]
    out = gdf[[c for c in keep if c in gdf.columns]]
    gpkg = OUT_DIR / f"{STEM}.gpkg"
    if gpkg.exists():
        gpkg.unlink()
    out.to_file(gpkg, layer=LAYER, driver="GPKG")
    qml = build_qml()
    embed_default_style(gpkg, LAYER, qml)
    (OUT_DIR / f"{STEM}.qml").write_text(qml, encoding="utf-8")

    png = OUT_DIR / f"{STEM}.png"
    draw_png(gdf, cuts, png)

    print(f"Building density thirds: ≤{cuts[0]:.3f} | ≤{cuts[1]:.3f} | >{cuts[1]:.3f}")
    print("Hexes per class (WFE-building):")
    counts = gdf["BIVAR_CLASS"].value_counts()
    for key in COLORS:
        print(f"  {key}: {int(counts.get(key, 0)):5d}  {class_label(key)}")
    if counts.get("nodata"):
        print(f"  nodata: {int(counts['nodata'])} (missing WFE_CAT)")
    print(f"Wrote {png}\nWrote {gpkg} (style embedded)\nWrote {OUT_DIR / (STEM + '.qml')}")


if __name__ == "__main__":
    main()
