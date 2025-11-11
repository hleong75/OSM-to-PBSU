# Examples

This directory contains example OSM data and usage examples for the OSM to PBSU converter.

## Sample Route

The `sample_route.json` file contains a simple example with 5 bus stops along a main road.

### Convert the Sample

```bash
# From the repository root
python osm_to_pbsu.py examples/sample_route.json -m "Example_City" -r "Route_1"
```

This will create:
- `output/Example_City.map.txt` - Main map configuration
- `output/Example_City/` - Complete directory structure with all required files

### Sample Bus Stops

1. **Central Station** (40.7580, -73.9855)
2. **Main Street** (40.7590, -73.9850)
3. **City Hall** (40.7600, -73.9845)
4. **Park Avenue** (40.7610, -73.9840)
5. **Shopping Center** (40.7620, -73.9835)

## Getting Real OSM Data

### Method 1: Use the fetch_osm_data.py script

```bash
# Fetch data for a specific area (Times Square area example)
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o my_route.json

# Then convert it
python osm_to_pbsu.py my_route.json -m "Manhattan" -r "Route_42"
```

### Method 2: Overpass Turbo

1. Go to https://overpass-turbo.eu/
2. Navigate to your area of interest
3. Paste this query:

```
[bbox:{{bbox}}];
(
  node["highway"="bus_stop"];
  node["public_transport"="platform"];
  way["highway"~"primary|secondary|tertiary"];
);
out body;
>;
out skel qt;
```

4. Click "Run"
5. Click "Export" → "Download as GPX"
6. Convert to JSON if needed

### Method 3: OpenStreetMap Website

1. Go to https://www.openstreetmap.org
2. Navigate to your area
3. Click "Export"
4. Select "OpenStreetMap XML Data" or use the Overpass API link
5. Save the data

## Real World Example

Let's say you want to create a route for a real city:

```bash
# 1. Find coordinates on OpenStreetMap
# For example, downtown São Paulo, Brazil area

# 2. Fetch the data
python fetch_osm_data.py --bbox "-23.55,-46.65,-23.54,-46.63" -o sao_paulo_route.json

# 3. Convert to PBSU
python osm_to_pbsu.py sao_paulo_route.json -m "Sao_Paulo" -r "Linha_9001"

# 4. Check the output
cd output/Sao_Paulo/
cat README.md
```

## Understanding the Output

After conversion, you'll have:

```
output/
├── Example_City.map.txt              # Main configuration
└── Example_City/
    ├── README.md                     # Your guide with coordinates
    ├── dest/                         # Add destination displays here
    ├── textures/                     # Add textures here
    └── tiles/
        └── Route_1/
            ├── entrypoints.txt       # Bus stop positions
            ├── entrypoints_list.txt  # Bus stop names
            └── aipeople/
                └── busstops/         # Individual configurations
                    ├── Central_Station.txt
                    ├── Main_Street.txt
                    └── ...
```

## Next Steps

1. **Create 3D Models**: Use Blender 2.79 to model your route
2. **Add Textures**: Place texture files in the textures/ folder
3. **Configure Destinations**: Create destination display images
4. **Test**: Copy to PBSU mods folder and test

See the main README.md for detailed instructions.

## Tips

- **Start small**: Begin with a simple route (3-5 stops) to learn the workflow
- **Use real data**: OpenStreetMap has excellent coverage for most cities
- **Check coordinates**: Verify that bus stops are where you expect them
- **Test early**: Import partial routes into PBSU to test as you build

## Common Issues

**No bus stops found:**
```bash
# Check your OSM data has bus stops
python -c "import json; data=json.load(open('your_file.json')); print([e for e in data['elements'] if e.get('tags',{}).get('highway')=='bus_stop'])"
```

**Coordinates look wrong:**
```bash
# Verify your data's coordinate range
python -c "import json; data=json.load(open('your_file.json')); nodes=[e for e in data['elements'] if e['type']=='node']; print(f\"Lat: {min(n['lat'] for n in nodes):.4f} to {max(n['lat'] for n in nodes):.4f}\"); print(f\"Lon: {min(n['lon'] for n in nodes):.4f} to {max(n['lon'] for n in nodes):.4f}\")"
```

## Resources

- [OpenStreetMap](https://www.openstreetmap.org) - Get map data
- [Overpass Turbo](https://overpass-turbo.eu/) - Query OSM data
- [PBSU Mods](http://busmods.com) - Example PBSU mods
- [Blender 2.79](https://download.blender.org/release/Blender2.79/) - Required for 3D modeling
