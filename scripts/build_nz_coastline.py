"""Build the packaged NZ coastline file from the LINZ coastline and islands polygons."""

from pathlib import Path
from typing import Annotated

import geopandas as gpd
import typer

from qcore import cli
from region_geo import LATLON, get_region

app = typer.Typer(pretty_exceptions_enable=False)

# Coastline groups that sit across 180 degrees and are left out by default
OUTLYING_GROUPS = ("Chatham", "Kermadec")
OUTPUT_FFP = get_region("nz").coastline_path


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
    gdf["outlying"] = gdf["grp_name"].fillna("").str.contains("|".join(OUTLYING_GROUPS))
    gdf = gdf.rename(columns={"grp_name": "group"})
    return gdf[["name", "group", "outlying", "geometry"]].to_crs(LATLON)


@cli.from_docstring(app)
def build_nz_coastline(
    coastline_ffp: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output_ffp: Annotated[Path, typer.Option(dir_okay=False)] = OUTPUT_FFP,
):
    """
    Build the NZ coastline file.

    Parameters
    ----------
    coastline_ffp : Path
        LINZ nz-coastlines-and-islands-polygons-topo-150k file
    output_ffp : Path, optional
        Output GeoPackage, by default the packaged region_geo/data/nz_coastline.gpkg
    """
    gdf = build_coastline(coastline_ffp)
    output_ffp.unlink(missing_ok=True)
    gdf.to_file(output_ffp, driver="GPKG", layer="coastline")
    print(f"{output_ffp}: {len(gdf)} polygons")


if __name__ == "__main__":
    app()
