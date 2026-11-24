"""Region definitions and lookup of the default region."""

import os
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

# Environment variable that changes the default region for the whole process
DEFAULT_REGION_ENV = "REGION_GEO_REGION"
FALLBACK_REGION = "nz"


@dataclass(frozen=True)
class Region:
    """
    A region (usually a country) and its geometry files.

    Attributes
    ----------
    key : str
        Short lowercase identifier, e.g. "nz"
    name : str
        Full name of the region
    coastline_file : str
        Coastline file in region_geo/data, with columns name, group, outlying
    """

    key: str
    name: str
    coastline_file: str

    @property
    def coastline_path(self) -> Path:
        """
        Path to the coastline file.

        Returns
        -------
        Path
            Path to the packaged coastline file
        """
        return Path(str(files("region_geo.data").joinpath(self.coastline_file)))


REGIONS = {
    "nz": Region(key="nz", name="New Zealand", coastline_file="nz_coastline.gpkg"),
}


def get_default_region() -> str:
    """
    Get the default region key.

    Returns
    -------
    str
        Value of the REGION_GEO_REGION environment variable, or "nz"
    """
    return os.environ.get(DEFAULT_REGION_ENV, FALLBACK_REGION).lower()


def get_region(region: str | None = None) -> Region:
    """
    Get a region definition.

    Parameters
    ----------
    region : str, optional
        Region key, by default None (uses the default region)

    Returns
    -------
    Region
        The region definition
    """
    key = (region or get_default_region()).lower()
    if key not in REGIONS:
        raise KeyError(f"Unknown region '{key}'. Available: {sorted(REGIONS)}")
    return REGIONS[key]


def list_regions() -> list[str]:
    """
    List the available region keys.

    Returns
    -------
    list[str]
        Sorted region keys
    """
    return sorted(REGIONS)
