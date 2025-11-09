# Quick Start Guide

Get started with OSM to PBSU conversion in 5 minutes!

## Prerequisites

- Python 3.6 or higher
- Internet connection (for fetching OSM data)
- Basic knowledge of your local bus routes

## Step 1: Get the Code

```bash
git clone https://github.com/hleong75/OSM-to-PBSU.git
cd OSM-to-PBSU
```

## Step 2: Try the Example

```bash
python osm_to_pbsu.py examples/sample_route.json -m "My_First_Map" -r "Route_1"
```

This creates a complete PBSU map structure in the `output/` directory!

## Step 3: Understand the Output

```bash
cd output/My_First_Map
cat README.md
```

The README shows:
- All bus stop names and positions
- Next steps for 3D modeling
- Coordinate information

## Step 4: Get Real Data

Find an area on OpenStreetMap:

```bash
# Example: Small area in Manhattan, NYC
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o manhattan.json

# Convert to PBSU
python osm_to_pbsu.py manhattan.json -m "Manhattan" -r "M42_Bus"
```

## Step 5: Check Your Output

```bash
ls output/Manhattan/
# You should see: dest/  textures/  tiles/  README.md

ls output/Manhattan/tiles/M42_Bus/
# You should see: entrypoints.txt  entrypoints_list.txt  aipeople/
```

## What's Next?

The converter creates the **configuration files**, but you still need to:

### 1. Create 3D Models (Required)
- Download [Blender 2.79](https://download.blender.org/release/Blender2.79/)
- Model the roads using the coordinates from entrypoints.txt
- Create bus stop trigger objects
- Export to .3ds format
- See: `ajuda - help/ENGLISH - Map Tutorial - Step 2.pdf`

### 2. Add Textures (Required)
- Create or download road/building textures
- Save as PNG (not JPG) in the textures/ folder
- Keep under 2048x2048 pixels for mobile compatibility

### 3. Configure Destinations (Required)
- Create destination display images
- Place in dest/ subfolders
- One folder per route destination

### 4. Add Preview (Recommended)
- Create preview.png (640x360px recommended)
- Shows in map selection screen

### 5. Test in PBSU (Final Step)
- Copy map folder to PBSU mods/maps/
- Launch Proton Bus Simulator
- Select your map!

## Common Questions

**Q: Why isn't my map showing in PBSU?**
A: You need to create the 3D models first! The converter only creates the configuration files.

**Q: Where do I put the generated files?**
A: 
- Windows: `Documents\Proton Bus Mods\maps\`
- Android: `/Android/data/com.viamep.p.../files/maps/`

**Q: Can I skip the 3D modeling?**
A: No, PBSU requires 3D models. The converter just automates the tedious configuration file creation.

**Q: What if I don't know Blender?**
A: Start with the PBSU tutorials in `ajuda - help/` folder. The community is also helpful on Facebook groups!

**Q: Can I convert any city?**
A: Yes! As long as OpenStreetMap has bus stop data for that area. Try it!

## Tips

- **Start small**: Begin with a short route (3-5 stops)
- **Check OSM first**: Make sure your area has bus stops tagged in OpenStreetMap
- **Use real data**: It's easier than making up coordinates
- **Test incrementally**: Convert → Model one stop → Test → Continue
- **Join the community**: See links in main README

## Example Real-World Workflow

Let's create a route for São Paulo, Brazil:

```bash
# 1. Find coordinates on openstreetmap.org for Avenida Paulista
# Approximate bbox: -23.565,-46.665,-23.555,-46.650

# 2. Fetch data
python fetch_osm_data.py --bbox "-23.565,-46.665,-23.555,-46.650" -o paulista.json

# 3. Convert
python osm_to_pbsu.py paulista.json -m "Sao_Paulo_Paulista" -r "Linha_Paulista"

# 4. Check what we got
cat output/Sao_Paulo_Paulista/README.md

# 5. Now create 3D models in Blender using the coordinates!
```

## Troubleshooting

**No bus stops found:**
```bash
# Check your OSM data
python -c "import json; print(json.load(open('your_file.json'))['elements'][:5])"
```

**Internet connection error when fetching:**
- Try again in a few minutes (Overpass API has rate limits)
- Try a smaller bounding box
- Save data from overpass-turbo.eu manually

**Help! I'm stuck:**
- Read the full README.md
- Check examples/README.md
- Look at the PBSU tutorials in `ajuda - help/`
- Ask in PBSU Facebook groups (links in main README)

## Success! What now?

Share your maps!
- Post on PBSU forums
- Upload to busmods.com
- Share in Facebook groups
- Help others get started

---

**Remember**: This tool automates the boring configuration file creation. The creative work (3D modeling, texturing) is still yours to do!

Happy mapping! 🚌🗺️
