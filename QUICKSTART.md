# Quick Start Guide

Get started with OSM to PBSU conversion with **AI automation** in 5 minutes!

## 🚀 Super Quick Start (AI-Powered)

The fastest way to create a complete PBSU map:

```bash
# 1. Clone the repo
git clone https://github.com/hleong75/OSM-to-PBSU.git
cd OSM-to-PBSU

# 2. Get OSM data and generate complete map
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o route.json
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1" --run-ai-automation

# 3. Copy to PBSU and play!
# Windows: Copy output/My_City to Documents/Proton Bus Mods/maps/
```

**Done!** Your map is ready with 3D models, textures, and everything needed!

---

## Prerequisites

- Python 3.6 or higher
- Internet connection (for fetching OSM data)
- **Blender 2.8 or higher** (for AI automation) - Download: https://www.blender.org/download/
- Basic knowledge of your local bus routes

**Optional but recommended:**
```bash
pip install Pillow  # For better texture quality
```

## Step 1: Get the Code

```bash
git clone https://github.com/hleong75/OSM-to-PBSU.git
cd OSM-to-PBSU
```

## Step 2: Try the Example with AI Automation

```bash
python osm_to_pbsu.py examples/sample_route.json -m "My_First_Map" -r "Route_1" --run-ai-automation
```

This creates a **complete, ready-to-use** PBSU map with:
- ✅ 3D models (roads, buildings, bus stops)
- ✅ Textures (asphalt, walls, grass, etc.)
- ✅ Destination displays
- ✅ Preview image
- ✅ All configuration files

**Your map is ready to test in PBSU!**

## Step 3: Understand the Output

```bash
cd output/My_First_Map
cat README.md
```

The README shows:
- All bus stop names and positions
- Next steps for 3D modeling
- Coordinate information

## Step 4: Get Real Data with AI Automation

Find an area on OpenStreetMap:

```bash
# Example: Small area in Manhattan, NYC
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o manhattan.json

# Convert to PBSU with AI automation
python osm_to_pbsu.py manhattan.json -m "Manhattan" -r "M42_Bus" --run-ai-automation
```

**That's it!** Your real-world map is ready to use.

## Step 5: Check Your Output

```bash
ls output/Manhattan/
# You should see: dest/  textures/  tiles/  README.md  preview.png

ls output/Manhattan/tiles/M42_Bus/
# You should see: entrypoints.txt  entrypoints_list.txt  aipeople/  M42_Bus_auto.3ds
```

Notice the **M42_Bus_auto.3ds** file - this is your automatically generated 3D model!

## Step 6: Test in PBSU

### Windows
```bash
# Copy to PBSU mods folder
xcopy /E /I output\Manhattan "%USERPROFILE%\Documents\Proton Bus Mods\maps\Manhattan"
copy output\Manhattan.map.txt "%USERPROFILE%\Documents\Proton Bus Mods\maps\"
```

### Android
Use a file manager to copy `output/Manhattan/` to:
```
/Android/data/com.viamep.protonbus/files/maps/
```

Then launch PBSU and select your map!

---

## Alternative: Manual Workflow

If you prefer manual control or don't have Blender:

### 1. Convert Without AI (Manual 3D Modeling)

```bash
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1"
python automate_post_conversion.py output/My_City
```

Then create 3D models manually using Blender helper scripts.

### 2. AI Automation (Automatic 3D Models)

```bash
# Convert first
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1"

# Then run AI automation separately  
python ai_automation.py output/My_City Route_1
```

### 3. One-Command AI (Fully Automated)

```bash
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1" --run-ai-automation
```

This does everything automatically!

---

## What Gets Automated?

### With `--run-ai-automation` flag:

✅ **3D Models**: Roads, buildings, bus stops automatically generated
✅ **Textures**: Procedural textures created (asphalt, grass, walls, etc.)
✅ **Destination Displays**: Text-based displays for each stop
✅ **Preview Image**: Map thumbnail for PBSU selection screen
✅ **Export to .3ds**: PBSU-compatible format

### Without AI automation:

✅ **Configuration Files**: entrypoints.txt, bus stop configs
✅ **Directory Structure**: Proper PBSU folder layout
✅ **Template Files**: Placeholder textures and displays
✅ **Blender Scripts**: Helper scripts for manual modeling

❌ **3D Models**: You need to create in Blender manually
❌ **Final Textures**: Replace placeholders manually
❌ **Destination Graphics**: Design manually

## 🎯 Recommended Workflow

**For Beginners / Quick Results:**
```bash
# Use AI automation - everything is done for you
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1" --run-ai-automation
```

**For Advanced Users / Custom Maps:**
```bash
# Generate base with AI, then customize
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1" --run-ai-automation
# Then open in Blender and refine as desired
```

---

## Common Questions

**Q: Why isn't my map showing in PBSU?**
A: With AI automation, your map should work immediately. Check:
1. Files are in correct PBSU mods/maps/ location
2. Both the folder and .map.txt file are copied
3. Check PBSU error logs if issues persist

**Q: Do I still need Blender if I use AI automation?**
A: Blender must be installed for AI automation to work, but you don't need to use it manually.

**Q: Where do I put the generated files?**
A: 
- Windows: `Documents\Proton Bus Mods\maps\`
- Android: `/Android/data/com.viamep.p.../files/maps/`

**Q: Can I skip the 3D modeling?**
A: Yes! Use `--run-ai-automation` flag and 3D models are generated automatically.

**Q: Can I customize AI-generated maps?**
A: Absolutely! The AI creates a working base that you can refine in Blender if desired.

**Q: What if I don't know Blender?**
A: With AI automation, you don't need to! It handles everything automatically.

**Q: Can I convert any city?**
A: Yes! As long as OpenStreetMap has bus stop data for that area. Try it!

## Tips

- **Start small**: Begin with a short route (3-5 stops) first
- **Use AI automation**: Get results in minutes instead of hours
- **Check OSM first**: Make sure your area has bus stops tagged in OpenStreetMap
- **Test incrementally**: AI automation makes testing quick - iterate if needed
- **Customize after**: AI generates a working base, refine it if you want
- **Join the community**: See links in main README

## Example Real-World Workflow with AI

Let's create a route for São Paulo, Brazil:

```bash
# 1. Find coordinates on openstreetmap.org for Avenida Paulista
# Approximate bbox: -23.565,-46.665,-23.555,-46.650

# 2. Fetch data and generate complete map in one step
python fetch_osm_data.py --bbox "-23.565,-46.665,-23.555,-46.650" -o paulista.json
python osm_to_pbsu.py paulista.json -m "Sao_Paulo" -r "Paulista" --run-ai-automation

# 3. Test in PBSU immediately!
# Copy output/Sao_Paulo to PBSU mods/maps/ and launch the game
```

**Time saved: 5-15 hours of manual work!**

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
- Read the full README.md and AI_AUTOMATION_GUIDE.md
- Check examples/README.md
- Look at the PBSU tutorials in `ajuda - help/`
- Ask in PBSU Facebook groups (links in main README)

**Blender not found error:**
- Make sure Blender 2.8 or higher is installed
- Add to PATH or use `--blender-path` parameter

## Success! What now?

With AI automation, your maps are ready much faster!

Share your maps:
- Post on PBSU forums
- Upload to busmods.com
- Share in Facebook groups
- Help others get started

**Optional**: Refine AI-generated maps in Blender for even better quality.

---

**Remember**: AI automation creates complete, working maps automatically. You can use them as-is or customize further!

Happy mapping! 🚌🤖🗺️
