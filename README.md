# region_geo

Coastline geometry for a region. New Zealand is the default region, so calls need no region argument. More regions and layers (boundaries, basins, back-arc, subduction interfaces) can be added later without changing the API.

Replaces `nzgeom` in NZGMDB.

## Install

```
pip install git+https://github.com/ucgmsim/region_geo.git
```

## Development

CI uses the shared [meta-ci-action](https://github.com/ucgmsim/meta-ci-action) workflows: ruff, deptry, npdlint, ty and pytest (95% coverage). To run the same checks as git hooks:

```
uv sync --all-groups --all-extras
uvx lefthook install
```

## Usage

```python
import region_geo

# Which points are on land (main islands of the default region)
on_land = region_geo.points_on_land(df["lon"], df["lat"])

# Coastline polygons as a GeoDataFrame (EPSG:4326 by default)
coast = region_geo.get_coastline(include_outlying=True, crs="EPSG:2193")

# Land as one shapely geometry
land = region_geo.get_land()
```

Pick another region with `region="xx"`, or set `REGION_GEO_REGION=xx` for the whole process.

`include_outlying` adds islands left out by default. For NZ these are the Chatham and Kermadec Islands, which sit across 180 degrees.

### Replacing nzgeom

```python
# Before
nz_coast = nzgeom.coastlines.get_NZ_coastlines().to_crs("EPSG:4326").union_all()
points = gpd.GeoSeries([Point(lon, lat) for lon, lat in zip(df["lon"], df["lat"])])
df = df[points.within(nz_coast).to_numpy()]

# After
df = df[region_geo.points_on_land(df["lon"], df["lat"])]
```

Same result on 5000 random points across NZ, about twice as fast. The merged land polygon is cached, so later calls are almost instant.

## Data

| Region | File | Source |
| --- | --- | --- |
| nz | `region_geo/data/nz_coastline.gpkg` | LINZ NZ Coastlines and Islands Polygons (Topo 1:50k), layer 51153, CC BY 4.0 |

Coastline files are GeoPackages in EPSG:4326 with columns `name`, `group`, `outlying`. Rebuild the NZ file with:

```
uv sync --extra scripts
python scripts/build_nz_coastline.py nz-coastlines-and-islands-polygons-topo-150k.gpkg
```

## Adding a region

1. Write `region_geo/data/<key>_coastline.gpkg` with the standard columns
2. Add a `Region` to `REGIONS` in `region_geo/regions.py`
