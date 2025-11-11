# OSM to PBSU Converter

A tool to convert OpenStreetMap data to Proton Bus Simulator (PBSU) route format.

📖 **[Quick Start Guide](QUICKSTART.md)** | 🔧 **[PBSU Format Reference](PBSU_FORMAT.md)** | 📋 **[Examples](examples/README.md)**

## Description

This program converts OpenStreetMap (OSM) data containing bus routes and bus stops into the file format required by Proton Bus Simulator. It automates the creation of:

- Entry points configuration (`entrypoints.txt`, `entrypoints_list.txt`)
- Bus stop configuration files
- Directory structure for PBSU maps
- Coordinate conversion from latitude/longitude to Unity coordinates

## Features

- ✅ Extracts bus stops from OSM data
- ✅ Converts GPS coordinates to Unity/PBSU coordinate system
- ✅ Generates proper PBSU file structure
- ✅ Creates configuration files for all bus stops
- ✅ Supports custom origin points for coordinate conversion
- ✅ Generates README with next steps and bus stop positions

## Requirements

- Python 3.6 or higher
- No external dependencies for basic conversion

## Installation

Simply clone this repository:

```bash
git clone https://github.com/hleong75/OSM-to-PBSU.git
cd OSM-to-PBSU
```

Make the script executable (on Linux/Mac):
```bash
chmod +x osm_to_pbsu.py
```

## Usage

### Basic Usage

```bash
python osm_to_pbsu.py <osm_file.json> -m "Map Name" -r "Route Name"
```

### Examples

```bash
# Convert a bus route from OSM data
python osm_to_pbsu.py route_101.json -m "My_City" -r "Route_101"

# Specify custom origin coordinates
python osm_to_pbsu.py route_101.json -m "My_City" -r "Route_101" --origin-lat 40.7128 --origin-lon -74.0060

# Use custom output directory
python osm_to_pbsu.py route_101.json -m "My_City" -r "Route_101" -o ./my_pbsu_maps
```

### Command-line Arguments

- `input_file` - Input OSM JSON file (required)
- `-m, --map-name` - Name of the map (required, avoid special characters)
- `-r, --route-name` - Name of the route (required, avoid special characters)
- `-o, --output` - Output directory (default: `output`)
- `--origin-lat` - Origin latitude for coordinate conversion (default: first bus stop)
- `--origin-lon` - Origin longitude for coordinate conversion (default: first bus stop)

## Getting OSM Data

You have several options to obtain OpenStreetMap data:

### Option 1: Overpass API (Recommended)

Use the `fetch_osm_data.py` helper script:

```bash
python fetch_osm_data.py --bbox "south,west,north,east" -o route_data.json
```

### Option 2: Overpass Turbo (Web Interface)

1. Go to https://overpass-turbo.eu/
2. Use a query like:
```
[bbox:{{bbox}}];
(
  node["highway"="bus_stop"];
  node["public_transport"="platform"];
  way["highway"~"primary|secondary|tertiary|residential"];
);
out body;
>;
out skel qt;
```
3. Click "Export" → "Data" → "GeoJSON" or "raw OSM data"
4. Save as JSON format

### Option 3: JOSM (Java OpenStreetMap Editor)

1. Download and open JOSM
2. Download the area you're interested in
3. File → Save As → Choose OSM JSON format

## Workflow

1. **Get OSM Data**: Use one of the methods above to download bus route data
2. **Run Converter**: Execute `osm_to_pbsu.py` with your OSM data
3. **Create 3D Models**: Use Blender 2.79 to create the map geometry
4. **Add Textures**: Place texture files in the textures folder
5. **Configure Destinations**: Add destination displays
6. **Test**: Copy to PBSU mods folder and test in the simulator

## Output Structure

The converter creates the following structure:

```
output/
├── MapName.map.txt              # Main map configuration
└── MapName/                     # Map base directory
    ├── README.md                # Instructions and bus stop list
    ├── textures/                # Texture files (you add these)
    ├── dest/                    # Destination displays (you add these)
    └── tiles/
        └── RouteName/           # Route models directory
            ├── entrypoints.txt      # Bus stop positions
            ├── entrypoints_list.txt # Bus stop names list
            └── aipeople/
                └── busstops/        # Individual bus stop configs
                    ├── BusStop1.txt
                    ├── BusStop2.txt
                    └── ...
```

## Next Steps After Conversion

The converter creates the file structure and configuration, but you still need to:

1. **Create 3D Models in Blender 2.79**:
   - Model roads, buildings, and scenery
   - Place bus stop objects at the coordinates from `entrypoints.txt`
   - Each bus stop needs a trigger object and passenger spawn points
   - Export to `.3ds` format

2. **Add Textures**:
   - Create or download textures for roads, buildings, etc.
   - Place in the `textures/` folder
   - Use PNG format (JPG may cause issues)

3. **Configure Destinations**:
   - Create folders for each route destination in `dest/`
   - Add destination display images

4. **Add Preview Image**:
   - Create `preview.png` (recommended size: 640x360px, 16:9 ratio)
   - Place in the map base directory

5. **Test in PBSU**:
   - Copy the generated folders to your PBSU installation:
     - Windows: `Documents/Proton Bus Mods/maps/`
     - Android: `/Android/data/com.viamep.p.../files/maps/`

## Important Notes

### Coordinate System

- **OSM/GPS**: Uses latitude/longitude (WGS84)
- **PBSU/Unity**: Uses meters with:
  - X axis: East-West (east is positive)
  - Y axis: Up-Down (up is positive, 0 for ground)
  - Z axis: North-South (north is positive)

⚠️ **Note**: Y and Z axes are swapped between Blender and Unity!

### File Naming Conventions

- **No special characters**: Avoid accents, spaces in filenames
- **Use underscores**: For internal names, use `Bus_Stop_Name` format
- **Case sensitive**: File names are case-sensitive on some systems

### PBSU Version

This converter generates files compatible with **PBSU Map Mod Version 2** (Phase 2).

For Phase 3 features (traffic lights, etc.), you'll need to manually add those configurations.

## Examples

See the `examples/` folder for:
- Sample OSM data files
- Example conversion outputs
- Tutorial for complete workflow

## Troubleshooting

**No bus stops found:**
- Check that your OSM data includes nodes tagged with `highway=bus_stop` or `public_transport=platform`

**Coordinates seem wrong:**
- Verify your origin coordinates are near your route
- Check that lat/lon values are not swapped

**Bus stops not appearing in game:**
- Ensure you've created the 3D trigger objects in Blender
- Verify the object names match the internal names (check README.md in output)

## References

- [PBSU Official Site](http://www.protonbus.com.br)
- [Proton Bus Mods](http://busmods.com)
- [OpenStreetMap](https://www.openstreetmap.org)
- [Overpass API](https://overpass-api.de/)

See the `ajuda - help/` folder for detailed PBSU mapping documentation.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This tool is provided as-is for use with Proton Bus Simulator. 

OpenStreetMap data is © OpenStreetMap contributors, available under the Open Database License.

## Author

Created for the PBSU modding community to simplify the process of converting real-world bus routes into the simulator.
