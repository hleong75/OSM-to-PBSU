#!/usr/bin/env python3
"""
Post-Conversion Automation Script for OSM to PBSU
Automates the next steps after converting OSM data to PBSU format

This script automates:
1. Creating placeholder textures
2. Generating destination display templates
3. Creating preview image template
4. Generating Blender helper scripts
5. Creating detailed checklists for manual work
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Tuple


class PostConversionAutomator:
    """Automates post-conversion tasks for PBSU maps"""
    
    def __init__(self, map_dir: str):
        """
        Initialize the automator
        
        Args:
            map_dir: Path to the map directory (e.g., output/MyMap)
        """
        self.map_dir = map_dir
        self.map_name = os.path.basename(map_dir)
        
    def create_placeholder_textures(self) -> None:
        """Create placeholder texture files"""
        textures_dir = os.path.join(self.map_dir, 'textures')
        os.makedirs(textures_dir, exist_ok=True)
        
        # Create simple colored PNG files as placeholders
        textures = {
            'road_asphalt.png': (60, 60, 65),  # Dark gray for asphalt
            'road_concrete.png': (180, 180, 180),  # Light gray for concrete
            'building_wall.png': (200, 180, 160),  # Beige for buildings
            'grass.png': (80, 150, 60),  # Green for grass
            'sidewalk.png': (150, 150, 140),  # Gray for sidewalks
        }
        
        print("Creating placeholder textures...")
        for filename, color in textures.items():
            filepath = os.path.join(textures_dir, filename)
            self._create_simple_png(filepath, color, 256, 256)
            print(f"  Created: {filename}")
    
    def _create_simple_png(self, filepath: str, color: Tuple[int, int, int], 
                          width: int, height: int) -> None:
        """Create a simple solid-color PNG file"""
        try:
            # Try to use PIL if available
            from PIL import Image
            img = Image.new('RGB', (width, height), color)
            img.save(filepath, 'PNG')
        except ImportError:
            # Fallback: create a minimal PNG file manually
            import struct
            import zlib
            
            def png_pack(png_tag, data):
                chunk_head = png_tag + data
                return (struct.pack("!I", len(data)) +
                       chunk_head +
                       struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))
            
            # PNG header
            png_data = b'\x89PNG\r\n\x1a\n'
            
            # IHDR chunk
            ihdr = struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0)
            png_data += png_pack(b'IHDR', ihdr)
            
            # IDAT chunk - create pixel data
            raw_data = b''
            for y in range(height):
                raw_data += b'\x00'  # Filter type
                for x in range(width):
                    raw_data += struct.pack('!3B', *color)
            
            compressed_data = zlib.compress(raw_data, 9)
            png_data += png_pack(b'IDAT', compressed_data)
            
            # IEND chunk
            png_data += png_pack(b'IEND', b'')
            
            with open(filepath, 'wb') as f:
                f.write(png_data)
    
    def create_destination_templates(self) -> None:
        """Create destination display image templates"""
        dest_dir = os.path.join(self.map_dir, 'dest')
        
        # Find route directories
        tiles_dir = os.path.join(self.map_dir, 'tiles')
        if not os.path.exists(tiles_dir):
            print("Warning: tiles directory not found")
            return
        
        routes = [d for d in os.listdir(tiles_dir) 
                 if os.path.isdir(os.path.join(tiles_dir, d))]
        
        if not routes:
            print("Warning: No routes found in tiles directory")
            return
        
        print("Creating destination display templates...")
        for route in routes:
            route_dest_dir = os.path.join(dest_dir, route)
            os.makedirs(route_dest_dir, exist_ok=True)
            
            # Create example destinations
            destinations = ['Terminal_A', 'Terminal_B', 'Centro']
            for dest in destinations:
                dest_path = os.path.join(route_dest_dir, dest)
                os.makedirs(dest_path, exist_ok=True)
                
                # Create a simple template image for destination display
                template_path = os.path.join(dest_path, '0.png')
                self._create_destination_display(template_path, dest)
                print(f"  Created: {route}/{dest}/0.png")
    
    def _create_destination_display(self, filepath: str, dest_name: str) -> None:
        """Create a simple destination display template"""
        # Create a simple colored rectangle as template (512x64 is common for destination displays)
        self._create_simple_png(filepath, (255, 180, 0), 512, 64)
    
    def create_preview_template(self) -> None:
        """Create preview image template"""
        preview_path = os.path.join(self.map_dir, 'preview.png')
        print("Creating preview image template...")
        # 640x360 (16:9 aspect ratio) with blue color
        self._create_simple_png(preview_path, (70, 130, 180), 640, 360)
        print(f"  Created: preview.png")
    
    def generate_blender_helper_scripts(self) -> None:
        """Generate Blender Python helper scripts"""
        scripts_dir = os.path.join(self.map_dir, 'blender_scripts')
        os.makedirs(scripts_dir, exist_ok=True)
        
        print("Generating Blender helper scripts...")
        
        # Script 1: Import entrypoints
        self._create_import_entrypoints_script(scripts_dir)
        print("  Created: import_entrypoints.py")
        
        # Script 2: Create bus stop markers
        self._create_busstop_markers_script(scripts_dir)
        print("  Created: create_busstop_markers.py")
        
        # Script 3: Create basic road mesh
        self._create_road_mesh_script(scripts_dir)
        print("  Created: create_road_mesh.py")
        
        # Create README for Blender scripts
        self._create_blender_scripts_readme(scripts_dir)
        print("  Created: README.md")
    
    def _create_import_entrypoints_script(self, scripts_dir: str) -> None:
        """Create Blender script to import entrypoints as markers"""
        script_content = '''"""
