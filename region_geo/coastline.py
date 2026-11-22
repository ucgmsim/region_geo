"""Load region coastlines and test which points are on land."""

from functools import lru_cache

import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry

from region_geo.regions import get_region

# WGS84 latitude / longitude, the CRS of the stored coastline files
LATLON = "EPSG:4326"


@lru_cache(maxsize=8)
def _read_coastline(region_key: str) -> gpd.GeoDataFrame:
    """
    Read a coastline file once per process.

    Parameters
    ----------
    region_key : str
        Region key

    Returns
    -------
    gpd.GeoDataFrame
        Coastline polygons in EPSG:4326
    """
    return gpd.read_file(get_region(region_key).coastline_path).to_crs(LATLON)


def get_coastline(
    region: str | None = None,
    include_outlying: bool = False,
    bbox: tuple[float, float, float, float] | None = None,
    crs: str = LATLON,
) -> gpd.GeoDataFrame:
    """
    Get the coastline (land) polygons of a region.

    Parameters
    ----------
    region : str, optional
        Region key, by default None (uses the default region)
    include_outlying : bool, optional
        Include outlying islands, by default False
        For NZ these are the Chatham and Kermadec Islands, which sit across 180 degrees
    bbox : tuple[float, float, float, float], optional
        Clip to (min lon, min lat, max lon, max lat), by default None
    crs : str, optional
        CRS of the returned polygons, by default EPSG:4326

    Returns
    -------
    gpd.GeoDataFrame
        Land polygons with columns name, group, outlying
    """
    gdf = _read_coastline(get_region(region).key).copy()
    if not include_outlying:
        gdf = gdf[~gdf["outlying"].astype(bool)]
    if bbox is not None:
        gdf = gdf.clip(bbox)
    return gdf.to_crs(crs)


@lru_cache(maxsize=8)
def _land(region_key: str, include_outlying: bool) -> BaseGeometry:
    """
    Merge the coastline polygons of a region once per process.

    Parameters
    ----------
    region_key : str
        Region key
    include_outlying : bool
        Include outlying islands

    Returns
    -------
    BaseGeometry
        Union of all land polygons in EPSG:4326, prepared for fast point tests
    """
    land = get_coastline(region_key, include_outlying).geometry.union_all()
    shapely.prepare(land)
    return land


def get_land(region: str | None = None, include_outlying: bool = False) -> BaseGeometry:
    """
    Get the land area of a region as one geometry.

    Parameters
    ----------
    region : str, optional
        Region key, by default None (uses the default region)
    include_outlying : bool, optional
        Include outlying islands, by default False

    Returns
    -------
    BaseGeometry
        Union of all land polygons in EPSG:4326 (do not modify, it is cached)
    """
    return _land(get_region(region).key, include_outlying)


def points_on_land(
    lons: np.ndarray | list[float],
    lats: np.ndarray | list[float],
    region: str | None = None,
    include_outlying: bool = False,
) -> np.ndarray:
    """
    Test which points are on land.

    Parameters
    ----------
    lons : np.ndarray | list[float]
        Longitudes of the points
    lats : np.ndarray | list[float]
        Latitudes of the points
    region : str, optional
        Region key, by default None (uses the default region)
    include_outlying : bool, optional
        Include outlying islands, by default False

    Returns
    -------
    np.ndarray
        Boolean array, True where the point is on land
    """
    land = get_land(region, include_outlying)
    return shapely.contains_xy(land, np.asarray(lons), np.asarray(lats))
