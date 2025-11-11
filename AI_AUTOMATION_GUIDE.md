# AI-Powered Automation Guide for OSM to PBSU

## 🆕 What's New - Enhanced Geographic Data Integration

**NEW in this version:**
- ✨ **Real Building Heights**: Buildings now use actual height data from OSM (building:levels, height tags)
- 🗺️ **Terrain Elevation**: Automatic terrain elevation data from geographic services
- 🏢 **Accurate Building Footprints**: Buildings created from actual OSM polygon shapes, not just boxes
- 🌆 **Street View Textures**: Optional realistic textures from Google Street View API
- ✅ **3DS Validation**: Comprehensive validation ensures 3DS files are properly generated
- 📊 **Geographic Data Export**: All building and elevation data saved to `geographic_data.json`

For detailed information about geographic data features, see **[Geographic Data Guide](GEOGRAPHIC_DATA_GUIDE.md)**.

## Overview

The AI automation feature completely automates the PBSU map creation process, eliminating the need for manual 3D modeling, texture creation, and asset generation. This revolutionary feature uses intelligent algorithms and Blender automation to create complete, ready-to-use PBSU maps from OpenStreetMap data.

## 🎯 What Gets Automated

### 1. 3D Model Generation (Enhanced with Geographic Data)
- **Roads**: Automatically generated meshes connecting all bus stops
- **Sidewalks**: Generated on both sides of roads with proper elevation
- **Bus Stop Objects**: 
  - Trigger objects (cubes) positioned at each stop
  - Passenger spawn points (5 per stop) with proper spacing
- **Buildings**: 🆕 **Now with accurate dimensions from OSM data**
  - Created from actual building footprints (polygons from OSM)
  - Real heights from OSM tags (building:levels, height)
  - Intelligent defaults based on building type (residential, commercial, etc.)
  - Properly UV-mapped for texturing
- **Ground Plane**: Large terrain mesh beneath the entire route
- **Automatic UV Mapping**: All models are UV-unwrapped for texturing
- **Export to .3ds**: Automatically exports in PBSU-compatible format
- **3DS Validation**: 🆕 Verifies file creation and validates size

### 2. Texture Generation (Enhanced with Street View)
- **Road Asphalt**: Realistic dark gray texture with noise
- **Road Concrete**: Light gray concrete texture
- **Building Walls**: Brick pattern texture
- **Grass**: Green texture with color variation
- **Sidewalk**: Tile pattern texture
- 🆕 **Street View Images**: Optional realistic textures from Google Street View
  - Requires Google Street View API key
  - Fetches actual street-level imagery
  - Saved to `textures/streetview/` directory

All textures are:
- Generated procedurally (no manual work required)
- PNG format (PBSU compatible)
- 512x512 pixels (optimized for performance)
- Ready to use immediately
- 🆕 Optionally enhanced with real-world imagery

### 3. Destination Displays
- Automatically extracts bus stop names from route data
- Generates display images (512x64 px) for each destination
- Adds text overlays with stop names
- Creates proper folder structure

### 4. Preview Image
- Generates map preview image (640x360 px, 16:9 ratio)
- Includes map name and route information
- Ready for PBSU map selection screen

## 🚀 Quick Start

### One-Command Solution

The fastest way to create a complete PBSU map:

```bash
# Fetch OSM data and generate complete map in one go
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o route.json
python osm_to_pbsu.py route.json -m "Manhattan" -r "M42" --run-ai-automation
```

That's it! Your map is ready to test in PBSU.

### Step-by-Step

If you prefer to run automation separately:

```bash
# 1. Convert OSM data
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1"

# 2. Run AI automation
python ai_automation.py output/My_City Route_1
```

## 📋 Requirements

### Essential
- **Python 3.6+**: Already required for OSM conversion
- **Blender 2.8 or higher**: Required for 3D model generation
  - Download: https://www.blender.org/download/
  - Must be accessible in PATH or specify with `--blender-path`

### Optional (Recommended)
- **PIL/Pillow**: For higher quality textures
  ```bash
  pip install Pillow
  ```
  Without Pillow, basic textures are still generated but with lower quality.

### Installation Verification

Check if Blender is properly installed:

```bash
blender --version
# Should output: Blender 2.8 or higher
```