Blender 2.79 Script: Import Entrypoints
This script imports bus stop positions from entrypoints.txt and creates markers
"""

import bpy
import os

def import_entrypoints(entrypoints_file):
    """Import entrypoints from file and create empty objects as markers"""
    
    if not os.path.exists(entrypoints_file):
        print(f"Error: File not found: {entrypoints_file}")
        return
    
    # Read entrypoints file
    with open(entrypoints_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse entrypoints
    entries = []
    current_entry = {}
    
    for line in content.split('\\n'):
        line = line.strip()
        if line.startswith('[entrypoint_'):
            if current_entry:
                entries.append(current_entry)
            current_entry = {}
        elif '=' in line:
            key, value = line.split('=', 1)
            current_entry[key] = value
    
    if current_entry:
        entries.append(current_entry)
    
    # Create markers in Blender
    for entry in entries:
        if 'name' not in entry:
            continue
        
        name = entry['name']
        x = float(entry.get('posX', 0))
        y = float(entry.get('posY', 0))
        z = float(entry.get('posZ', 0))
        
        # Note: Blender uses Y-up, Unity uses Z-up
        # So we swap Y and Z when importing
        blender_pos = (x, z, y)
        
        # Create empty object as marker
        bpy.ops.object.empty_add(type='SPHERE', location=blender_pos)
        obj = bpy.context.object
        obj.name = f"BusStop_{name}"
        obj.empty_draw_size = 2.0
        
        print(f"Created marker: {name} at {blender_pos}")
    
    print(f"Imported {len(entries)} bus stop markers")

# Main execution
if __name__ == "__main__":
    # Update this path to your entrypoints.txt file
    entrypoints_file = "PATH_TO_YOUR_MAP/tiles/ROUTE_NAME/entrypoints.txt"
    
    # Call the import function
    import_entrypoints(entrypoints_file)
'''
        
        script_path = os.path.join(scripts_dir, 'import_entrypoints.py')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
    
    def _create_busstop_markers_script(self, scripts_dir: str) -> None:
        """Create Blender script to create bus stop trigger objects"""
        script_content = '''"""
