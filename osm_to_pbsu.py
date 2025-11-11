#!/usr/bin/env python3
"""
OSM to PBSU Converter
Converts OpenStreetMap data to Proton Bus Simulator route format

This tool extracts bus routes, bus stops, and road networks from OpenStreetMap
and generates the necessary files for Proton Bus Simulator maps.
"""

import json
import math
import os
import sys
from typing import Dict, List, Tuple, Optional
import argparse


class OSMToPBSUConverter:
    """Converts OpenStreetMap data to PBSU route format"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.bus_stops = []
        self.route_ways = []
        self.buildings = []
        self.entrypoints = []
        
    def parse_osm_json(self, osm_data: Dict) -> None:
        """Parse OSM JSON data and extract relevant information"""
        elements = osm_data.get('elements', [])
        
        # First pass: collect nodes and ways
        nodes_dict = {}
        for element in elements:
            if element['type'] == 'node':
                nodes_dict[element['id']] = element
                
                # Check if it's a bus stop
                tags = element.get('tags', {})
                if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
                    self.bus_stops.append({
                        'id': element['id'],
                        'lat': element['lat'],
                        'lon': element['lon'],
                        'name': tags.get('name', f"Bus Stop {element['id']}"),
                        'tags': tags
                    })
        
        # Second pass: collect ways and relations
        for element in elements:
            if element['type'] == 'way':
                tags = element.get('tags', {})
                
                # Collect roads
                if tags.get('highway') in ['primary', 'secondary', 'tertiary', 'residential', 'trunk']:
                    way_nodes = []
                    for node_id in element.get('nodes', []):
                        if node_id in nodes_dict:
                            node = nodes_dict[node_id]
                            way_nodes.append({
                                'lat': node['lat'],
                                'lon': node['lon']
                            })
                    if way_nodes:
                        self.route_ways.append({
                            'id': element['id'],
                            'nodes': way_nodes,
                            'tags': tags
                        })
                
                # Collect buildings
                if tags.get('building'):
                    way_nodes = []
                    for node_id in element.get('nodes', []):
                        if node_id in nodes_dict:
                            node = nodes_dict[node_id]
                            way_nodes.append({
                                'lat': node['lat'],
                                'lon': node['lon']
                            })
                    if way_nodes:
                        # Extract height information
                        height = self._extract_building_height(tags)
                        self.buildings.append({
                            'id': element['id'],
                            'nodes': way_nodes,
                            'tags': tags,
                            'height': height
                        })
    
    def _extract_building_height(self, tags: Dict) -> float:
        """
        Extract building height from OSM tags
        
        Tries multiple sources:
        1. height tag (in meters)
        2. building:levels tag (floors * 3.5m average)
        3. building:height tag
        4. Default to 10m for generic buildings
        """
        # Direct height in meters
        if 'height' in tags:
            try:
                height_str = tags['height'].replace('m', '').replace('M', '').strip()
                return float(height_str)
            except (ValueError, AttributeError):
                pass
        
        # Building height tag
        if 'building:height' in tags:
            try:
                height_str = tags['building:height'].replace('m', '').replace('M', '').strip()
                return float(height_str)
            except (ValueError, AttributeError):
                pass
        
        # Number of levels (assume 3.5m per floor)
        if 'building:levels' in tags:
            try:
                levels = float(tags['building:levels'])
                return levels * 3.5
            except (ValueError, AttributeError):
                pass
        
        # Default heights based on building type
        building_type = tags.get('building', 'yes')
        default_heights = {
            'house': 7.0,
            'residential': 10.5,  # 3 floors
            'apartments': 21.0,   # 6 floors
            'commercial': 14.0,   # 4 floors
            'retail': 7.0,
            'industrial': 10.0,
            'warehouse': 8.0,
            'office': 35.0,       # 10 floors
            'hotel': 28.0,        # 8 floors
            'school': 10.5,
            'university': 14.0,
            'hospital': 21.0,
            'church': 15.0,
            'cathedral': 25.0,
        }
        
        return default_heights.get(building_type, 10.0)
    
    def fetch_elevation_data(self, locations: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
        """
        Fetch elevation data for a list of lat/lon coordinates
        Uses Open-Elevation API (free and open source)
        
        Args:
            locations: List of (latitude, longitude) tuples
        
        Returns:
            Dictionary mapping (lat, lon) to elevation in meters
        """
        if not locations:
            return {}
        
        elevations = {}
        
        try:
            import urllib.request
            import json
            
            # Open-Elevation API endpoint
            url = "https://api.open-elevation.com/api/v1/lookup"
            
            # Batch requests in groups of 100 (API limit)
            batch_size = 100
            for i in range(0, len(locations), batch_size):
                batch = locations[i:i+batch_size]
                
                # Format locations for API
                locations_data = [{"latitude": lat, "longitude": lon} for lat, lon in batch]
                data = json.dumps({"locations": locations_data}).encode('utf-8')
                
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        
                        for loc_data in result.get('results', []):
                            lat = loc_data['latitude']
                            lon = loc_data['longitude']
                            elevation = loc_data['elevation']
                            elevations[(lat, lon)] = elevation
                            
                except Exception as e:
                    print(f"Warning: Could not fetch elevation data for batch: {e}")
                    # Use default elevation of 0 for failed fetches
                    for lat, lon in batch:
                        elevations[(lat, lon)] = 0.0
        
        except ImportError:
            print("Warning: Could not import required modules for elevation data")
            for lat, lon in locations:
                elevations[(lat, lon)] = 0.0
        
        return elevations
    
    def lat_lon_to_unity_coords(self, lat: float, lon: float, 
                                origin_lat: float, origin_lon: float) -> Tuple[float, float, float]:
        """
        Convert latitude/longitude to Unity coordinates (meters)
        
        In Unity/PBSU:
        - X is east-west (east is positive)
        - Y is up-down (up is positive, typically 0 for ground level)
        - Z is north-south (north is positive)
        
        Note: Y and Z axes are swapped between Blender and Unity!
        """
        # Earth radius in meters
        earth_radius = 6371000
        
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        origin_lat_rad = math.radians(origin_lat)
        origin_lon_rad = math.radians(origin_lon)
        
        # Calculate differences
        dlat = lat_rad - origin_lat_rad
        dlon = lon_rad - origin_lon_rad
        
        # Convert to meters (approximate for small distances)
        x = dlon * earth_radius * math.cos(origin_lat_rad)  # East-West
        z = dlat * earth_radius  # North-South
        y = 0.0  # Ground level
        
        return (x, y, z)
    
    def calculate_rotation_y(self, lat1: float, lon1: float, 
                            lat2: float, lon2: float) -> float:
        """
        Calculate rotation around Y axis (heading) from point 1 to point 2
        Returns angle in degrees (0-360)
        """
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        # Calculate bearing
        angle_rad = math.atan2(dlon, dlat)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360
        angle_deg = (angle_deg + 360) % 360
        
        return angle_deg
    
    def generate_entrypoints_list(self) -> str:
        """Generate entrypoints_list.txt content"""
        lines = []
        for i, stop in enumerate(self.bus_stops, 1):
            # Clean name for internal use (no spaces or special chars)
            internal_name = stop['name'].replace(' ', '_').replace('-', '_')
            internal_name = ''.join(c for c in internal_name if c.isalnum() or c == '_')
            lines.append(f"{internal_name}")
        return '\n'.join(lines)
    
    def generate_entrypoints_txt(self, origin_lat: float, origin_lon: float) -> str:
        """Generate entrypoints.txt content with bus stop positions"""
        lines = []
        
        for i, stop in enumerate(self.bus_stops, 1):
            # Clean name for internal use
            internal_name = stop['name'].replace(' ', '_').replace('-', '_')
            internal_name = ''.join(c for c in internal_name if c.isalnum() or c == '_')
            
            # Convert to Unity coordinates
            x, y, z = self.lat_lon_to_unity_coords(
                stop['lat'], stop['lon'], origin_lat, origin_lon
            )
            
            # Calculate rotation (default facing north if we don't have direction info)
            rot_y = 0  # Default facing north
            
            lines.append(f"[entrypoint_{i}]")
            lines.append(f"name={internal_name}")
            lines.append(f"posX={x:.6f}")
            lines.append(f"posY={y:.6f}")
            lines.append(f"posZ={z:.6f}")
            lines.append(f"rotX=0")
            lines.append(f"rotY={rot_y}")
            lines.append(f"rotZ=0")
            lines.append("")
        
        return '\n'.join(lines)
    
    def generate_busstop_txt(self, stop: Dict, index: int, 
                            origin_lat: float, origin_lon: float) -> str:
        """Generate individual bus stop configuration file"""
        internal_name = stop['name'].replace(' ', '_').replace('-', '_')
        internal_name = ''.join(c for c in internal_name if c.isalnum() or c == '_')
        
        lines = [
            f"[busstop]",
            f"name={stop['name']}",
            f"side=right",  # Default to right side
            f"radius=1",
            f"paxAmount=5",  # Default 5 passengers
            f"",
            f"[from_3d]",
            f"readFrom3D=1",
            f"prefix={internal_name}",
            f"rotY=0",
            f""
        ]
        
        return '\n'.join(lines)
    
    def generate_map_txt(self, map_name: str, route_name: str) -> str:
        """Generate main .map.txt file"""
        lines = [
            f"[map]",
            f"baseDir={map_name}",
            f"modelsDir={route_name}",
            f"textures=textures",
            f"mapModVersion=2",
            f"preview=preview.png",
            f""
        ]
        return '\n'.join(lines)
    
    def create_directory_structure(self, map_name: str, route_name: str) -> None:
        """Create the PBSU directory structure"""
        base_dir = os.path.join(self.output_dir, map_name)
        tiles_dir = os.path.join(base_dir, 'tiles', route_name)
        textures_dir = os.path.join(base_dir, 'textures')
        dest_dir = os.path.join(base_dir, 'dest')
        busstops_dir = os.path.join(tiles_dir, 'aipeople', 'busstops')
        
        # Create directories
        os.makedirs(tiles_dir, exist_ok=True)
        os.makedirs(textures_dir, exist_ok=True)
        os.makedirs(dest_dir, exist_ok=True)
        os.makedirs(busstops_dir, exist_ok=True)
        
        return base_dir, tiles_dir, busstops_dir
    
    def convert(self, osm_file: str, map_name: str, route_name: str,
                origin_lat: Optional[float] = None, 
                origin_lon: Optional[float] = None) -> None:
        """Main conversion function"""
        
        print(f"Loading OSM data from {osm_file}...")
        with open(osm_file, 'r', encoding='utf-8') as f:
            osm_data = json.load(f)
        
        print("Parsing OSM data...")
        self.parse_osm_json(osm_data)
        
        print(f"Found {len(self.bus_stops)} bus stops")
        print(f"Found {len(self.route_ways)} road segments")
        print(f"Found {len(self.buildings)} buildings")
        
        # Count buildings with height data
        buildings_with_height = sum(1 for b in self.buildings if b.get('height', 0) > 0)
        print(f"  - {buildings_with_height} buildings have height information")
        
        if len(self.bus_stops) == 0:
            print("Warning: No bus stops found in OSM data!")
            return
        
        # Use first bus stop as origin if not specified
        if origin_lat is None or origin_lon is None:
            origin_lat = self.bus_stops[0]['lat']
            origin_lon = self.bus_stops[0]['lon']
            print(f"Using origin coordinates: {origin_lat}, {origin_lon}")
        
        print("Creating directory structure...")
        base_dir, tiles_dir, busstops_dir = self.create_directory_structure(
            map_name, route_name
        )
        
        print("Generating PBSU files...")
        
        # Generate main map file
        map_txt = self.generate_map_txt(map_name, route_name)
        map_file = os.path.join(self.output_dir, f"{map_name}.map.txt")
        with open(map_file, 'w', encoding='utf-8') as f:
            f.write(map_txt)
        print(f"Created {map_file}")
        
        # Generate entrypoints_list.txt
        entrypoints_list = self.generate_entrypoints_list()
        entrypoints_list_file = os.path.join(tiles_dir, 'entrypoints_list.txt')
        with open(entrypoints_list_file, 'w', encoding='utf-8') as f:
            f.write(entrypoints_list)
        print(f"Created {entrypoints_list_file}")
        
        # Generate entrypoints.txt
        entrypoints_txt = self.generate_entrypoints_txt(origin_lat, origin_lon)
        entrypoints_file = os.path.join(tiles_dir, 'entrypoints.txt')
        with open(entrypoints_file, 'w', encoding='utf-8') as f:
            f.write(entrypoints_txt)
        print(f"Created {entrypoints_file}")
        
        # Generate individual bus stop files
        for i, stop in enumerate(self.bus_stops, 1):
            busstop_txt = self.generate_busstop_txt(stop, i, origin_lat, origin_lon)
            internal_name = stop['name'].replace(' ', '_').replace('-', '_')
            internal_name = ''.join(c for c in internal_name if c.isalnum() or c == '_')
            busstop_file = os.path.join(busstops_dir, f"{internal_name}.txt")
            with open(busstop_file, 'w', encoding='utf-8') as f:
                f.write(busstop_txt)
        print(f"Created {len(self.bus_stops)} bus stop configuration files")
        
        # Fetch elevation data for bus stops and key points
        print("\nFetching elevation data...")
        locations = [(stop['lat'], stop['lon']) for stop in self.bus_stops]
        # Add some road points for terrain mapping
        for way in self.route_ways[:10]:  # Sample first 10 road segments
            for node in way['nodes'][::5]:  # Every 5th node
                locations.append((node['lat'], node['lon']))
        
        elevations = self.fetch_elevation_data(locations)
        print(f"Fetched elevation data for {len(elevations)} points")
        
        # Export geographic data (buildings, elevations) for 3D generation
        geographic_data = {
            'origin': {'lat': origin_lat, 'lon': origin_lon},
            'buildings': [],
            'elevations': {},
            'bus_stops': []
        }
        
        # Convert buildings to Unity coordinates with height
        for building in self.buildings:
            if not building['nodes']:
                continue
            
            # Calculate building center
            center_lat = sum(n['lat'] for n in building['nodes']) / len(building['nodes'])
            center_lon = sum(n['lon'] for n in building['nodes']) / len(building['nodes'])
            center_x, center_y, center_z = self.lat_lon_to_unity_coords(
                center_lat, center_lon, origin_lat, origin_lon
            )
            
            # Convert footprint nodes
            footprint = []
            for node in building['nodes']:
                x, y, z = self.lat_lon_to_unity_coords(
                    node['lat'], node['lon'], origin_lat, origin_lon
                )
                footprint.append({'x': x, 'y': y, 'z': z})
            
            geographic_data['buildings'].append({
                'center': {'x': center_x, 'y': center_y, 'z': center_z},
                'footprint': footprint,
                'height': building['height'],
                'type': building['tags'].get('building', 'yes'),
                'name': building['tags'].get('name', '')
            })
        
        # Add elevation data
        for (lat, lon), elevation in elevations.items():
            x, y, z = self.lat_lon_to_unity_coords(lat, lon, origin_lat, origin_lon)
            geographic_data['elevations'][f"{lat},{lon}"] = {
                'x': x, 'y': elevation, 'z': z, 'elevation': elevation
            }
        
        # Add bus stop data with positions
        for stop in self.bus_stops:
            x, y, z = self.lat_lon_to_unity_coords(
                stop['lat'], stop['lon'], origin_lat, origin_lon
            )
            internal_name = stop['name'].replace(' ', '_').replace('-', '_')
            internal_name = ''.join(c for c in internal_name if c.isalnum() or c == '_')
            geographic_data['bus_stops'].append({
                'name': stop['name'],
                'internal_name': internal_name,
                'position': {'x': x, 'y': y, 'z': z},
                'lat': stop['lat'],
                'lon': stop['lon']
            })
        
        # Save geographic data
        geo_data_file = os.path.join(base_dir, 'geographic_data.json')
        with open(geo_data_file, 'w', encoding='utf-8') as f:
            json.dump(geographic_data, f, indent=2)
        print(f"Created {geo_data_file}")
        print(f"  - Exported {len(geographic_data['buildings'])} buildings with heights")
        print(f"  - Exported {len(geographic_data['elevations'])} elevation points")
        
        # Create README with instructions
        readme_content = f"""# PBSU Route: {map_name} - {route_name}

