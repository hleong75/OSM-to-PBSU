# OSM to PBSU Converter

A tool to convert OpenStreetMap data to Proton Bus Simulator (PBSU) route format with accurate geographic data and AI-powered 3D generation.

📖 **[Quick Start Guide](QUICKSTART.md)** | 🔧 **[PBSU Format Reference](PBSU_FORMAT.md)** | 📋 **[Examples](examples/README.md)** | 🌍 **[Geographic Data Guide](GEOGRAPHIC_DATA_GUIDE.md)**

## Description

This program converts OpenStreetMap (OSM) data containing bus routes and bus stops into the file format required by Proton Bus Simulator. It automates the creation of:

- Entry points configuration (`entrypoints.txt`, `entrypoints_list.txt`)
- Bus stop configuration files
- Directory structure for PBSU maps
- Coordinate conversion from latitude/longitude to Unity coordinates

## Features

- ✅ Extracts bus stops from OSM data
- ✅ Extracts buildings with accurate height information
- ✅ Fetches terrain elevation data from geographic services
- ✅ Converts GPS coordinates to Unity/PBSU coordinate system
- ✅ Generates proper PBSU file structure
- ✅ Creates configuration files for all bus stops
- ✅ Supports custom origin points for coordinate conversion
- ✅ Generates README with next steps and bus stop positions
- ✨ **ENHANCED: AI-Powered Automation** - Automatically generates 3D models with real-world dimensions, textures, and assets!
- 🌍 **NEW: Geographic Data Integration** - Real building heights and terrain elevation
- 🏢 **NEW: Accurate 3D Buildings** - Buildings created with actual footprints and heights from OSM
- 🗺️ **NEW: Street View Textures** - Optional realistic textures from Google Street View

## Requirements

- Python 3.6 or higher
- No external dependencies for basic conversion
- **For AI Automation (optional):**
  - Blender 2.8 or higher (for automatic 3D model generation)
  - PIL/Pillow (optional, for better texture quality): `pip install Pillow`
  - Google Street View API key (optional, for realistic textures)

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

### ✨ Enhanced AI-Powered Automation with Geographic Data

Run complete automation in one command with real-world accuracy:

```bash
# Convert OSM data AND automatically generate everything with accurate dimensions
python osm_to_pbsu.py route_101.json -m "My_City" -r "Route_101" --run-ai-automation

# With Google Street View for realistic textures
python osm_to_pbsu.py route_101.json -m "My_City" -r "Route_101" --run-ai-automation --streetview-api-key YOUR_API_KEY
```

This will automatically:
- Convert OSM data to PBSU format
- **Fetch building heights from OSM data (building:levels, height tags)**
- **Fetch terrain elevation data from geographic services**
- Generate accurate 3D models using Blender with real dimensions
- Create buildings with actual footprints and heights
- Create procedural textures (or fetch from Street View)
- Generate destination displays
- Create preview image

**Your map will be ready to use in PBSU without manual work!**

### Manual Step-by-Step

If you prefer manual control or want to customize:

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
- `--run-ai-automation` - Automatically run AI automation after conversion (NEW!)
- `--blender-path` - Path to Blender executable for AI automation (default: `blender`)

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

## Complete Workflow

### Option A: AI-Powered Automation (Recommended) ✨

1. **Get OSM Data**: Use one of the methods above to download bus route data
2. **Run with AI Automation**: 
   ```bash
   python osm_to_pbsu.py route.json -m "My_City" -r "Route_1" --run-ai-automation
   ```
3. **Done!** Your map is ready to test in PBSU

### Option B: Semi-Automated (More Control)

1. **Get OSM Data**: Use one of the methods above to download bus route data
2. **Run Converter**: Execute `osm_to_pbsu.py` with your OSM data
3. **Run AI Automation**: Execute `ai_automation.py` to generate 3D models and assets
   ```bash
   python ai_automation.py output/My_City Route_1
   ```
4. **Test**: Copy to PBSU mods folder and test in the simulator

### Option C: Manual (Traditional)

1. **Get OSM Data**: Use one of the methods above to download bus route data
2. **Run Converter**: Execute `osm_to_pbsu.py` with your OSM data
3. **Run Post-Conversion**: Execute `automate_post_conversion.py` to create templates
4. **Create 3D Models**: Use Blender 2.8 or higher with the generated helper scripts
5. **Customize Assets**: Replace placeholder textures and destination displays
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

## Post-Conversion Automation

After running the converter, you have three options:

### ✨ Option 1: AI Automation (Fully Automated)

Run complete AI-powered automation:

```bash
python ai_automation.py output/My_City Route_1
```

This will automatically:
- ✅ Generate 3D models using Blender (roads, bus stops, buildings)
- ✅ Create procedural textures (asphalt, concrete, walls, grass)
- ✅ Generate destination displays with text
- ✅ Create preview image
- ✅ Export everything to PBSU-compatible format

**Your map will be ready to use without any manual work!**

**Requirements:**
- Blender 2.8 or higher must be installed and in PATH (or specify with `--blender-path`)
- PIL/Pillow recommended for better quality: `pip install Pillow`

### Option 2: Semi-Automated (Blender Helper Scripts)

Use the traditional automation script to prepare templates and helper scripts:

```bash
python automate_post_conversion.py output/My_City
```

This automation script will:
- ✅ Create placeholder textures (ready-to-use PNG files)
- ✅ Generate destination display templates
- ✅ Create preview image template
- ✅ Generate Blender helper scripts for 3D modeling
- ✅ Create a detailed checklist for manual work

### Blender Helper Scripts

The automation creates Python scripts for Blender 2.8+:

1. **import_entrypoints.py** - Import bus stop positions as markers
2. **create_busstop_markers.py** - Create trigger objects and passenger spawn points
3. **create_road_mesh.py** - Generate basic road mesh connecting bus stops

These scripts dramatically speed up the 3D modeling process!

## Next Steps After Conversion

### If You Used AI Automation ✨

**Congratulations!** Your map is already complete and ready to test:

1. **Copy to PBSU**: 
   - Copy the generated map folder to your PBSU installation
   - Windows: `Documents/Proton Bus Mods/maps/`
   - Android: `/Android/data/com.viamep.p.../files/maps/`

2. **Test in PBSU**:
   - Launch Proton Bus Simulator
   - Select your map from Custom Maps
   - Test the route and enjoy!

3. **Optional Refinements**:
   - You can manually refine the 3D models in Blender if desired
   - Replace textures with higher quality versions
   - Customize destination displays further

### If You Used Manual/Semi-Automated Approach

The converter and automation create the file structure and templates, but you still need to:

1. **Create 3D Models in Blender 2.8 or higher**:
   - Use the provided Blender helper scripts in `blender_scripts/`
   - Model roads, buildings, and scenery
   - Place bus stop objects at the coordinates from `entrypoints.txt`
   - Each bus stop needs a trigger object and passenger spawn points
   - Export to `.3ds` format

2. **Replace Placeholder Textures**:
   - Placeholder textures are already created in the `textures/` folder
   - Replace them with your own designs or downloaded textures
   - Use PNG format (JPG may cause issues)
   - Keep under 2048x2048 pixels for mobile compatibility

3. **Customize Destination Displays**:
   - Templates are created in `dest/` folder
   - Replace with your own destination text/graphics
   - Common size: 512x64 pixels PNG

4. **Update Preview Image**:
   - Replace the template `preview.png` with actual map screenshot
   - Recommended size: 640x360px, 16:9 ratio
   - Shows in map selection screen

5. **Test in PBSU**:
   - Follow the detailed checklist in `POST_CONVERSION_CHECKLIST.md`
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
