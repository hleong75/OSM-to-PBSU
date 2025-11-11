# Complete Workflow Example: Creating a PBSU Map

This document walks through the entire process of creating a PBSU map from OpenStreetMap data, including the new automation features.

## Overview

The workflow has been dramatically simplified with the new automation script:

1. **Get OSM Data** (manual or automated)
2. **Run Converter** (automated)
3. **Run Post-Conversion Automation** (automated) ⭐ NEW
4. **Use Blender Helper Scripts** (semi-automated) ⭐ NEW
5. **Customize Assets** (manual)
6. **Test in PBSU** (manual)

## Step-by-Step Example

### Step 1: Get OSM Data

Let's create a map for a small area in Manhattan, NYC.

#### Option A: Use the helper script (recommended)

```bash
python fetch_osm_data.py --bbox "40.755,-73.990,40.760,-73.980" -o manhattan_route.json
```

#### Option B: Manual download from Overpass Turbo

1. Go to https://overpass-turbo.eu/
2. Zoom to your desired area
3. Run this query:
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
4. Export → Data → Save as JSON

### Step 2: Run the Converter

```bash
python osm_to_pbsu.py manhattan_route.json -m "Manhattan_42nd" -r "M42_Crosstown"
```

**Output:**
```
Loading OSM data from manhattan_route.json...
Parsing OSM data...
Found 8 bus stops
Found 15 road segments
Using origin coordinates: 40.7571, -73.9869
Creating directory structure...
Generating PBSU files...
Created output/Manhattan_42nd.map.txt
Created output/Manhattan_42nd/tiles/M42_Crosstown/entrypoints_list.txt
Created output/Manhattan_42nd/tiles/M42_Crosstown/entrypoints.txt
Created 8 bus stop configuration files
Created output/Manhattan_42nd/README.md

✓ Conversion complete!
```

### Step 3: Run Post-Conversion Automation ⭐ NEW

```bash
python automate_post_conversion.py output/Manhattan_42nd
```

**Output:**
```
============================================================
Post-Conversion Automation for: Manhattan_42nd
============================================================

Creating placeholder textures...
  Created: road_asphalt.png
  Created: road_concrete.png
  Created: building_wall.png
  Created: grass.png
  Created: sidewalk.png

Creating destination display templates...
  Created: M42_Crosstown/Terminal_A/0.png
  Created: M42_Crosstown/Terminal_B/0.png
  Created: M42_Crosstown/Centro/0.png

Creating preview image template...
  Created: preview.png

Generating Blender helper scripts...
  Created: import_entrypoints.py
  Created: create_busstop_markers.py
  Created: create_road_mesh.py
  Created: README.md

Generating post-conversion checklist...
  Created: POST_CONVERSION_CHECKLIST.md

✓ Post-conversion automation complete!
```

**What was just created:**
- ✅ 5 placeholder texture files (PNG)
- ✅ 3 destination display templates
- ✅ Preview image template
- ✅ 3 Blender Python helper scripts
- ✅ Comprehensive checklist for remaining work

### Step 4: Use Blender Helper Scripts ⭐ NEW

Now open Blender 2.8 or higher and use the generated scripts:

#### 4.1 Import Bus Stop Markers

1. Open Blender 2.8 or higher
2. Open Text Editor panel
3. Open `output/Manhattan_42nd/blender_scripts/import_entrypoints.py`
4. Update the path at the bottom:
   ```python
   entrypoints_file = "/full/path/to/output/Manhattan_42nd/tiles/M42_Crosstown/entrypoints.txt"
   ```
5. Run script (Alt+P)

**Result:** Empty spheres appear at each bus stop location

#### 4.2 Create Basic Road Mesh

1. Open `blender_scripts/create_road_mesh.py`
2. Update the path
3. Run script

**Result:** A basic road mesh connecting all bus stops

#### 4.3 Refine the Road (Manual)

Now you can:
- Edit the road mesh vertices
- Add curves to roads
- Add intersections
- Adjust road width
- Add sidewalks

#### 4.4 Create Bus Stop Objects

1. Open `blender_scripts/create_busstop_markers.py`
2. Update the path
3. Run script

**Result:** 
- Trigger objects (cubes) at each stop
- 5 passenger spawn points per stop

#### 4.5 Add Buildings and Scenery (Manual)

- Model or import buildings
- Add trees, street furniture
- Add ground/terrain
- Keep polygon count reasonable

#### 4.6 Export to .3ds

1. Select all objects (A)
2. File → Export → 3D Studio (.3ds)
3. Save to: `output/Manhattan_42nd/tiles/M42_Crosstown/`
4. Settings:
   - Scale: 1.0
   - Forward: Y Forward
   - Up: Z Up

### Step 5: Customize Assets

#### 5.1 Replace Placeholder Textures

The automation created basic placeholder textures. Now replace them:

```bash
cd output/Manhattan_42nd/textures/
# Replace these with your own textures:
# - road_asphalt.png
# - road_concrete.png  
# - building_wall.png
# - grass.png
# - sidewalk.png
```

**Tips:**
- Use PNG format (not JPG)
- Keep under 2048x2048 pixels
- Power-of-two dimensions (256, 512, 1024, 2048)
- You can find free textures at textures.com, poliigon.com, etc.