If Blender is not in PATH, you can specify the full path:

```bash
python ai_automation.py output/My_City Route_1 --blender-path /path/to/blender
```

## 🎮 Usage Examples

### Example 1: Manhattan Bus Route

```bash
# Get OSM data for Manhattan
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o manhattan.json

# Generate complete map with AI automation
python osm_to_pbsu.py manhattan.json -m "Manhattan_42nd" -r "M42_Crosstown" --run-ai-automation

# Copy to PBSU and test!
# Windows: Copy output/Manhattan_42nd to Documents/Proton Bus Mods/maps/
```

### Example 2: São Paulo Route

```bash
# Get data for Avenida Paulista
python fetch_osm_data.py --bbox "-23.565,-46.665,-23.555,-46.650" -o paulista.json

# Convert and automate
python osm_to_pbsu.py paulista.json -m "Sao_Paulo" -r "Paulista" --run-ai-automation
```

### Example 3: Skip 3D Generation

If you have issues with Blender or want to generate only textures and displays:

```bash
python ai_automation.py output/My_City Route_1 --skip-3d
```

This will:
- Generate textures
- Create destination displays
- Create preview image
- Skip 3D model generation

You can then manually create 3D models using the Blender helper scripts.

## 🔧 Advanced Options

### Custom Blender Path

```bash
# Windows
python ai_automation.py output/My_City Route_1 --blender-path "C:\Program Files\Blender Foundation\Blender\blender.exe"

# Linux
python ai_automation.py output/My_City Route_1 --blender-path /usr/local/blender-2.79/blender

# macOS
python ai_automation.py output/My_City Route_1 --blender-path /Applications/Blender.app/Contents/MacOS/blender
```

### Integrated Workflow

```bash
# Full automation in one command
python osm_to_pbsu.py route.json -m "My_City" -r "Route_1" \
  --run-ai-automation \
  --blender-path /path/to/blender
```

## 🎨 How It Works

### 3D Generation Process

1. **Parse Entrypoints**: Reads bus stop positions from entrypoints.txt
2. **Coordinate Conversion**: Converts Unity coordinates to Blender (Y-Z swap)
3. **Road Mesh Creation**:
   - Connects bus stops with a continuous road
   - Calculates perpendicular directions for road width
   - Creates quad faces between segments
4. **Sidewalk Generation**:
   - Creates parallel meshes on both sides of road
   - Slightly elevated above road level
5. **Bus Stop Objects**:
   - Places trigger cubes at each stop location
   - Creates 5 passenger spawn empties per stop
   - Names objects according to PBSU conventions
6. **Building Generation**:
   - Distributes buildings along the route
   - Varies dimensions for visual interest
   - Places on both sides of road
7. **UV Mapping**: Automatically unwraps all meshes
8. **Export**: Saves as .3ds with proper axis settings

### Texture Generation Algorithm

Uses procedural generation techniques:

- **Asphalt**: Base color + random noise + crack lines + blur
- **Concrete**: Base color + noise variation
- **Walls**: Brick pattern with mortar lines
- **Grass**: Green base + color variation for realism
- **Sidewalk**: Tile grid pattern

### Destination Display Creation

1. Reads bus stop names from entrypoints.txt
2. Creates PNG image (512x64) for each stop
3. Renders text using system fonts (if available)
4. Organizes into proper PBSU folder structure

## 📊 Performance

### Generation Time

Typical times on a modern PC:

- Small route (3-5 stops): 1-2 minutes
- Medium route (10-15 stops): 2-4 minutes
- Large route (20+ stops): 4-7 minutes

### Output Size

- 3D Model: 200KB - 2MB (depending on complexity)
- Textures: ~1MB total (5 textures × 200KB each)
- Destination displays: ~50KB per stop
- Total map size: 2-5MB typical

## ⚠️ Troubleshooting

### Blender Not Found

**Error**: `Error: Blender not found at 'blender'`

**Solutions**:
1. Install Blender 2.8 or higher
2. Add Blender to system PATH
3. Use `--blender-path` parameter with full path

### Blender Execution Timeout

**Error**: `Error: Blender execution timed out`

**Causes**:
- Very large route (50+ stops)
- Slow computer

**Solutions**:
- Reduce route complexity
- Process smaller sections separately
- Increase timeout in ai_automation.py (modify line ~300)

