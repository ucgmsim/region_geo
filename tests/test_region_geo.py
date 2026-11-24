import numpy as np
import pytest

import region_geo
from region_geo.regions import DEFAULT_REGION_ENV

CHRISTCHURCH = (172.63, -43.53)
TASMAN_SEA = (170.0, -40.0)
CHATHAM = (-176.507, -43.912)


def test_default_region_is_nz(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(DEFAULT_REGION_ENV, raising=False)
    assert region_geo.get_default_region() == "nz"
    assert region_geo.get_region().name == "New Zealand"


def test_default_region_env_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(DEFAULT_REGION_ENV, "nowhere")
    with pytest.raises(KeyError):
        region_geo.get_region()


def test_points_on_land():
    lons, lats = zip(CHRISTCHURCH, TASMAN_SEA, CHATHAM)
    np.testing.assert_array_equal(
        region_geo.points_on_land(lons, lats), [True, False, False]
    )


def test_points_on_land_outlying():
    on_land = region_geo.points_on_land(
        [CHATHAM[0]], [CHATHAM[1]], include_outlying=True
    )
    assert on_land[0]


def test_coastline_outlying_filter():
    main = region_geo.get_coastline()
    full = region_geo.get_coastline(include_outlying=True)
    assert len(full) > len(main)
    assert not main["outlying"].any()


def test_coastline_crs_and_bbox():
    gdf = region_geo.get_coastline(bbox=(172.0, -44.0, 173.0, -43.0), crs="EPSG:2193")
    assert gdf.crs.to_epsg() == 2193
    assert not gdf.empty


def test_list_regions():
    assert "nz" in region_geo.list_regions()
