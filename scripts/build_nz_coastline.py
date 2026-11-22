"""Build the packaged NZ coastline file from the LINZ coastline and islands polygons."""

import argparse
from pathlib import Path

import geopandas as gpd

# Coastline groups that sit across 180 degrees and are left out by default
OUTLYING_GROUPS = ("Chatham", "Kermadec")
LATLON = "EPSG:4326"
OUTPUT_FFP = Path(__file__).parents[1] / "region_geo" / "data" / "nz_coastline.gpkg"


def build_coastline(coastline_ffp: Path) -> gpd.GeoDataFrame:
    """
    Build the coastline from the LINZ coastline and islands polygons.

    Parameters
    ----------
    coastline_ffp : Path
        LINZ nz-coastlines-and-islands-polygons-topo-150k file

    Returns
    -------
    gpd.GeoDataFrame
        Columns name, group, outlying in EPSG:4326
    """
    gdf = gpd.read_file(coastline_ffp)
    outlying = gdf["grp_name"].fillna("").str.contains("|".join(OUTLYING_GROUPS))
    out = gpd.GeoDataFrame(
        {"name": gdf["name"], "group": gdf["grp_name"], "outlying": outlying},
        geometry=gdf.geometry,
        crs=gdf.crs,
    )
    return out.to_crs(LATLON)


def main():
    """Build the NZ coastline file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coastline", type=Path, help="LINZ coastline gpkg")
    parser.add_argument("--output", type=Path, default=OUTPUT_FFP)
    args = parser.parse_args()

    gdf = build_coastline(args.coastline)
    args.output.unlink(missing_ok=True)
    gdf.to_file(args.output, driver="GPKG", layer="coastline")
    print(f"{args.output}: {len(gdf)} polygons")


if __name__ == "__main__":
    main()