### Poor Texture Quality

**Issue**: Textures look too simple or low quality

**Solutions**:
- Install Pillow: `pip install Pillow`
- Manually replace generated textures with higher quality versions
- Use texture packs from resources like textures.com

### Bus Stops Not Working in Game

**Issue**: Bus stops don't trigger in PBSU

**Checks**:
1. Verify trigger objects were created (check .3ds file)
2. Check object naming matches internal names
3. Ensure spawn points exist
4. Verify .3ds file is in correct location

### Buildings Look Too Simple

This is expected! The AI generates basic geometry. For better results:

1. Use the generated model as a base
2. Import into Blender manually
3. Add details, windows, doors
4. Re-export

## 🎯 Best Practices

### 1. Start Small
- Test with short routes (3-5 stops) first
- Verify the workflow before processing large areas
- Check PBSU compatibility early

### 2. Verify OSM Data
- Ensure bus stops are properly tagged in OSM
- Check that route has road network data
- Preview in overpass-turbo.eu before downloading

### 3. Test Incrementally
- Run AI automation
- Test immediately in PBSU
- Iterate if needed

### 4. Customize After Generation
The AI generates a complete, working map, but you can:
- Replace textures with higher quality versions
- Refine 3D models in Blender
- Add custom buildings and details
- Adjust bus stop positions

### 5. Keep Backups
- Generated files can be regenerated
- Keep original OSM data
- Version control your customizations

## 🔍 Quality Expectations

### What AI Automation Provides
✅ Fully functional PBSU map
✅ All bus stops working
✅ Complete road network
✅ Basic buildings for atmosphere
✅ Textures ready to use
✅ Proper file structure

### What May Need Refinement
⚠️ Building details (windows, doors, etc.)
⚠️ Texture realism (procedural vs. photo)
⚠️ Road curves (simplified geometry)
⚠️ Landscape details (trees, signs, etc.)

**The AI creates a working foundation that you can refine if desired.**

## 🆚 Comparison

### AI Automation vs. Manual

| Aspect | AI Automation | Manual |
|--------|--------------|--------|
| Time | 2-5 minutes | 5-15 hours |
| 3D Modeling | Automatic | Manual in Blender |
| Textures | Procedural | Create/download |
| Destinations | Auto-generated | Manual design |
| Quality | Good baseline | Potentially better |
| Effort | Minimal | Significant |
| Customization | Limited | Full control |

### When to Use AI vs. Manual

**Use AI Automation When:**
- You want results quickly
- You're learning PBSU mapping
- You need a prototype/proof of concept
- You want a functional base to customize
- You have many maps to create

**Use Manual Approach When:**
- You want highest quality
- You need specific artistic vision
- You're creating a showcase map
- You enjoy 3D modeling
- You need unique features

**Best Approach**: Use AI automation first, then manually refine!

## 🎓 Learning Path

### Beginner (Use AI Automation)
1. Learn to fetch OSM data
2. Run AI automation
3. Test in PBSU
4. Understand generated structure

### Intermediate (Customize AI Output)
1. Generate with AI
2. Open in Blender
3. Add details and refinements
4. Replace some textures

### Advanced (Hybrid Approach)
1. Use AI for base geometry
2. Extensive manual customization
3. Custom texture creation
4. Advanced PBSU features

## 📚 Additional Resources

### PBSU Mapping
- See `ajuda - help/` folder for PBSU tutorials
- Visit busmods.com for community maps
- Join PBSU Facebook groups

### Blender
- Blender documentation (https://www.blender.org/support/)
- YouTube tutorials for bus simulator mapping
- Community forums

### Textures
- textures.com (paid/free textures)
- poliigon.com (high-quality textures)
- freepbr.com (free PBR textures)

## 🤝 Contributing

Have ideas to improve AI automation?

- Better building generation algorithms
- More realistic texture generation
- Traffic light placement
- Landmark detection from OSM
- Improved road curvature

Open an issue or pull request on GitHub!

## 📄 License

AI automation is part of the OSM to PBSU converter toolkit.
Uses Blender (GPL) for 3D generation.
OpenStreetMap data is © OpenStreetMap contributors (ODbL).

---

**Happy automated mapping!** 🚌🤖🗺️
