# Geographic Data and Enhanced 3DS Generation Guide

## Overview

This guide explains the new geographic data features and enhanced 3DS generation capabilities added to the OSM-to-PBSU converter.

## What's New

### 1. Geographic Data Enrichment

The converter now extracts and uses real geographic data from OpenStreetMap:

#### Building Heights
- **OSM Tags Supported:**
  - `height` - Direct height in meters (e.g., "15m", "15")
  - `building:height` - Alternative height tag
  - `building:levels` - Number of floors (converted to height using 3.5m per floor)
  
- **Default Heights by Type:**
  If no height information is available, the system uses intelligent defaults:
  - House: 7.0m
  - Residential: 10.5m (3 floors)
  - Apartments: 21.0m (6 floors)
  - Commercial: 14.0m (4 floors)
  - Office: 35.0m (10 floors)
  - Hospital: 21.0m
  - And more...

#### Terrain Elevation

**IMPORTANT: API calls have been removed. Use LiDAR HD files for accurate elevation data.**

- **LiDAR HD Support** (Recommended - Works offline, no API required):
  - Supports GeoTIFF (.tif, .tiff), XYZ ASCII (.xyz, .txt), and LAS/LAZ (.las, .laz) formats
  - Load elevation data directly from files using `--lidar-file` parameter
  - Provides Y-coordinate (height) for accurate terrain modeling
  - Example: `python osm_to_pbsu.py route.json -m "Paris" -r "Route1" --lidar-file elevation.tif`
  
