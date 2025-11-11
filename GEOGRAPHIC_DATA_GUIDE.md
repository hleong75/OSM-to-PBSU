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
- Fetches elevation data from Open-Elevation API (free, no API key required)
- Provides Y-coordinate (height) for accurate terrain modeling
- Falls back to ground level (0) if service is unavailable

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

### 3. Street View Texture Integration

Optional integration with Google Street View Static API for realistic textures:

#### How to Use
1. Obtain a Google Street View API key from Google Cloud Console
2. Run conversion with the API key:
   ```bash
   python osm_to_pbsu.py route.json -m "City" -r "Route" \
     --run-ai-automation \
     --streetview-api-key YOUR_API_KEY
   ```

#### Features
- Fetches actual street-level images
- Uses bus stop locations as viewpoints
- Saves textures to `textures/streetview/` directory
- Falls back to procedural generation if API fails

#### Limitations
- Requires valid Google API key
- Subject to Google's usage quotas and pricing
- Limited to first 5 bus stops by default (configurable)

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

### With Street View Textures
```bash
# Use real textures from Google Street View
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1" \
  --run-ai-automation \
  --streetview-api-key YOUR_GOOGLE_API_KEY
```

### Manual Step-by-Step
```bash
# 1. Convert OSM data
python osm_to_pbsu.py paris.json -m "Paris" -r "Line_1"

# 2. Run AI automation separately
python ai_automation.py output/Paris Line_1 \
  --blender-path /usr/bin/blender \
  --streetview-api-key YOUR_API_KEY
```

## Output Structure

After conversion with geographic data:

```
output/
└── MapName/
    ├── geographic_data.json         # NEW: All geographic data
    ├── README.md
    ├── textures/
    │   ├── streetview/              # NEW: Street View images
    │   │   ├── stop1_streetview.jpg
    │   │   └── stop2_streetview.jpg
    │   ├── road_asphalt.png
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

### Elevation Data Not Fetched
- Check internet connectivity
- Elevation API may be rate-limited
- Falls back to 0 (ground level) automatically

### Street View Textures Not Downloaded
- Verify API key is valid
- Check Google Cloud Console for quota
- Ensure billing is enabled for the API
- Check if locations have Street View coverage

## Best Practices

1. **Data Quality:**
   - Use OSM data from well-mapped areas
   - Check building tags in JOSM before export
   - Add missing height data to OSM if possible

2. **Performance:**
   - Limit area size for faster processing
   - Use `--skip-3d` to test without Blender
   - Process large areas in segments

3. **Textures:**
   - Use Street View only for final production
   - Procedural textures are fine for testing
   - Consider API costs for large areas

4. **Testing:**
   - Always test with small area first
   - Verify 3DS file in Blender before PBSU
   - Check geographic_data.json for accuracy

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