Blender 2.79 Script: Create Bus Stop Objects
This script creates trigger objects and passenger spawn points for bus stops
"""

import bpy
import math

def create_busstop_objects(busstop_name, location):
    """
    Create bus stop trigger and passenger spawn points
    
    Args:
        busstop_name: Internal name of the bus stop
        location: Tuple of (x, y, z) in Blender coordinates
    """
    
    x, y, z = location
    
    # Create trigger object (a simple cube)
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    trigger = bpy.context.object
    trigger.name = f"{busstop_name}_trigger"
    trigger.scale = (2, 1, 3)  # Make it wider
    
    # Create passenger spawn points
    # Create 5 spawn points in a line
    for i in range(5):
        offset_x = (i - 2) * 0.5  # Spread them out
        spawn_loc = (x + offset_x, y, z)
        
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=spawn_loc)
        spawn = bpy.context.object
        spawn.name = f"{busstop_name}.{i:03d}"
        spawn.empty_draw_size = 0.3
    
    print(f"Created objects for bus stop: {busstop_name}")

def create_all_busstops_from_entrypoints(entrypoints_file):
    """Create bus stop objects for all entrypoints"""
    
    import os
    if not os.path.exists(entrypoints_file):
        print(f"Error: File not found: {entrypoints_file}")
        return
    
    # Read and parse entrypoints
    with open(entrypoints_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    current_entry = {}
    
    for line in content.split('\\n'):
        line = line.strip()
        if line.startswith('[entrypoint_'):
            if current_entry:
                entries.append(current_entry)
            current_entry = {}
        elif '=' in line:
            key, value = line.split('=', 1)
            current_entry[key] = value
    
    if current_entry:
        entries.append(current_entry)
    
    # Create bus stop objects for each entry
    for entry in entries:
        if 'name' not in entry:
            continue
        
        name = entry['name']
        x = float(entry.get('posX', 0))
        y = float(entry.get('posY', 0))
        z = float(entry.get('posZ', 0))
        
        # Convert Unity to Blender coordinates (swap Y and Z)
        blender_pos = (x, z, y)
        
        create_busstop_objects(name, blender_pos)
    
    print(f"Created bus stop objects for {len(entries)} stops")

# Main execution
if __name__ == "__main__":
    # Update this path to your entrypoints.txt file
    entrypoints_file = "PATH_TO_YOUR_MAP/tiles/ROUTE_NAME/entrypoints.txt"
    
    # Call the function
    create_all_busstops_from_entrypoints(entrypoints_file)
'''
        
        script_path = os.path.join(scripts_dir, 'create_busstop_markers.py')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
    
    def _create_road_mesh_script(self, scripts_dir: str) -> None:
        """Create Blender script to create basic road mesh from OSM data"""
        script_content = '''"""
