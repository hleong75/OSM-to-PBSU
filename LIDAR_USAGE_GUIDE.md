# LiDAR HD Usage Guide for OSM-to-PBSU

## Quick Start

This tool now supports loading elevation data directly from LiDAR HD files - **no API required!**

### Basic Usage

```bash
# Convert with LiDAR elevation data
python osm_to_pbsu.py route.json -m "Paris" -r "Route_1" \
  --lidar-file LIDARHD_75056.tif \
  --run-ai-automation
```

## Supported File Formats

### GeoTIFF (.tif, .tiff) - **Recommended**
- Industry standard format
- Widely supported
- Best for large areas
- **Requires:** `pip install rasterio`

**Example:**
```bash
python osm_to_pbsu.py route.json -m "City" -r "Route" \
  --lidar-file elevation_data.tif
```

### XYZ ASCII (.xyz, .txt)
- Simple text format: X Y Z (coordinates and elevation)
- No special libraries required
- Good for small to medium areas

**Example:**
```bash
python osm_to_pbsu.py route.json -m "City" -r "Route" \
  --lidar-file elevation_points.xyz
```

### LAS/LAZ Point Clouds (.las, .laz)
- Point cloud format
- High detail
- **Requires:** `pip install laspy`

**Example:**
```bash
python osm_to_pbsu.py route.json -m "City" -r "Route" \
  --lidar-file pointcloud.las
```

## Where to Get LiDAR HD Data

### France (Free High-Resolution Data)
**IGN Géoportail - LiDAR HD**
- Website: https://geoservices.ign.fr/
- Coverage: All of France at 1m resolution
- Format: GeoTIFF (.tif)
- Free to download and use

**How to Download:**
1. Go to https://geoservices.ign.fr/lidarhd
2. Find your area on the map
3. Download the tiles you need (GeoTIFF format)
4. Use the file with `--lidar-file` parameter

### United States
**USGS Earth Explorer**
- Website: https://earthexplorer.usgs.gov/
- Coverage: All USA
- Formats: Multiple including GeoTIFF
- Free to download

**How to Download:**
1. Create free account at https://earthexplorer.usgs.gov/
2. Search for your location
3. Select "Digital Elevation" datasets
4. Download GeoTIFF format
5. Use with `--lidar-file` parameter

### Worldwide
**OpenTopography**
- Website: https://opentopography.org/
- Coverage: Selected areas worldwide
- Formats: Multiple including GeoTIFF, LAS/LAZ
- Free for academic/research use

## Installation

### Basic (no LiDAR support)
```bash
pip install Pillow requests
```

### With GeoTIFF support (recommended)
```bash
pip install Pillow requests rasterio
```

### With LAS/LAZ support
```bash
pip install Pillow requests laspy
```

### Full support (all formats)
```bash
pip install Pillow requests rasterio laspy
```

## Examples

### Example 1: Paris Metro with LiDAR
```bash
# Download LiDAR data from IGN for Paris
# Then convert OSM data with elevation
python osm_to_pbsu.py paris_metro.json \
  -m "Paris" \
  -r "Metro_Line_1" \
  --lidar-file LIDARHD_75056.tif \
  --run-ai-automation \
  --blender-timeout 900
```

### Example 2: US City with USGS Data
```bash
# Download USGS DEM data for your area
# Then convert
python osm_to_pbsu.py nyc_route.json \
  -m "New_York" \
  -r "Bus_M15" \
  --lidar-file usgs_elevation.tif \
  --run-ai-automation
```

### Example 3: Without LiDAR (flat terrain)
```bash
# Works fine without LiDAR - uses elevation 0
python osm_to_pbsu.py route.json \
  -m "City" \
  -r "Route" \
  --run-ai-automation
```

## Troubleshooting

### "LiDAR file not found"
- Check the file path is correct
- Use absolute path if having issues
- Ensure the file exists

### "rasterio not installed" (for .tif files)
```bash
pip install rasterio
```

### "laspy not installed" (for .las/.laz files)
```bash
pip install laspy
```

### LiDAR file doesn't cover my area
- Download a different tile that covers your route
- Or use multiple tiles (process in segments)
- Falls back to elevation 0 if coordinates outside coverage

### Blender times out
```bash
# Increase timeout for complex maps
python osm_to_pbsu.py route.json -m "City" -r "Route" \
  --lidar-file elevation.tif \
  --run-ai-automation \
  --blender-timeout 900  # 15 minutes
```

## Benefits of Using LiDAR

✅ **Accurate Elevation:** Real-world terrain elevation from actual measurements  
✅ **No API Required:** Works completely offline  
✅ **Free Data:** Most countries provide free LiDAR data  
✅ **High Resolution:** 1m or better resolution in many areas  
✅ **No Rate Limits:** Use as much as you need  
✅ **Better Maps:** More realistic terrain in your PBSU maps  

## Notes

- LiDAR files can be large (100+ MB per tile)
- Processing is done locally - no data sent anywhere
- The tool automatically interpolates elevation for your route points
- If no LiDAR file provided, defaults to elevation 0 (flat terrain)
- You can mix LiDAR elevation with building heights from OSM

## Support

For issues or questions:
- Check the main README.md
- See GEOGRAPHIC_DATA_GUIDE.md for more details
- Open an issue on GitHub