## Generated from OpenStreetMap Data

This route was automatically generated from OpenStreetMap data using osm_to_pbsu.py

### Statistics:
- Bus stops: {len(self.bus_stops)}
- Road segments: {len(self.route_ways)}
- Buildings: {len(self.buildings)} ({buildings_with_height} with height data)
- Elevation points: {len(elevations)}
- Origin coordinates: {origin_lat}, {origin_lon}

### Next Steps:

1. **Create 3D Models in Blender 2.79:**
   - Model the road network and buildings
   - Place bus stop objects at the coordinates specified in entrypoints.txt
   - Each bus stop needs:
     - A trigger object named `{{stopname}}_trigger`
     - Passenger spawn points named `{{stopname}}.000`, `{{stopname}}.001`, etc.
   - Export to .3ds format and place in tiles/{route_name}/

2. **Add Textures:**
   - Place texture files in {map_name}/textures/

3. **Configure Destinations:**
   - Create destination folders in {map_name}/dest/
   - Add destination display images

4. **Create Preview Image:**
   - Add preview.png (640x360px recommended) in {map_name}/

5. **Test in Proton Bus Simulator:**
   - Copy the {map_name}/ folder to your PBSU mods/maps/ directory
   - Copy {map_name}.map.txt to mods/maps/
   - Launch PBSU and select the map

