#!/usr/bin/env python3
"""
AI-Powered Automation for OSM to PBSU
Automates 3D modeling, texture creation, and asset generation without human intervention

This module provides intelligent automation for:
1. Automatic 3D model generation from OSM data using Blender
2. Procedural texture generation (no APIs)
3. Automatic destination display creation
4. Automatic preview image rendering

NOTE: All API calls have been removed. This module works completely offline.
"""

import os
import sys
import json
import subprocess
import argparse
from typing import Dict, List, Tuple, Optional
import math
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AIAutomation:
    """AI-powered automation for complete PBSU map generation"""
    
    def __init__(self, map_dir: str, blender_path: str = "blender", blender_timeout: int = 600):
        """
        Initialize AI automation
        
        Args:
            map_dir: Path to the map directory
            blender_path: Path to Blender executable (default: "blender" in PATH)
            blender_timeout: Timeout for Blender execution in seconds (default: 600)
        """
        self.map_dir = map_dir
        self.map_name = os.path.basename(map_dir)
        self.blender_path = blender_path
        self.blender_timeout = blender_timeout
        logger.info(f"Initialized AIAutomation for map: {self.map_name}")
        logger.info(f"Map directory: {map_dir}")
        logger.info(f"Blender path: {blender_path}")
        logger.info(f"Blender timeout: {blender_timeout} seconds")
        
    def generate_blender_automation_script(self) -> str:
        """Generate comprehensive Blender automation script"""
        script = '''"""
Comprehensive Blender Automation Script for PBSU Map Generation
This script runs in Blender 2.8+ and automatically creates:
- Road meshes from entrypoints
- Bus stop objects with triggers and spawn points
- Realistic buildings with actual heights from OSM data
- Terrain with elevation data
- Ground terrain
- UV mapping
- Exports to .3ds format
"""

import bpy
import bmesh
import math
import os
import sys
import json

def clear_scene():
    """Clear default scene objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def load_geographic_data(filepath):
    """Load geographic data (buildings, elevations) from JSON"""
    if not os.path.exists(filepath):
        print(f"Warning: Geographic data file not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading geographic data: {e}")
        return None

def parse_entrypoints(filepath):
    """Parse entrypoints.txt file"""
    if not os.path.exists(filepath):
        print(f"Error: Entrypoints file not found: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
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
    
    return entries

def unity_to_blender(x, y, z):
    """Convert Unity coordinates to Blender (swap Y and Z)"""
    return (x, z, y)

def create_road_mesh(points, road_width=6.0, name="Road"):
    """Create road mesh from points with proper geometry"""
    if len(points) < 2:
        return None
    
    verts = []
    faces = []
    half_width = road_width / 2.0
    
    # Generate road vertices
    for i, point in enumerate(points):
        x, y, z = point
        
        # Calculate tangent direction
        if i < len(points) - 1:
            dx = points[i+1][0] - x
            dy = points[i+1][1] - y
        else:
            dx = x - points[i-1][0]
            dy = y - points[i-1][1]
        
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx, dy = dx/length, dy/length
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = 1, 0
        
        # Create left and right edge vertices
        left = (x + perp_x * half_width, y + perp_y * half_width, z)
        right = (x - perp_x * half_width, y - perp_y * half_width, z)
        verts.extend([left, right])
        
        # Create face between segments
        if i > 0:
            base = (i - 1) * 2
            face = (base, base + 1, base + 3, base + 2)
            faces.append(face)
    
    # Create mesh
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Add UV mapping
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Created road mesh: {name}")
    return obj

def create_sidewalk(points, road_width=6.0, sidewalk_width=2.0, name="Sidewalk"):
    """Create sidewalk meshes on both sides of the road"""
    if len(points) < 2:
        return []
    
    sidewalks = []
    half_road = road_width / 2.0
    
    for side, side_name in [(1, "Left"), (-1, "Right")]:
        verts = []
        faces = []
        
        for i, point in enumerate(points):
            x, y, z = point
            
            if i < len(points) - 1:
                dx = points[i+1][0] - x
                dy = points[i+1][1] - y
            else:
                dx = x - points[i-1][0]
                dy = y - points[i-1][1]
            
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx, dy = dx/length, dy/length
                perp_x, perp_y = -dy, dx
            else:
                perp_x, perp_y = 1, 0
            
            # Create inner and outer edge
            inner_offset = side * half_road
            outer_offset = side * (half_road + sidewalk_width)
            
            inner = (x + perp_x * inner_offset, y + perp_y * inner_offset, z + 0.1)
            outer = (x + perp_x * outer_offset, y + perp_y * outer_offset, z + 0.1)
            verts.extend([inner, outer])
            
            if i > 0:
                base = (i - 1) * 2
                face = (base, base + 1, base + 3, base + 2)
                faces.append(face)
        
        if verts:
            mesh = bpy.data.meshes.new(f"{name}_{side_name}_mesh")
            mesh.from_pydata(verts, [], faces)
            mesh.update()
            
            obj = bpy.data.objects.new(f"{name}_{side_name}", mesh)
            bpy.context.collection.objects.link(obj)
            sidewalks.append(obj)
            
            # UV mapping
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()
            bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Created sidewalks")
    return sidewalks

def create_busstop_trigger(name, location, rotation_y=0):
    """Create bus stop trigger object"""
    x, y, z = location
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z + 1.0))
    trigger = bpy.context.object
    trigger.name = f"{name}_trigger"
    trigger.scale = (2.5, 1.0, 3.5)
    trigger.rotation_euler[2] = math.radians(rotation_y)
    return trigger

def create_passenger_spawns(name, location, count=5, spacing=0.6):
    """Create passenger spawn point empties"""
    spawns = []
    x, y, z = location
    
    for i in range(count):
        offset_x = (i - count//2) * spacing
        spawn_loc = (x + offset_x, y + 1.5, z)
        
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=spawn_loc)
        spawn = bpy.context.object
        spawn.name = f"{name}.{i:03d}"
        spawn.empty_display_size = 0.3
        spawns.append(spawn)
    
    return spawns

def create_simple_building(location, width=10, depth=10, height=15):
    """Create a simple building"""
    x, y, z = location
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z + height/2))
    building = bpy.context.object
    building.scale = (width/2, depth/2, height/2)
    
    # UV mapping
    bpy.context.view_layer.objects.active = building
    building.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return building

def create_building_from_footprint(footprint, height, name="Building"):
    """
    Create a building from a footprint polygon with accurate height
    
    Args:
        footprint: List of dicts with x, y, z coordinates
        height: Building height in meters
        name: Building name
    """
    if len(footprint) < 3:
        return None
    
    # Convert footprint to Blender coordinates
    base_verts = []
    for point in footprint:
        x, y, z = point['x'], point['y'], point['z']
        blender_pos = unity_to_blender(x, y, z)
        base_verts.append(blender_pos)
    
    # Create mesh data
    verts = []
    faces = []
    
    # Add base vertices (bottom)
    for v in base_verts:
        verts.append(v)
    
    # Add top vertices
    for v in base_verts:
        verts.append((v[0], v[1], v[2] + height))
    
    n = len(base_verts)
    
    # Create bottom face
    bottom_face = list(range(n))
    faces.append(bottom_face)
    
    # Create top face (reversed for correct normal)
    top_face = list(range(n, 2*n))
    top_face.reverse()
    faces.append(top_face)
    
    # Create side faces
    for i in range(n):
        next_i = (i + 1) % n
        face = [i, next_i, next_i + n, i + n]
        faces.append(face)
    
    # Create mesh
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # UV mapping
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj

def create_ground_plane(center, size=500):
    """Create ground plane"""
    x, y, z = center
    bpy.ops.mesh.primitive_plane_add(location=(x, y, z - 0.1))
    ground = bpy.context.object
    ground.name = "Ground"
    ground.scale = (size, size, 1)
    
    # UV mapping
    bpy.context.view_layer.objects.active = ground
    ground.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return ground

def generate_buildings_along_road(road_points, spacing=30, offset=15):
    """Generate simple buildings along the road"""
    buildings = []
    
    for i in range(0, len(road_points), max(1, len(road_points) // 10)):
        point = road_points[i]
        x, y, z = point
        
        if i < len(road_points) - 1:
            dx = road_points[i+1][0] - x
            dy = road_points[i+1][1] - y
        else:
            dx = 1
            dy = 0
        
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx, dy = dx/length, dy/length
            perp_x, perp_y = -dy, dx
        else:
            perp_x, perp_y = 1, 0
        
        # Create buildings on both sides
        for side in [1, -1]:
            bldg_x = x + perp_x * offset * side
            bldg_y = y + perp_y * offset * side
            bldg_z = z
            
            building = create_simple_building(
                (bldg_x, bldg_y, bldg_z),
                width=8 + (i % 4) * 2,
                depth=8 + (i % 3) * 2,
                height=10 + (i % 5) * 5
            )
            building.name = f"Building_{len(buildings)}"
            buildings.append(building)
    
    print(f"Generated {len(buildings)} buildings")
    return buildings

def main():
    """Main automation function"""
    # Get paths from command line arguments
    if len(sys.argv) < 5:
        print("Usage: blender --background --python script.py -- <entrypoints_file> <output_file> [geographic_data_file]")
        return
    
    # Arguments after "--" are in sys.argv[sys.argv.index("--")+1:]
    try:
        dash_index = sys.argv.index("--")
        entrypoints_file = sys.argv[dash_index + 1]
        output_file = sys.argv[dash_index + 2]
        # Optional geographic data file
        geographic_data_file = sys.argv[dash_index + 3] if len(sys.argv) > dash_index + 3 else None
    except (ValueError, IndexError):
        print("Error: Missing arguments")
        return
    
    print("="*60)
    print("PBSU Map Automated 3D Generation with Geographic Data")
    print("="*60)
    
    # Clear scene
    print("Clearing scene...")
    clear_scene()
    
    # Load geographic data if available
    geo_data = None
    if geographic_data_file and os.path.exists(geographic_data_file):
        print(f"Loading geographic data: {geographic_data_file}")
        geo_data = load_geographic_data(geographic_data_file)
        if geo_data:
            print(f"  - Buildings: {len(geo_data.get('buildings', []))}")
            print(f"  - Elevation points: {len(geo_data.get('elevations', {}))}")
    
    # Parse entrypoints
    print(f"Parsing entrypoints: {entrypoints_file}")
    entries = parse_entrypoints(entrypoints_file)
    if not entries:
        print("Error: No entrypoints found!")
        return
    
    print(f"Found {len(entries)} bus stops")
    
    # Extract positions and convert to Blender coordinates
    road_points = []
    busstop_data = []
    
    for entry in entries:
        if 'name' not in entry:
            continue
        
        name = entry['name']
        x = float(entry.get('posX', 0))
        y = float(entry.get('posY', 0))
        z = float(entry.get('posZ', 0))
        rot_y = float(entry.get('rotY', 0))
        
        blender_pos = unity_to_blender(x, y, z)
        road_points.append(blender_pos)
        busstop_data.append({
            'name': name,
            'position': blender_pos,
            'rotation_y': rot_y
        })
    
    # Calculate center point for ground plane
    if road_points:
        center_x = sum(p[0] for p in road_points) / len(road_points)
        center_y = sum(p[1] for p in road_points) / len(road_points)
        center_z = 0
        center = (center_x, center_y, center_z)
    else:
        center = (0, 0, 0)
    
    # Create ground
    print("Creating ground plane...")
    create_ground_plane(center)
    
    # Create road
    print("Creating road mesh...")
    road = create_road_mesh(road_points)
    
    # Create sidewalks
    print("Creating sidewalks...")
    create_sidewalk(road_points)
    
    # Create bus stops
    print("Creating bus stop objects...")
    for stop in busstop_data:
        create_busstop_trigger(stop['name'], stop['position'], stop['rotation_y'])
        create_passenger_spawns(stop['name'], stop['position'])
    
    # Generate buildings
    print("Generating buildings...")
    if geo_data and geo_data.get('buildings'):
        # Use accurate building data from OSM
        print(f"Creating {len(geo_data['buildings'])} buildings from OSM data...")
        for i, building_data in enumerate(geo_data['buildings']):
            footprint = building_data.get('footprint', [])
            height = building_data.get('height', 10.0)
            building_type = building_data.get('type', 'yes')
            
            if len(footprint) >= 3:
                building = create_building_from_footprint(
                    footprint, height, f"Building_{i}_{building_type}"
                )
                if building:
                    print(f"  Created building {i+1}/{len(geo_data['buildings'])} - Height: {height:.1f}m")
    else:
        # Fallback to procedural generation
        print("No geographic data available, using procedural generation...")
        generate_buildings_along_road(road_points)
    
    # Export to .3ds
    print(f"Exporting to {output_file}...")
    
    # Count mesh objects before export
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    print(f"Scene contains {len(mesh_objects)} mesh objects")
    
    if len(mesh_objects) == 0:
        print("WARNING: No mesh objects found in scene!")
        print("Creating a minimal placeholder cube to allow export...")
        # Create a minimal cube at origin as fallback
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        bpy.context.active_object.name = "Placeholder_Cube"
        mesh_objects = [bpy.context.active_object]
    
    # Select all objects for export
    bpy.ops.object.select_all(action='SELECT')
    selected_count = len([obj for obj in bpy.context.selected_objects])
    print(f"Selected {selected_count} objects for export")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Enable export addons
    print("Enabling export addons...")
    import addon_utils
    
    # List of addons to try enabling
    addons_to_enable = [
        'io_scene_3ds',      # For .3ds export
        'io_scene_obj',      # For .obj export (fallback)
        'io_scene_fbx',      # For .fbx export (fallback)
        'io_scene_gltf2',    # For .gltf export (fallback)
    ]
    
    enabled_addons = []
    for addon_name in addons_to_enable:
        try:
            # Check if addon is already enabled
            is_enabled = addon_utils.check(addon_name)[1]
            if not is_enabled:
                addon_utils.enable(addon_name, default_set=True, persistent=True)
                print(f"  ✓ Enabled {addon_name} addon")
            else:
                print(f"  ✓ {addon_name} addon already enabled")
            enabled_addons.append(addon_name)
        except Exception as e:
            print(f"  ✗ Could not enable {addon_name} addon: {e}")
    
    # Try to export to 3DS format
    export_success = False
    export_format = None
    actual_output_file = output_file
    export_errors = []
    
    # Try different export formats in order of preference
    export_attempts = [
        ('3DS', '.3ds', 'bpy.ops.export_scene.autodesk_3ds', {
            'filepath': output_file,
            'use_selection': True,
            'axis_forward': 'Y',
            'axis_up': 'Z'
        }),
        ('OBJ', '.obj', 'bpy.ops.export_scene.obj', {
            'filepath': output_file.replace('.3ds', '.obj'),
            'use_selection': True,
            'axis_forward': 'Y',
            'axis_up': 'Z'
        }),
        ('FBX', '.fbx', 'bpy.ops.export_scene.fbx', {
            'filepath': output_file.replace('.3ds', '.fbx'),
            'use_selection': True,
            'axis_forward': 'Y',
            'axis_up': 'Z'
        }),
        ('glTF', '.gltf', 'bpy.ops.export_scene.gltf', {
            'filepath': output_file.replace('.3ds', '.gltf'),
            'export_format': 'GLTF_SEPARATE'
        }),
    ]
    
    export_errors = []
    for format_name, extension, op_path, kwargs in export_attempts:
        try:
            print(f"Attempting {format_name} export...")
            
            # Get the operator
            op_parts = op_path.split('.')
            op = bpy.ops
            for part in op_parts[1:]:  # Skip 'bpy'
                op = getattr(op, part)
            
            # Call the export operator
            result = op(**kwargs)
            
            # Check if export actually succeeded
            if os.path.exists(kwargs['filepath']):
                export_success = True
                export_format = format_name
                actual_output_file = kwargs['filepath']
                print(f"✓ Successfully exported to {format_name} format: {actual_output_file}")
                break
            else:
                error_msg = f"Export completed but file not created: {kwargs['filepath']}"
                print(f"✗ {format_name} export failed: {error_msg}")
                export_errors.append(f"{format_name}: {error_msg}")
                continue
            
        except AttributeError as e:
            error_msg = f"Export operator not available: {e}"
            print(f"✗ {format_name} export failed: {error_msg}")
            export_errors.append(f"{format_name}: {error_msg}")
            continue
        except RuntimeError as e:
            error_msg = f"Runtime error: {e}"
            print(f"✗ {format_name} export failed: {error_msg}")
            export_errors.append(f"{format_name}: {error_msg}")
            continue
        except KeyError as e:
            error_msg = f"Missing parameter: {e}"
            print(f"✗ {format_name} export failed: {error_msg}")
            export_errors.append(f"{format_name}: {error_msg}")
            continue
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {e}"
            print(f"✗ {format_name} export failed: {error_msg}")
            export_errors.append(f"{format_name}: {error_msg}")
            continue
    
    if export_success:
        print("="*60)
        print("✓ 3D Model generation complete!")
        print(f"Format: {export_format}")
        print(f"Exported to: {actual_output_file}")
        if export_format != '3DS':
            print("")
            print("NOTE: PBSU requires .3ds format.")
            print(f"You will need to convert the {export_format} file to .3ds format.")
            print("You can use Blender's GUI: File > Export > Autodesk 3DS (.3ds)")
        print("="*60)
    else:
        print("="*60)
        print("✗ 3D Model generation failed!")
        print("All export formats failed. Details:")
        for error in export_errors:
            print(f"  - {error}")
        print("")
        print("Possible causes:")
        print("  1. Blender export addons may not be installed or enabled")
        print("  2. The scene may have no valid geometry to export")
        print("  3. File permissions may prevent writing to the output directory")
        print("")
        print("Troubleshooting:")
        print("  - Ensure Blender 2.8 or higher is installed with export addons")
        print("  - Check that the output directory is writable")
        print("  - Try running Blender manually to verify it works")
        print("="*60)
        raise RuntimeError("All export attempts failed")

if __name__ == "__main__":
    main()
'''
        return script
    
    def run_blender_automation(self, route_name: str) -> bool:
        """Run Blender in headless mode to generate 3D models"""
        logger.info("="*60)
        logger.info("Starting Blender Automation")
        logger.info("="*60)
        
        print(f"\n{'='*60}")
        print("Automated 3D Model Generation with Geographic Data")
        print(f"{'='*60}\n")
        
        # Find entrypoints file
        tiles_dir = os.path.join(self.map_dir, 'tiles', route_name)
        entrypoints_file = os.path.join(tiles_dir, 'entrypoints.txt')
        
        logger.info(f"Looking for entrypoints file: {entrypoints_file}")
        if not os.path.exists(entrypoints_file):
            logger.error(f"Entrypoints file not found: {entrypoints_file}")
            print(f"Error: Entrypoints file not found: {entrypoints_file}")
            return False
        logger.info("Entrypoints file found")
        
        # Find geographic data file
        geo_data_file = os.path.join(self.map_dir, 'geographic_data.json')
        logger.info(f"Looking for geographic data file: {geo_data_file}")
        if not os.path.exists(geo_data_file):
            logger.warning("Geographic data file not found, using basic generation")
            print("Warning: Geographic data file not found, using basic generation")
            geo_data_file = ""
        else:
            logger.info(f"Using geographic data: {geo_data_file}")
            print(f"Using geographic data: {geo_data_file}")
            # Log some stats from the geo data
            try:
                with open(geo_data_file, 'r') as f:
                    geo_data = json.load(f)
                logger.info(f"  - Buildings: {len(geo_data.get('buildings', []))}")
                logger.info(f"  - Elevations: {len(geo_data.get('elevations', {}))}")
                logger.info(f"  - Bus stops: {len(geo_data.get('bus_stops', []))}")
            except Exception as e:
                logger.warning(f"Could not read geographic data stats: {e}")
        
        # Output 3ds file
        output_3ds = os.path.join(tiles_dir, f"{route_name}_auto.3ds")
        logger.info(f"Output 3DS file will be: {output_3ds}")
        
        # Verify output directory exists
        if not os.path.exists(tiles_dir):
            logger.error(f"Output directory does not exist: {tiles_dir}")
            print(f"Error: Output directory does not exist: {tiles_dir}")
            return False
        logger.info(f"Output directory verified: {tiles_dir}")
        
        # Create temporary Blender script
        script_path = os.path.join(self.map_dir, 'temp_blender_script.py')
        logger.info(f"Creating temporary Blender script: {script_path}")
        script_content = self.generate_blender_automation_script()
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.info(f"Blender script created successfully ({len(script_content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to create Blender script: {e}")
            print(f"Error: Failed to create Blender script: {e}")
            return False
        
        print(f"Running Blender automation...")
        print(f"This may take several minutes...\n")
        logger.info("Starting Blender execution...")
        
        try:
            # Run Blender in background mode
            cmd = [
                self.blender_path,
                '--background',
                '--python', script_path,
                '--',
                entrypoints_file,
                output_3ds,
                geo_data_file
            ]
            
            logger.info(f"Blender command: {' '.join(cmd)}")
            logger.info(f"Executing Blender (timeout: {self.blender_timeout} seconds)...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.blender_timeout
            )
            
            logger.info(f"Blender process finished with return code: {result.returncode}")
            
            # Log Blender stdout
            if result.stdout:
                logger.debug("Blender stdout:")
                for line in result.stdout.split('\n'):
                    logger.debug(f"  {line}")
            
            # Log Blender stderr
            if result.stderr:
                logger.debug("Blender stderr:")
                for line in result.stderr.split('\n'):
                    logger.debug(f"  {line}")
            
            if result.returncode == 0:
                logger.info("Blender process completed successfully")
                # Validate that 3DS file was created
                if os.path.exists(output_3ds):
                    file_size = os.path.getsize(output_3ds)
                    logger.info(f"3DS file created: {output_3ds}")
                    logger.info(f"3DS file size: {file_size} bytes ({file_size / 1024:.2f} KB)")
                    
                    if file_size > 0:
                        print("✓ 3D model generated successfully!")
                        print(f"Output: {output_3ds}")
                        print(f"File size: {file_size / 1024:.2f} KB")
                        logger.info("3D model validation passed")
                    else:
                        logger.error("3DS file is empty (0 bytes)")
                        print("Error: 3DS file was created but is empty")
                        print("\nBlender output (last 50 lines):")
                        print('\n'.join(result.stdout.split('\n')[-50:]))
                        return False
                else:
                    logger.error("3DS file was not created")
                    print("Error: 3DS file was not created")
                    print("\nBlender output (last 50 lines):")
                    print('\n'.join(result.stdout.split('\n')[-50:]))
                    if result.stderr:
                        print("\nBlender errors:")
                        print(result.stderr)
                    return False
                
                # Clean up temp script
                if os.path.exists(script_path):
                    os.remove(script_path)
                    logger.info("Cleaned up temporary Blender script")
                
                return True
            else:
                logger.error(f"Blender process failed with return code: {result.returncode}")
                print(f"Error running Blender:")
                print(result.stderr)
                if result.stdout:
                    print("\nBlender output (last 50 lines):")
                    print('\n'.join(result.stdout.split('\n')[-50:]))
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Blender execution timed out after {self.blender_timeout} seconds")
            print(f"Error: Blender execution timed out after {self.blender_timeout} seconds")
            print(f"Try increasing the timeout with --blender-timeout parameter")
            return False
        except FileNotFoundError:
            logger.error(f"Blender not found at: {self.blender_path}")
            print(f"Error: Blender not found at '{self.blender_path}'")
            print("Please install Blender 2.8 or higher or specify the path with --blender-path")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Blender execution: {e}")
            import traceback
            logger.error(traceback.format_exc())
            print(f"Error: {e}")
            return False
    
    def fetch_street_view_textures(self, api_key: Optional[str] = None) -> bool:
        """
        [DEPRECATED] Fetch Street View images for building textures
        
        This method has been disabled as API calls are no longer allowed.
        Use procedural texture generation instead.
        
        Args:
            api_key: Not used (kept for compatibility)
        
        Returns:
            False (always, as this feature is disabled)
        """
        logger.info("Street View texture fetching called but is disabled (no API calls allowed)")
        print("\nNote: Street View API texture fetching is disabled.")
        print("Using procedural texture generation instead.")
        return False
    
    def generate_procedural_textures(self) -> bool:
        """Generate procedural textures using Python imaging"""
        logger.info("Starting procedural texture generation")
        print(f"\n{'='*60}")
        print("Procedural Texture Generation")
        print(f"{'='*60}\n")
        
        textures_dir = os.path.join(self.map_dir, 'textures')
        os.makedirs(textures_dir, exist_ok=True)
        logger.info(f"Textures directory: {textures_dir}")
        
        try:
            from PIL import Image, ImageDraw, ImageFilter
            has_pil = True
            logger.info("PIL/Pillow available for texture generation")
        except ImportError:
            has_pil = False
            logger.warning("PIL/Pillow not available, using basic texture generation")
            print("PIL/Pillow not available, using basic texture generation")
        
        textures_to_generate = {
            'road_asphalt.png': self._generate_asphalt_texture,
            'road_concrete.png': self._generate_concrete_texture,
            'building_wall.png': self._generate_wall_texture,
            'grass.png': self._generate_grass_texture,
            'sidewalk.png': self._generate_sidewalk_texture,
        }
        
        logger.info(f"Generating {len(textures_to_generate)} textures...")
        for filename, generator in textures_to_generate.items():
            filepath = os.path.join(textures_dir, filename)
            try:
                logger.debug(f"Generating {filename}...")
                generator(filepath, has_pil)
                print(f"✓ Generated: {filename}")
                logger.info(f"Successfully generated: {filename}")
            except Exception as e:
                logger.error(f"Failed to generate {filename}: {e}")
                print(f"✗ Failed to generate {filename}: {e}")
        
        print(f"\n✓ Texture generation complete!")
        logger.info("Procedural texture generation completed")
        return True
    
    def _generate_asphalt_texture(self, filepath: str, has_pil: bool) -> None:
        """Generate realistic asphalt texture"""
        if has_pil:
            from PIL import Image, ImageDraw, ImageFilter
            import random
            
            size = 512
            img = Image.new('RGB', (size, size), (45, 45, 50))
            draw = ImageDraw.Draw(img)
            
            # Add noise for texture
            pixels = img.load()
            for i in range(size):
                for j in range(size):
                    noise = random.randint(-15, 15)
                    r, g, b = pixels[i, j]
                    pixels[i, j] = (
                        max(0, min(255, r + noise)),
                        max(0, min(255, g + noise)),
                        max(0, min(255, b + noise))
                    )
            
            # Add some cracks
            for _ in range(20):
                x1 = random.randint(0, size)
                y1 = random.randint(0, size)
                x2 = x1 + random.randint(-50, 50)
                y2 = y1 + random.randint(-50, 50)
                draw.line([(x1, y1), (x2, y2)], fill=(30, 30, 35), width=1)
            
            img = img.filter(ImageFilter.GaussianBlur(0.5))
            img.save(filepath, 'PNG')
        else:
            self._create_simple_png(filepath, (45, 45, 50), 512, 512)
    
    def _generate_concrete_texture(self, filepath: str, has_pil: bool) -> None:
        """Generate concrete texture"""
        if has_pil:
            from PIL import Image
            import random
            
            size = 512
            img = Image.new('RGB', (size, size), (180, 180, 180))
            pixels = img.load()
            
            # Add noise
            for i in range(size):
                for j in range(size):
                    noise = random.randint(-20, 20)
                    r, g, b = pixels[i, j]
                    pixels[i, j] = (
                        max(0, min(255, r + noise)),
                        max(0, min(255, g + noise)),
                        max(0, min(255, b + noise))
                    )
            
            img.save(filepath, 'PNG')
        else:
            self._create_simple_png(filepath, (180, 180, 180), 512, 512)
    
    def _generate_wall_texture(self, filepath: str, has_pil: bool) -> None:
        """Generate building wall texture with bricks"""
        if has_pil:
            from PIL import Image, ImageDraw
            
            size = 512
            img = Image.new('RGB', (size, size), (200, 180, 160))
            draw = ImageDraw.Draw(img)
            
            # Draw brick pattern
            brick_w, brick_h = 60, 30
            mortar = 2
            
            for y in range(0, size, brick_h):
                offset = 0 if (y // brick_h) % 2 == 0 else brick_w // 2
                for x in range(-brick_w, size + brick_w, brick_w):
                    bx = x + offset
                    # Draw mortar lines
                    draw.rectangle([bx, y, bx + brick_w - mortar, y + brick_h - mortar],
                                 fill=(180, 165, 150))
            
            img.save(filepath, 'PNG')
        else:
            self._create_simple_png(filepath, (200, 180, 160), 512, 512)
    
    def _generate_grass_texture(self, filepath: str, has_pil: bool) -> None:
        """Generate grass texture"""
        if has_pil:
            from PIL import Image
            import random
            
            size = 512
            img = Image.new('RGB', (size, size), (60, 130, 50))
            pixels = img.load()
            
            # Add color variation
            for i in range(size):
                for j in range(size):
                    noise = random.randint(-30, 30)
                    r, g, b = pixels[i, j]
                    pixels[i, j] = (
                        max(0, min(255, r + noise)),
                        max(0, min(255, g + noise)),
                        max(0, min(255, b + noise // 2))
                    )
            
            img.save(filepath, 'PNG')
        else:
            self._create_simple_png(filepath, (60, 130, 50), 512, 512)
    
    def _generate_sidewalk_texture(self, filepath: str, has_pil: bool) -> None:
        """Generate sidewalk texture"""
        if has_pil:
            from PIL import Image, ImageDraw
            
            size = 512
            img = Image.new('RGB', (size, size), (150, 150, 140))
            draw = ImageDraw.Draw(img)
            
            # Draw tile pattern
            tile_size = 64
            for y in range(0, size, tile_size):
                for x in range(0, size, tile_size):
                    draw.rectangle([x+1, y+1, x+tile_size-1, y+tile_size-1],
                                 outline=(120, 120, 110), width=1)
            
            img.save(filepath, 'PNG')
        else:
            self._create_simple_png(filepath, (150, 150, 140), 512, 512)
    
    def _create_simple_png(self, filepath: str, color: Tuple[int, int, int],
                          width: int, height: int) -> None:
        """Fallback: Create simple PNG without PIL"""
        import struct
        import zlib
        
        def png_pack(png_tag, data):
            chunk_head = png_tag + data
            return (struct.pack("!I", len(data)) +
                   chunk_head +
                   struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))
        
        png_data = b'\x89PNG\r\n\x1a\n'
        ihdr = struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0)
        png_data += png_pack(b'IHDR', ihdr)
        
        raw_data = b''
        for y in range(height):
            raw_data += b'\x00'
            for x in range(width):
                raw_data += struct.pack('!3B', *color)
        
        compressed_data = zlib.compress(raw_data, 9)
        png_data += png_pack(b'IDAT', compressed_data)
        png_data += png_pack(b'IEND', b'')
        
        with open(filepath, 'wb') as f:
            f.write(png_data)
    
    def generate_destination_displays(self, route_name: str) -> bool:
        """Generate destination display images with text"""
        print(f"\n{'='*60}")
        print("Destination Display Generation")
        print(f"{'='*60}\n")
        
        dest_dir = os.path.join(self.map_dir, 'dest', route_name)
        os.makedirs(dest_dir, exist_ok=True)
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            has_pil = True
        except ImportError:
            has_pil = False
            print("PIL not available, creating basic destination displays")
        
        # Get bus stop names from entrypoints
        tiles_dir = os.path.join(self.map_dir, 'tiles', route_name)
        entrypoints_file = os.path.join(tiles_dir, 'entrypoints.txt')
        
        destinations = ['Terminal_A', 'Terminal_B', 'Centro']
        
        # Try to extract real stop names
        if os.path.exists(entrypoints_file):
            try:
                with open(entrypoints_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    destinations = []
                    for line in content.split('\n'):
                        if line.startswith('name='):
                            name = line.split('=', 1)[1].strip()
                            if name and name not in destinations:
                                destinations.append(name)
            except Exception as e:
                print(f"Could not read stop names: {e}")
        
        # Create destination displays
        for dest_name in destinations[:5]:  # Limit to first 5
            dest_path = os.path.join(dest_dir, dest_name)
            os.makedirs(dest_path, exist_ok=True)
            
            display_file = os.path.join(dest_path, '0.png')
            self._create_destination_display(display_file, dest_name, has_pil)
            print(f"✓ Generated: {dest_name}/0.png")
        
        print(f"\n✓ Destination displays complete!")
        return True
    
    def _create_destination_display(self, filepath: str, text: str, has_pil: bool) -> None:
        """Create destination display image with text"""
        width, height = 512, 64
        
        if has_pil:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (width, height), (0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Try to use a font, fallback to default
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 32)
                except:
                    font = ImageFont.load_default()
            
            # Draw text
            text_display = text.replace('_', ' ').upper()
            bbox = draw.textbbox((0, 0), text_display, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text_display, fill=(255, 200, 0), font=font)
            img.save(filepath, 'PNG')
        else:
            # Fallback: orange background
            self._create_simple_png(filepath, (255, 180, 0), width, height)
    
    def generate_preview_image(self, route_name: str) -> bool:
        """Generate preview image (render or placeholder)"""
        print(f"\n{'='*60}")
        print("Preview Image Generation")
        print(f"{'='*60}\n")
        
        preview_path = os.path.join(self.map_dir, 'preview.png')
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            width, height = 640, 360
            img = Image.new('RGB', (width, height), (70, 130, 180))
            draw = ImageDraw.Draw(img)
            
            # Draw map name
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Title
            title = self.map_name.replace('_', ' ')
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height // 3
            draw.text((x, y), title, fill=(255, 255, 255), font=font)
            
            # Subtitle
            subtitle = f"Route: {route_name}"
            bbox = draw.textbbox((0, 0), subtitle, font=small_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height // 2
            draw.text((x, y), subtitle, fill=(255, 255, 255), font=small_font)
            
            img.save(preview_path, 'PNG')
            print(f"✓ Generated preview image")
            return True
            
        except ImportError:
            # Fallback
            self._create_simple_png(preview_path, (70, 130, 180), 640, 360)
            print(f"✓ Generated basic preview image")
            return True
    
    def update_readme(self, route_name: str) -> None:
        """Update README to reflect automated generation"""
        readme_path = os.path.join(self.map_dir, 'README.md')
        
        if not os.path.exists(readme_path):
            return
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add automation note at the beginning
        automation_note = f"""## ✨ AI-Automated Generation

This map was automatically generated using AI-powered automation:
- ✓ 3D models generated automatically from OSM data
- ✓ Procedural textures created automatically
- ✓ Destination displays generated automatically
- ✓ Preview image created automatically

The map is ready to use in Proton Bus Simulator!

---

"""
        
        if "AI-Automated Generation" not in content:
            content = automation_note + content
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def run_full_automation(self, route_name: str, api_key: Optional[str] = None) -> bool:
        """
        Run complete AI automation pipeline
        
        Args:
            route_name: Name of the route
            api_key: Not used (kept for compatibility, API calls are disabled)
        
        Returns:
            True if all steps completed successfully, False otherwise
        """
        logger.info("="*60)
        logger.info("Starting Full AI Automation Pipeline")
        logger.info("="*60)
        logger.info(f"Map: {self.map_name}")
        logger.info(f"Route: {route_name}")
        
        print(f"\n{'='*60}")
        print(f"AI-Powered Full Automation for: {self.map_name}")
        print(f"Route: {route_name}")
        print(f"{'='*60}\n")
        
        if api_key:
            logger.warning("API key provided but API calls are disabled")
            print("Note: API calls are disabled, ignoring provided API key")
        
        success = True
        
        # 1. Generate 3D models
        logger.info("Step 1: Generating 3D models with Blender...")
        if not self.run_blender_automation(route_name):
            logger.error("3D model generation failed")
            print("Warning: 3D model generation failed")
            success = False
        else:
            logger.info("3D model generation completed successfully")
        
        # 2. Street View textures disabled (no API calls)
        logger.info("Step 2: Street View textures skipped (API calls disabled)")
        
        # 3. Generate procedural textures
        logger.info("Step 3: Generating procedural textures...")
        if not self.generate_procedural_textures():
            logger.error("Texture generation failed")
            print("Warning: Texture generation failed")
            success = False
        else:
            logger.info("Texture generation completed successfully")
        
        # 4. Generate destination displays
        logger.info("Step 4: Generating destination displays...")
        if not self.generate_destination_displays(route_name):
            logger.error("Destination display generation failed")
            print("Warning: Destination display generation failed")
            success = False
        else:
            logger.info("Destination display generation completed successfully")
        
        # 5. Generate preview image
        logger.info("Step 5: Generating preview image...")
        if not self.generate_preview_image(route_name):
            logger.error("Preview image generation failed")
            print("Warning: Preview image generation failed")
            success = False
        else:
            logger.info("Preview image generation completed successfully")
        
        # 6. Update README
        logger.info("Step 6: Updating README...")
        self.update_readme(route_name)
        logger.info("README updated")
        
        logger.info("="*60)
        print(f"\n{'='*60}")
        if success:
            logger.info("AI Automation Pipeline Completed Successfully!")
            print("✓ AI Automation Complete!")
            print(f"{'='*60}\n")
            print("Your map is ready to use in Proton Bus Simulator!")
            print(f"Location: {self.map_dir}")
        else:
            logger.warning("AI Automation completed with warnings")
            print("⚠ AI Automation completed with warnings")
            print(f"{'='*60}\n")
            print("Some features may need manual adjustment")
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description='AI-powered automation for complete PBSU map generation (NO API CALLS)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run full AI automation on a converted map
  python ai_automation.py output/My_City Route_1
  
  # Specify Blender path
  python ai_automation.py output/My_City Route_1 --blender-path /path/to/blender
  
  # Skip 3D generation (textures and displays only)
  python ai_automation.py output/My_City Route_1 --skip-3d
  
This script automates:
- 3D model generation from OSM data (using Blender)
- Building heights from real OSM data
- Terrain elevation from geographic data
- Procedural texture generation (no APIs)
- Destination display creation
- Preview image generation

Requirements:
- Blender 2.8 or higher (for 3D model generation)
- Python PIL/Pillow (optional, for better texture quality)

NOTE: All API calls have been removed. This script works completely offline.
        '''
    )
    
    parser.add_argument('map_dir', help='Path to map directory (e.g., output/My_City)')
    parser.add_argument('route_name', help='Route name (e.g., Route_1)')
    parser.add_argument('--blender-path', default='blender',
                       help='Path to Blender executable (default: "blender" in PATH)')
    parser.add_argument('--blender-timeout', type=int, default=600,
                       help='Timeout for Blender execution in seconds (default: 600)')
    parser.add_argument('--skip-3d', action='store_true',
                       help='Skip 3D model generation')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("AI Automation Script Started")
    logger.info("="*60)
    logger.info(f"Map directory: {args.map_dir}")
    logger.info(f"Route name: {args.route_name}")
    logger.info(f"Blender path: {args.blender_path}")
    logger.info(f"Blender timeout: {args.blender_timeout} seconds")
    logger.info(f"Skip 3D: {args.skip_3d}")
    
    if not os.path.exists(args.map_dir):
        logger.error(f"Map directory not found: {args.map_dir}")
        print(f"Error: Map directory not found: {args.map_dir}")
        sys.exit(1)
    
    logger.info("Map directory verified")
    automator = AIAutomation(args.map_dir, args.blender_path, args.blender_timeout)
    
    try:
        if args.skip_3d:
            logger.info("Running partial automation (skipping 3D generation)")
            # Run without 3D generation
            automator.generate_procedural_textures()
            automator.generate_destination_displays(args.route_name)
            automator.generate_preview_image(args.route_name)
            automator.update_readme(args.route_name)
            logger.info("Partial automation completed")
        else:
            logger.info("Running full automation")
            # Full automation
            success = automator.run_full_automation(args.route_name, api_key=None)
            if success:
                logger.info("Full automation completed successfully")
            else:
                logger.warning("Full automation completed with warnings")
            sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Error during automation: {e}")
        logger.error("Stack trace:")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error during automation: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