#### 5.2 Customize Destination Displays

```bash
cd output/Manhattan_42nd/dest/M42_Crosstown/
# Edit the template folders:
# - Terminal_A/0.png (512x64 recommended)
# - Terminal_B/0.png
# - Centro/0.png
```

Design these to show:
- Destination name
- Route number
- Direction arrow (optional)

#### 5.3 Create Preview Image

Replace the template preview:

```bash
# Take a screenshot or render of your map
# Save as: output/Manhattan_42nd/preview.png
# Size: 640x360 (16:9 ratio)
```

This appears in the map selection screen in PBSU.

### Step 6: Test in PBSU

#### 6.1 Copy Files

**Windows:**
```bash
copy output\Manhattan_42nd C:\Users\YourName\Documents\Proton Bus Mods\maps\Manhattan_42nd
copy output\Manhattan_42nd.map.txt C:\Users\YourName\Documents\Proton Bus Mods\maps\
```

**Android:**
```bash
# Use a file manager app
# Copy to: /Android/data/com.viamep.protonbus/files/maps/
```

#### 6.2 Launch PBSU

1. Start Proton Bus Simulator
2. Go to Custom Maps
3. Select "Manhattan_42nd"
4. Test the route!

#### 6.3 Verify

Check that:
- ✓ Map loads without errors
- ✓ Bus stops appear correctly
- ✓ You can stop at each bus stop
- ✓ Passengers board and alight
- ✓ Textures display properly
- ✓ Destination displays work
- ✓ No crashes or glitches

### Step 7: Iterate and Improve

Based on testing, you might need to:

1. **Adjust bus stop positions**
   - Edit `entrypoints.txt`
   - Move trigger objects in Blender
   - Re-export

2. **Fix texture issues**
   - Replace textures that don't look good
   - Adjust UV mapping

3. **Improve geometry**
   - Add more detail
   - Fix collision issues
   - Optimize polygon count

4. **Performance tuning**
   - Reduce polygon count if game lags
   - Use smaller textures
   - Simplify geometry

## Time Comparison

### Old Workflow (Before Automation)
- Get OSM data: 15 min
- Manual coordinate conversion: 2 hours
- Create directory structure: 30 min
- Write config files: 2 hours
- Create texture placeholders: 1 hour
- Create destination templates: 1 hour
- Figure out Blender workflow: 3 hours
- Manual 3D modeling: 5+ hours
- **Total: ~15 hours**

### New Workflow (With Automation)
- Get OSM data: 15 min (or use fetch script: 1 min)
- Run converter: 1 min ✓
- Run automation: 1 min ✓
- Use Blender scripts: 30 min ✓
- Refine 3D models: 3-5 hours
- Customize textures: 1 hour
- Test and iterate: 1 hour
- **Total: ~6-8 hours (50-60% time saved!)**

## Checklist Reference

The automation creates `POST_CONVERSION_CHECKLIST.md` which tracks:

```markdown
## ✅ Automated Steps (Already Done)
- [x] Created directory structure
- [x] Generated entrypoints.txt
- [x] Created placeholder textures
... etc

## 🔨 Manual Steps (You Need to Do)
- [ ] Install Blender 2.8 or higher
- [ ] Run import_entrypoints.py
- [ ] Create 3D models
... etc
```

Use this to track your progress!

## Tips for Success

1. **Start Small**
   - Begin with a short route (3-5 stops)
   - Test frequently
   - Expand gradually

2. **Use References**
   - Look at photos of the real route
   - Check other PBSU maps for inspiration
   - Join PBSU Facebook groups for help

3. **Test Early, Test Often**
   - Don't wait until everything is done
   - Test after each major step
   - Fix issues as you find them

4. **Keep Backups**
   - Save versions as you work
   - Use git for version control
   - Keep backup copies

5. **Join the Community**
   - PBSU Facebook groups
   - busmods.com forums
   - Share your progress
   - Ask for help when stuck

## Troubleshooting

### Bus stops don't work in game
- Check object naming matches internal names exactly
- Verify trigger objects are at ground level (Y=0)
- Ensure spawn points exist and are properly named

### Performance issues
- Reduce polygon count (aim for <300k total)
- Use smaller textures
- Simplify geometry
- Remove unnecessary details

### Textures look wrong
- Use PNG not JPG
- Check texture sizes (power of 2)
- Verify UV mapping
- Check texture paths

### Map won't load
- Check .map.txt file syntax
- Verify all referenced files exist
- Check for special characters in filenames
- Look at PBSU error logs

## Resources

- **Blender Scripts README:** `blender_scripts/README.md`
- **PBSU Tutorials:** `ajuda - help/` folder
- **Map Checklist:** `POST_CONVERSION_CHECKLIST.md`
- **PBSU Format Reference:** `PBSU_FORMAT.md`
- **busmods.com:** Example maps and tutorials
- **PBSU Facebook Groups:** Community help

## Conclusion

The automation significantly streamlines the PBSU map creation process. You can now focus on the creative aspects (3D modeling, texturing) instead of tedious configuration work.

**Happy mapping!** 🚌🗺️

---

**Questions?** Check the documentation or ask in PBSU community groups.
