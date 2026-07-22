"""Load local ArcGIS paths for Next Gen FAA (Fire Action Assessment) scripts.

Copy config/paths.example.yaml → config/paths.local.yaml and edit.
Uses a tiny flat-YAML reader so ArcGIS Pro does not need PyYAML.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # src/lib/paths.py → repo root
CONFIG_DIR = REPO_ROOT / "config"
LOCAL_PATHS = CONFIG_DIR / "paths.local.yaml"
EXAMPLE_PATHS = CONFIG_DIR / "paths.example.yaml"


def _parse_flat_yaml(text: str) -> dict[str, str]:
    """Parse simple `key: value` YAML (no nesting). Comments and blanks ignored."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        out[key] = val
    return out


def load_paths(path: Path | None = None) -> dict[str, str]:
    """Load paths.local.yaml, or fall back to the example with a warning."""
    target = path or LOCAL_PATHS
    if not target.exists():
        if EXAMPLE_PATHS.exists():
            print(
                f"WARNING: {target.name} not found. Using {EXAMPLE_PATHS.name}. "
                "Copy it to paths.local.yaml and set your Pro/local paths.",
                file=sys.stderr,
            )
            target = EXAMPLE_PATHS
        else:
            raise FileNotFoundError(
                f"Missing {LOCAL_PATHS}. Copy config/paths.example.yaml to paths.local.yaml."
            )
    cfg = _parse_flat_yaml(target.read_text(encoding="utf-8"))
    # Resolve relative filesystem paths against repo root (not field names / flags)
    path_keys = {
        "workspace",
        "hexes",
        "aoi",
        "wrtc_housing_unit_risk",
        "wrtc_housing_unit_exposure",
        "wrtc_housing_unit_density",
        "wrtc_risk_reduction_zones",
        "wrtc_risk_to_homes",
        "wrtc_housing_exposure",
        "landfire_evt",
        "landfire_bps",
        "mfri_table",
        "whp",
        "burn_probability",
        "padus",
        "resilient_lands",
        "plantations",
        "infrastructure",
        "mills",
        "silvis_wui",
        "disturbances_dir",
        "output_hex_dir",
        "output_hex_geojson",
        "output_hex_csv",
    }
    for key in path_keys:
        val = cfg.get(key, "")
        if not val:
            continue
        if val.startswith(("C:", "D:", "E:", "F:", "G:", "/", "\\\\")):
            continue
        cfg[key] = str((REPO_ROOT / val).resolve())
    cfg["_repo_root"] = str(REPO_ROOT)
    cfg["_config_dir"] = str(CONFIG_DIR)
    return cfg


def require_arcpy():
    """Import arcpy or exit with a clear message (scripts are meant for ArcGIS Pro)."""
    try:
        import arcpy  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "arcpy is required. Run these scripts from ArcGIS Pro Python "
            "(Python window, Notebook, or Pro’s python.exe)."
        ) from exc
    return arcpy


def ensure_output_dir(cfg: dict[str, str]) -> Path:
    out = Path(cfg.get("output_hex_dir") or (REPO_ROOT / "outputs" / "hex"))
    out.mkdir(parents=True, exist_ok=True)
    return out