Blender 2.79 Script: Create Basic Road Mesh
This script creates a basic road mesh connecting bus stops
"""

import bpy
import math

def create_road_between_points(points, road_width=5.0):
    """
    Create a simple road mesh connecting the given points
    
    Args:
        points: List of (x, y, z) tuples in Blender coordinates
        road_width: Width of the road in meters
    """
    
    if len(points) < 2:
        print("Need at least 2 points to create a road")
        return
    
    # Create vertices for the road mesh
    verts = []
    edges = []
    faces = []
    
    half_width = road_width / 2.0
    
    for i, point in enumerate(points):
        x, y, z = point
        
        # Calculate perpendicular direction for road width
        if i < len(points) - 1:
            # Use direction to next point
            dx = points[i+1][0] - x
            dy = points[i+1][1] - y
        else:
            # Use direction from previous point
            dx = x - points[i-1][0]
            dy = y - points[i-1][1]
        
        # Normalize and rotate 90 degrees
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx, dy = dx/length, dy/length
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = 1, 0
        
        # Create left and right vertices
        left = (x + perp_x * half_width, y + perp_y * half_width, z)
        right = (x - perp_x * half_width, y - perp_y * half_width, z)
        
        verts.extend([left, right])
        
        # Create faces between segments
        if i > 0:
            base = (i - 1) * 2
            # Create quad face
            face = (base, base + 1, base + 3, base + 2)
            faces.append(face)
    
    # Create mesh
    mesh = bpy.data.meshes.new("Road_Mesh")
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    
    # Create object
    obj = bpy.data.objects.new("Road", mesh)
    bpy.context.scene.objects.link(obj)
    
    print(f"Created road mesh with {len(verts)} vertices and {len(faces)} faces")
    return obj

def create_road_from_entrypoints(entrypoints_file, road_width=5.0):
    """Create a road connecting all bus stops from entrypoints file"""
    
    import os
    if not os.path.exists(entrypoints_file):
        print(f"Error: File not found: {entrypoints_file}")
        return
    
    # Read and parse entrypoints
    with open(entrypoints_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    current_entry = {}
    
    for line in content.split('\\n'):
        line = line.strip()
        if line.startswith('[entrypoint_'):
            if current_entry:
                entries.append(current_entry)
            current_entry = {}
        elif '=' in line:
            key, value = line.split('=', 1)
            current_entry[key] = value
    
    if current_entry:
        entries.append(current_entry)
    
    # Extract positions
    points = []
    for entry in entries:
        x = float(entry.get('posX', 0))
        y = float(entry.get('posY', 0))
        z = float(entry.get('posZ', 0))
        
        # Convert Unity to Blender coordinates (swap Y and Z)
        blender_pos = (x, z, y)
        points.append(blender_pos)
    
    # Create road mesh
    if points:
        create_road_between_points(points, road_width)
        print(f"Created road connecting {len(points)} bus stops")

# Main execution
if __name__ == "__main__":
    # Update this path to your entrypoints.txt file
    entrypoints_file = "PATH_TO_YOUR_MAP/tiles/ROUTE_NAME/entrypoints.txt"
    road_width = 5.0  # Road width in meters
    
    # Call the function
    create_road_from_entrypoints(entrypoints_file, road_width)
'''
        
        script_path = os.path.join(scripts_dir, 'create_road_mesh.py')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
    
    def _create_blender_scripts_readme(self, scripts_dir: str) -> None:
        """Create README for Blender scripts"""
        readme_content = '''# Blender Helper Scripts for PBSU Map Creation

These Python scripts automate repetitive tasks in Blender 2.79 when creating PBSU maps.

## Prerequisites

- Blender 2.79 (required for PBSU compatibility)
- Your converted OSM to PBSU map files

## Scripts Overview

### 1. import_entrypoints.py
Imports bus stop positions from entrypoints.txt and creates empty objects as markers.

**Usage:**
1. Open Blender 2.79
2. Open the script in Blender's Text Editor (Window > Toggle System Console)
3. Update the `entrypoints_file` path to point to your entrypoints.txt
4. Run the script (Alt+P or click "Run Script")

This will create sphere empties at each bus stop location.

### 2. create_busstop_markers.py
Creates bus stop trigger objects and passenger spawn points.

**Usage:**
1. Open Blender 2.79
2. Open the script in Blender's Text Editor
3. Update the `entrypoints_file` path
4. Run the script

This will create:
- A trigger object (cube) for each bus stop
- 5 passenger spawn points (empty axes) for each stop

### 3. create_road_mesh.py
Creates a basic road mesh connecting all bus stops.

**Usage:**
1. Open Blender 2.79
2. Open the script in Blender's Text Editor
3. Update the `entrypoints_file` path
4. Optionally adjust `road_width` (default: 5 meters)
5. Run the script

This creates a simple road mesh. You'll need to refine it manually.

## Coordinate System Notes

**Important:** Unity (PBSU) and Blender use different coordinate systems:

- **Unity/PBSU:** X (east-west), Y (up-down), Z (north-south)
- **Blender 2.79:** X (east-west), Y (north-south), Z (up-down)

The scripts automatically handle this conversion when importing coordinates.

## Workflow Recommendation

1. Run `import_entrypoints.py` first to see all bus stop locations
2. Run `create_road_mesh.py` to create a basic road connecting stops
3. Manually refine the road mesh, add curves, intersections
4. Run `create_busstop_markers.py` to add trigger objects and spawn points
5. Add buildings, scenery, and other details manually
6. Export to .3ds format (File > Export > 3D Studio)

## Naming Conventions

**Critical:** Object names must match the internal names in the configuration files!

- Bus stop triggers: `{stopname}_trigger`
- Passenger spawn points: `{stopname}.000`, `{stopname}.001`, etc.

Where `{stopname}` is the internal name from entrypoints.txt (with spaces replaced by underscores).

## Export Settings

When exporting to .3ds format:
- Selection Only: No (export all)
- Scale: 1.0
- Apply Modifiers: Yes
- Forward: Y Forward
- Up: Z Up

## Troubleshooting

**Script doesn't run:**
- Make sure you're using Blender 2.79 (not 2.8+)
- Check that the file path is correct (use absolute paths)
- Check Python console for error messages

**Objects appear at wrong locations:**
- Verify your entrypoints.txt file is correct
- Check coordinate system conversion

**Bus stops don't work in game:**
- Verify object naming exactly matches internal names
- Check that trigger objects are at correct height (Y=0 usually)
- Ensure passenger spawn points are properly named

## Additional Resources

See the PBSU mapping tutorials in the `ajuda - help/` folder for complete mapping guides.

## Tips

- Start simple! Don't model the entire city at once
- Test in PBSU frequently during development
- Keep polygon count reasonable (under 300k triangles for mobile)
- Use simple placeholder textures first, refine later
- The scripts create basic geometry - manual refinement is needed for quality

Happy mapping! 🚌🗺️
'''
        
        readme_path = os.path.join(scripts_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def generate_checklist(self) -> None:
        """Generate a detailed checklist for manual work"""
        checklist_path = os.path.join(self.map_dir, 'POST_CONVERSION_CHECKLIST.md')
        
        print("Generating post-conversion checklist...")
        
        checklist_content = f'''# Post-Conversion Checklist for {self.map_name}

This checklist guides you through all steps needed after running the OSM to PBSU converter.

## ✅ Automated Steps (Already Done)

- [x] Created directory structure
- [x] Generated entrypoints.txt
- [x] Generated entrypoints_list.txt
- [x] Created bus stop configuration files
- [x] Created placeholder textures
- [x] Created destination display templates
- [x] Created preview image template
- [x] Generated Blender helper scripts

## 🔨 Manual Steps (You Need to Do)

### Phase 1: 3D Modeling (Blender 2.79)

- [ ] **Install Blender 2.79** (required for PBSU compatibility)
  - Download from: https://download.blender.org/release/Blender2.79/
  
- [ ] **Import bus stop markers**
  - Run `blender_scripts/import_entrypoints.py` in Blender
  - This creates markers showing where bus stops should be
  
- [ ] **Create basic road mesh**
  - Run `blender_scripts/create_road_mesh.py` in Blender
  - OR model roads manually using the bus stop positions as guides
  
- [ ] **Refine road geometry**
  - Add curves to roads
  - Add intersections
  - Model lanes properly
  - Ensure roads connect to all bus stops
  
- [ ] **Create bus stop objects**
  - Run `blender_scripts/create_busstop_markers.py` OR
  - Manually create trigger objects: `{{stopname}}_trigger`
  - Manually create spawn points: `{{stopname}}.000`, `{{stopname}}.001`, etc.
  - Each stop needs 3-5 spawn points for passengers
  
- [ ] **Add buildings and scenery**
  - Model or import buildings
  - Add trees, signs, street furniture
  - Add sidewalks
  - Keep polygon count reasonable (<300k triangles)
  
- [ ] **UV unwrap and prepare for textures**
  - UV unwrap all objects
  - Organize UV maps efficiently
  
- [ ] **Export to .3ds format**
  - File > Export > 3D Studio (.3ds)
  - Save in: `tiles/{{route_name}}/`
  - Use scale: 1.0, Forward: Y, Up: Z

### Phase 2: Textures

- [ ] **Replace placeholder textures**
  - Current placeholders are in `textures/` folder
  - Create or download proper textures
  
- [ ] **Required texture types:**
  - [ ] Road asphalt/concrete
  - [ ] Building walls
  - [ ] Sidewalks
  - [ ] Grass/terrain
  - [ ] Any custom materials
  
- [ ] **Texture requirements:**
  - Use PNG format (JPG may cause issues)
  - Keep under 2048x2048 pixels (for mobile compatibility)
  - Power-of-two dimensions recommended (256, 512, 1024, 2048)
  - Small details can use smaller textures (even 4x4 for solid colors)

### Phase 3: Destinations

- [ ] **Configure route destinations**
  - Edit folders in `dest/{{route_name}}/`
  - Current templates: Terminal_A, Terminal_B, Centro
  
- [ ] **Create destination display images:**
  - [ ] Design destination text/graphics
  - [ ] Export as PNG (512x64 is common size)
  - [ ] Name as `0.png`, `1.png`, etc. for variations
  - [ ] Place in appropriate destination folder

### Phase 4: Preview and Metadata

- [ ] **Create preview image**
  - Replace `preview.png` with actual screenshot/render
  - Recommended size: 640x360px (16:9 ratio)
  - This shows in map selection screen
  
- [ ] **Test map configuration**
  - Verify all file names are correct
  - Check no special characters in filenames
  - Ensure directory structure matches PBSU requirements

### Phase 5: Testing

- [ ] **Copy to PBSU mods folder**
  - Windows: `Documents\\Proton Bus Mods\\maps\\`
  - Android: `/Android/data/com.viamep.../files/maps/`
  - Copy both `{{map_name}}/` folder and `{{map_name}}.map.txt`
  
- [ ] **Test in Proton Bus Simulator**
  - [ ] Map loads without errors
  - [ ] Bus stops appear correctly
  - [ ] Passengers spawn at stops
  - [ ] Textures display properly
  - [ ] Destinations work
  - [ ] No crashes or glitches
  
- [ ] **Refine based on testing**
  - Adjust bus stop positions if needed
  - Fix texture issues
  - Improve geometry
  - Optimize performance

### Phase 6: Polish and Release

- [ ] **Final optimization**
  - Check polygon count (aim for <300k)
  - Optimize textures (reduce size where possible)
  - Remove unused resources
  
- [ ] **Documentation**
  - Update README.md with map-specific info
  - Add credits for textures/models used
  - List any known issues
  
- [ ] **Share your map!**
  - Upload to busmods.com
  - Share in PBSU Facebook groups
  - Post on PBSU forums
  - Help others learn from your work

## 📚 Resources

- **Blender Scripts:** See `blender_scripts/README.md`
- **PBSU Tutorials:** See `ajuda - help/` folder in repository root
- **Bus Stop Info:** Check README.md for coordinates
- **Example Maps:** Download from busmods.com to learn

## 💡 Tips

1. **Start small:** Complete one section at a time, test frequently
2. **Use references:** Look at real photos of your route for accuracy
3. **Test early:** Import to PBSU and test as soon as you have basic geometry
4. **Keep backups:** Save versions as you progress
5. **Join community:** Ask for help in PBSU forums/groups
6. **Be patient:** Creating quality maps takes time!

## ⚠️ Common Issues

**Bus stops don't work:**
- Check object naming matches internal names exactly
- Verify trigger objects are at ground level (Y=0)
- Ensure spawn points exist and are properly named

**Textures look wrong:**
- Use PNG not JPG
- Check texture sizes (power of 2)
- Verify UV mapping

**Performance issues:**
- Reduce polygon count
- Use smaller textures
- Remove unnecessary details

**Map won't load:**
- Check .map.txt file syntax
- Verify all referenced files exist
- Check for special characters in filenames

---

**Progress:** Check off items as you complete them. Good luck! 🚌
'''
        
        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        
        print(f"  Created: POST_CONVERSION_CHECKLIST.md")
    
    def run_all(self, enable_ai: bool = False, route_name: str = None) -> None:
        """Run all automation tasks"""
        print(f"\n{'='*60}")
        print(f"Post-Conversion Automation for: {self.map_name}")
        print(f"{'='*60}\n")
        
        if not os.path.exists(self.map_dir):
            print(f"Error: Map directory not found: {self.map_dir}")
            return
        
        self.create_placeholder_textures()
        print()
        
        self.create_destination_templates()
        print()
        
        self.create_preview_template()
        print()
        
        self.generate_blender_helper_scripts()
        print()
        
        self.generate_checklist()
        print()
        
        print(f"{'='*60}")
        print("✓ Post-conversion automation complete!")
        print(f"{'='*60}")
        print()
        
        if enable_ai and route_name:
            print("🤖 AI Automation is available!")
            print()
            print("To run complete AI automation (3D models, textures, etc.):")
            print(f"  python ai_automation.py {self.map_dir} {route_name}")
            print()
            print("This will:")
            print("  - Automatically generate 3D models in Blender")
            print("  - Create procedural textures")
            print("  - Generate destination displays")
            print("  - Create preview image")
            print()
        else:
            print("Next steps:")
            print(f"1. Read: {os.path.join(self.map_dir, 'POST_CONVERSION_CHECKLIST.md')}")
            print(f"2. Open Blender 2.79 and use scripts in: {os.path.join(self.map_dir, 'blender_scripts/')}")
            print(f"3. Replace placeholder textures in: {os.path.join(self.map_dir, 'textures/')}")
            print(f"4. Customize destination displays in: {os.path.join(self.map_dir, 'dest/')}")
            print(f"5. Replace preview.png with actual map preview")
            print()
            print("💡 TIP: For fully automated generation, use:")
            print(f"   python ai_automation.py {self.map_dir} <route_name>")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Automate post-conversion tasks for OSM to PBSU maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run on a converted map
  python automate_post_conversion.py output/My_City
  
  # After running osm_to_pbsu.py
  python osm_to_pbsu.py route.json -m "My_City" -r "Route_1"
  python automate_post_conversion.py output/My_City

This script automates the tedious post-conversion tasks:
- Creates placeholder textures
- Generates destination display templates  
- Creates preview image template
- Generates Blender helper scripts
- Creates detailed checklist for manual work
        '''
    )
    
    parser.add_argument('map_dir', 
                       help='Path to map directory (e.g., output/My_City)')
    parser.add_argument('--enable-ai', action='store_true',
                       help='Show AI automation option in output')
    parser.add_argument('--route-name',
                       help='Route name for AI automation suggestion')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.map_dir):
        print(f"Error: Directory not found: {args.map_dir}")
        print()
        print("Make sure you've run osm_to_pbsu.py first to create the map structure.")
        sys.exit(1)
    
    # Auto-detect route name if not provided
    route_name = args.route_name
    if not route_name:
        tiles_dir = os.path.join(args.map_dir, 'tiles')
        if os.path.exists(tiles_dir):
            routes = [d for d in os.listdir(tiles_dir) if os.path.isdir(os.path.join(tiles_dir, d))]
            if routes:
                route_name = routes[0]
    
    automator = PostConversionAutomator(args.map_dir)
    
    try:
        automator.run_all(enable_ai=args.enable_ai or True, route_name=route_name)
    except Exception as e:
        print(f"Error during automation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