### Bus Stops:
"""
        for i, stop in enumerate(self.bus_stops, 1):
            x, y, z = self.lat_lon_to_unity_coords(
                stop['lat'], stop['lon'], origin_lat, origin_lon
            )
            readme_content += f"\n{i}. {stop['name']} - Position: ({x:.2f}, {y:.2f}, {z:.2f})"
        
        readme_file = os.path.join(base_dir, 'README.md')
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Created {readme_file}")
        
        print(f"\n✓ Conversion complete!")
        print(f"Output directory: {base_dir}")
        print(f"\n{'='*60}")
        print("Next Steps:")
        print(f"{'='*60}")
        print("\n1. Run post-conversion automation:")
        print(f"   python automate_post_conversion.py {base_dir}")
        print("\n2. (OPTIONAL) Run AI-powered automation for complete generation:")
        print(f"   python ai_automation.py {base_dir} {route_name}")
        print("\n   This will automatically:")
        print("   - Generate 3D models using Blender")
        print("   - Create procedural textures")
        print("   - Generate destination displays")
        print("   - Create preview image")
        print(f"\n3. OR manually create 3D models in Blender 2.79")
        print(f"   See {readme_file} for detailed instructions")


def main():
    parser = argparse.ArgumentParser(
        description='Convert OpenStreetMap data to Proton Bus Simulator route format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert OSM JSON file to PBSU route
  python osm_to_pbsu.py route_data.json -m "My City" -r "Route 101"
  
  # Specify custom origin coordinates
  python osm_to_pbsu.py route_data.json -m "My City" -r "Route 101" --origin-lat 40.7128 --origin-lon -74.0060
  
  # Custom output directory
  python osm_to_pbsu.py route_data.json -m "My City" -r "Route 101" -o ./my_maps

Note: Input file should be OSM JSON format (from Overpass API or exported from JOSM)
        """
    )
    
    parser.add_argument('input_file', help='Input OSM JSON file')
    parser.add_argument('-m', '--map-name', required=True, 
                       help='Name of the map (avoid special characters)')
    parser.add_argument('-r', '--route-name', required=True,
                       help='Name of the route (avoid special characters)')
    parser.add_argument('-o', '--output', default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--origin-lat', type=float,
                       help='Origin latitude (default: first bus stop)')
    parser.add_argument('--origin-lon', type=float,
                       help='Origin longitude (default: first bus stop)')
    parser.add_argument('--run-ai-automation', action='store_true',
                       help='Automatically run AI automation after conversion')
    parser.add_argument('--blender-path', default='blender',
                       help='Path to Blender executable for AI automation')
    parser.add_argument('--streetview-api-key', default=None,
                       help='Google Street View Static API key for realistic textures')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    converter = OSMToPBSUConverter(output_dir=args.output)
    
    try:
        converter.convert(
            args.input_file,
            args.map_name,
            args.route_name,
            args.origin_lat,
            args.origin_lon
        )
        
        # Run AI automation if requested
        if args.run_ai_automation:
            print("\n" + "="*60)
            print("Running AI Automation...")
            print("="*60 + "\n")
            
            map_dir = os.path.join(args.output, args.map_name)
            
            # Import and run AI automation
            try:
                # First run post-conversion setup
                from automate_post_conversion import PostConversionAutomator
                post_automator = PostConversionAutomator(map_dir)
                post_automator.run_all(enable_ai=False)
                
                # Then run AI automation
                from ai_automation import AIAutomation
                ai_automator = AIAutomation(map_dir, args.blender_path)
                ai_automator.run_full_automation(args.route_name, args.streetview_api_key)
                
            except ImportError as e:
                print(f"Error: Could not import automation modules: {e}")
                print("Make sure ai_automation.py and automate_post_conversion.py are in the same directory")
            except Exception as e:
                print(f"Error during AI automation: {e}")
                import traceback
                traceback.print_exc()
                print("\nYou can manually run automation later with:")
                print(f"  python ai_automation.py {map_dir} {args.route_name}")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