- **Where to Get LiDAR HD Data:**
  - France: [IGN Géoportail](https://geoservices.ign.fr/) - Free high-resolution LiDAR data
  - USA: [USGS Earth Explorer](https://earthexplorer.usgs.gov/)
  - Worldwide: [OpenTopography](https://opentopography.org/)

- Falls back to ground level (0) if no LiDAR file is provided

#### Building Footprints
- Extracts actual building polygon shapes from OSM
- Converts footprints to Unity/PBSU coordinate system
- Preserves building orientation and shape

### 2. Enhanced 3DS Generation

The Blender automation script now creates more accurate 3D models:

#### Realistic Buildings
- Creates buildings from actual OSM footprints (not just boxes)
- Uses real heights from OSM data
- Generates proper 3D geometry with walls and roof
- Includes UV mapping for textures

#### Geographic Data File
All geographic data is exported to `geographic_data.json` which contains:
```json
{
  "origin": {
    "lat": 48.8584,
    "lon": 2.2945
  },
  "buildings": [
    {
      "center": {"x": 100, "y": 0, "z": 50},
      "footprint": [...],
      "height": 17.5,
      "type": "residential",
      "name": "Building Name"
    }
  ],
  "elevations": {...},
  "bus_stops": [...]
}
```

### 3. Procedural Texture Generation

**Note: API-based texture fetching has been disabled. The tool now uses procedural generation.**

The AI automation automatically generates textures using procedural algorithms:

#### Features
- **Works completely offline** - No API keys required
- Generates realistic textures for:
  - Asphalt roads
  - Concrete surfaces
  - Building walls (with brick patterns)
  - Grass terrain
  - Sidewalks (with tile patterns)
- Uses PIL/Pillow for high-quality generation
- Falls back to simple PNG generation if PIL is unavailable

#### How to Use
Simply run with `--run-ai-automation`:
```bash
python osm_to_pbsu.py route.json -m "City" -r "Route" --run-ai-automation
```

All textures are automatically generated and saved to `textures/` directory.

### 4. 3DS File Validation

Enhanced validation ensures 3DS files are properly generated:
- Checks file existence
- Validates file size (must be > 0 bytes)
- Reports detailed error messages
- Shows file location and size on success

## Usage Examples

### Basic Conversion with Geographic Data
```bash
# Fetch OSM data with buildings
python fetch_osm_data.py --bbox "48.85,2.29,48.87,2.35" -o paris.json

# Convert to PBSU with geographic enrichment
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1"
```

### Full Automation with Accurate 3D Models
```bash
# Complete automation: OSM → 3DS with real dimensions
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1" \
  --run-ai-automation \
  --blender-path /usr/bin/blender
```

### With LiDAR HD Elevation Data
```bash
# Use real elevation data from LiDAR files (no API required)
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1" \
  --run-ai-automation \
  --lidar-file LIDARHD_75056.tif
```

### With Custom Blender Timeout
```bash
# Increase timeout for complex maps with many buildings
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1" \
  --run-ai-automation \
  --blender-timeout 900
```

### Manual Step-by-Step
```bash
# 1. Convert OSM data with LiDAR elevation
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1" --lidar-file elevation.tif

# 2. Run AI automation separately with custom timeout
python ai_automation.py output/Paris Line_1 \
  --blender-path /usr/bin/blender \
  --blender-timeout 900
```

## Output Structure

After conversion with geographic data:

```
output/
└── MapName/
    ├── geographic_data.json         # NEW: All geographic data
    ├── README.md
    ├── textures/
    │   ├── road_asphalt.png         # Procedurally generated
    │   ├── road_concrete.png        # Procedurally generated
    │   ├── building_wall.png
    │   └── ...
    ├── dest/
    └── tiles/
        └── RouteName/
            ├── entrypoints.txt
            ├── entrypoints_list.txt
            ├── RouteName_auto.3ds   # Generated 3D model
            └── aipeople/busstops/
```

## Technical Details

### Coordinate System Conversions

1. **OSM → Unity/PBSU:**
   - Lat/Lon (WGS84) → X,Y,Z meters
   - Origin point: First bus stop (or custom)
   - X: East-West (east positive)
   - Y: Elevation (up positive)
   - Z: North-South (north positive)

2. **Unity → Blender:**
   - Swaps Y and Z axes
   - Y becomes Z (height)
   - Z becomes Y (north)

### Building Height Calculation

Priority order:
1. `height` tag (direct meters)
2. `building:height` tag
3. `building:levels` × 3.5m
4. Default by building type
5. Generic default (10m)

### Elevation Data Source

- **Service:** Open-Elevation API
- **Endpoint:** https://api.open-elevation.com/api/v1/lookup
- **Free:** No API key required
- **Batch Size:** Up to 100 points per request
- **Fallback:** Returns 0 (ground level) on failure

## Troubleshooting

### 3DS File Not Generated
Check:
1. Blender is installed and in PATH
2. Blender version is 2.79
3. Check Blender output for errors
4. Verify entrypoints.txt exists

### Buildings Have Wrong Heights
- Check if OSM data has height tags
- Use building type defaults
- Manually edit `geographic_data.json` if needed

### Elevation Data Issues
- Provide a LiDAR HD file using `--lidar-file` parameter
- Supported formats: GeoTIFF (.tif), XYZ (.xyz), LAS/LAZ (.las, .laz)
- Falls back to 0 (ground level) if no LiDAR file provided
- Check that the LiDAR file covers your map area

### Blender Timeout
- If Blender times out, increase timeout: `--blender-timeout 900`
- Default timeout is 600 seconds (10 minutes)
- Complex maps with many buildings may need longer timeout
- Monitor Blender process to see if it's making progress

## Best Practices

1. **Data Quality:**
   - Use OSM data from well-mapped areas
   - Check building tags in JOSM before export
   - Add missing height data to OSM if possible
   - Use LiDAR HD data for accurate elevation

2. **Performance:**
   - Limit area size for faster processing
   - Use `--skip-3d` to test without Blender
   - Process large areas in segments
   - Increase `--blender-timeout` for complex maps

3. **Textures:**
   - Procedural textures work great and are free
   - No API keys or internet required
   - PIL/Pillow provides better quality textures
   - All textures generated automatically

4. **Testing:**
   - Always test with small area first
   - Verify 3DS file in Blender before PBSU
   - Check geographic_data.json for accuracy
   - Monitor log files for issues

## Future Enhancements

Potential improvements for future versions:
- Support for terrain mesh from elevation data
- More detailed building modeling (windows, doors)
- Automatic LOD (Level of Detail) generation
- Integration with other texture sources
- Building interior generation
- Traffic and pedestrian path generation

## Contributing

Found issues or have suggestions? Please report them on GitHub!
