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
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('osm_to_pbsu.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OSMToPBSUConverter:
    """Converts OpenStreetMap data to PBSU route format"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.bus_stops = []
        self.route_ways = []
        self.buildings = []
        self.entrypoints = []
        logger.info(f"Initialized OSMToPBSUConverter with output directory: {output_dir}")
        
    def parse_osm_json(self, osm_data: Dict) -> None:
        """Parse OSM JSON data and extract relevant information"""
        logger.info("Starting to parse OSM JSON data")
        elements = osm_data.get('elements', [])
        logger.info(f"Found {len(elements)} elements in OSM data")
        
        # First pass: collect nodes and ways
        nodes_dict = {}
        for element in elements:
            if element['type'] == 'node':
                nodes_dict[element['id']] = element
                
                # Check if it's a bus stop
                tags = element.get('tags', {})
                if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
                    bus_stop_data = {
                        'id': element['id'],
                        'lat': element['lat'],
                        'lon': element['lon'],
                        'name': tags.get('name', f"Bus Stop {element['id']}"),
                        'tags': tags
                    }
                    self.bus_stops.append(bus_stop_data)
                    logger.debug(f"Found bus stop: {bus_stop_data['name']} at ({element['lat']}, {element['lon']})")
        
        logger.info(f"First pass complete: {len(nodes_dict)} nodes, {len(self.bus_stops)} bus stops found")
        
        # Second pass: collect ways and relations
        logger.info("Starting second pass: collecting ways and relations")
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
                        road_name = tags.get('name', f'Way {element["id"]}')
                        logger.debug(f"Found road: {road_name} with {len(way_nodes)} nodes")
                
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
                        building_data = {
                            'id': element['id'],
                            'nodes': way_nodes,
                            'tags': tags,
                            'height': height
                        }
                        self.buildings.append(building_data)
                        logger.debug(f"Found building: height={height}m, nodes={len(way_nodes)}, type={tags.get('building', 'yes')}")
        
        logger.info(f"Second pass complete: {len(self.route_ways)} road segments, {len(self.buildings)} buildings found")
    
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
        
        NOTE: API calls have been removed. This function now returns default elevation of 0.
        For accurate elevation data, use LiDAR HD data files (see load_lidar_elevation).
        
        Args:
            locations: List of (latitude, longitude) tuples
        
        Returns:
            Dictionary mapping (lat, lon) to elevation in meters (default: 0)
        """
        logger.info(f"Elevation data requested for {len(locations)} locations")
        logger.info("API calls disabled - using default elevation of 0m")
        logger.info("For accurate elevation, provide LiDAR HD data file")
        
        elevations = {}
        for lat, lon in locations:
            elevations[(lat, lon)] = 0.0
        
        return elevations
    
    def load_lidar_elevation(self, lidar_file: str, locations: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
        """
        Load elevation data from LiDAR HD file (French government high-resolution data)
        
        Supports common formats:
        - GeoTIFF (.tif, .tiff)
        - XYZ ASCII (.xyz, .txt)
        - LAS/LAZ point clouds (.las, .laz)
        
        Args:
            lidar_file: Path to LiDAR HD elevation data file
            locations: List of (latitude, longitude) tuples
        
        Returns:
            Dictionary mapping (lat, lon) to elevation in meters
        """
        logger.info(f"Loading LiDAR HD elevation data from: {lidar_file}")
        
        if not os.path.exists(lidar_file):
            logger.error(f"LiDAR file not found: {lidar_file}")
            return {loc: 0.0 for loc in locations}
        
        elevations = {}
        file_ext = os.path.splitext(lidar_file)[1].lower()
        
        try:
            if file_ext in ['.tif', '.tiff']:
                # Try to load GeoTIFF using rasterio (optional dependency)
                try:
                    import rasterio
                    from rasterio.transform import rowcol
                    
                    logger.info("Loading GeoTIFF file with rasterio")
                    with rasterio.open(lidar_file) as dataset:
                        for lat, lon in locations:
                            try:
                                # Transform lat/lon to pixel coordinates
                                row, col = rowcol(dataset.transform, lon, lat)
                                # Read elevation value
                                elevation = dataset.read(1)[row, col]
                                elevations[(lat, lon)] = float(elevation)
                                logger.debug(f"Elevation at ({lat}, {lon}): {elevation}m")
                            except Exception as e:
                                logger.warning(f"Could not read elevation for ({lat}, {lon}): {e}")
                                elevations[(lat, lon)] = 0.0
                    
                    logger.info(f"Successfully loaded {len(elevations)} elevation values from GeoTIFF")
                    
                except ImportError:
                    logger.error("rasterio not installed. Install with: pip install rasterio")
                    logger.info("Falling back to default elevation")
                    elevations = {loc: 0.0 for loc in locations}
                    
            elif file_ext in ['.xyz', '.txt']:
                # Load XYZ ASCII format
                logger.info("Loading XYZ ASCII file")
                xyz_data = []
                with open(lidar_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            try:
                                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                                xyz_data.append((x, y, z))
                            except ValueError:
                                continue
                
                logger.info(f"Loaded {len(xyz_data)} points from XYZ file")
                
                # Simple nearest neighbor interpolation
                for lat, lon in locations:
                    min_dist = float('inf')
                    nearest_z = 0.0
                    for x, y, z in xyz_data[:10000]:  # Limit search for performance
                        dist = math.sqrt((x - lon)**2 + (y - lat)**2)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_z = z
                    elevations[(lat, lon)] = nearest_z
                    logger.debug(f"Elevation at ({lat}, {lon}): {nearest_z}m (dist: {min_dist:.6f})")
                
                logger.info(f"Interpolated {len(elevations)} elevation values from XYZ data")
                
            elif file_ext in ['.las', '.laz']:
                # Try to load LAS/LAZ using laspy (optional dependency)
                try:
                    import laspy
                    
                    logger.info("Loading LAS/LAZ file with laspy")
                    las = laspy.read(lidar_file)
                    points = [(p.X, p.Y, p.Z) for p in las.points[:100000]]  # Limit for performance
                    
                    logger.info(f"Loaded {len(points)} points from LAS file")
                    
                    # Simple nearest neighbor interpolation
                    for lat, lon in locations:
                        min_dist = float('inf')
                        nearest_z = 0.0
                        for x, y, z in points:
                            dist = math.sqrt((x - lon)**2 + (y - lat)**2)
                            if dist < min_dist:
                                min_dist = dist
                                nearest_z = z
                        elevations[(lat, lon)] = nearest_z
                        logger.debug(f"Elevation at ({lat}, {lon}): {nearest_z}m")
                    
                    logger.info(f"Interpolated {len(elevations)} elevation values from LAS data")
                    
                except ImportError:
                    logger.error("laspy not installed. Install with: pip install laspy")
                    logger.info("Falling back to default elevation")
                    elevations = {loc: 0.0 for loc in locations}
            else:
                logger.error(f"Unsupported LiDAR file format: {file_ext}")
                logger.info("Supported formats: .tif, .tiff, .xyz, .txt, .las, .laz")
                elevations = {loc: 0.0 for loc in locations}
                
        except Exception as e:
            logger.error(f"Error loading LiDAR data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            elevations = {loc: 0.0 for loc in locations}
        
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
                origin_lon: Optional[float] = None,
                lidar_file: Optional[str] = None) -> None:
        """Main conversion function"""
        
        logger.info("="*60)
        logger.info("Starting OSM to PBSU Conversion")
        logger.info("="*60)
        logger.info(f"OSM file: {osm_file}")
        logger.info(f"Map name: {map_name}")
        logger.info(f"Route name: {route_name}")
        
        print(f"Loading OSM data from {osm_file}...")
        logger.info(f"Loading OSM data from {osm_file}...")
        try:
            with open(osm_file, 'r', encoding='utf-8') as f:
                osm_data = json.load(f)
            logger.info("Successfully loaded OSM JSON data")
        except Exception as e:
            logger.error(f"Failed to load OSM file: {e}")
            raise
        
        print("Parsing OSM data...")
        logger.info("Parsing OSM data...")
        try:
            self.parse_osm_json(osm_data)
        except Exception as e:
            logger.error(f"Failed to parse OSM data: {e}")
            raise
        
        print(f"Found {len(self.bus_stops)} bus stops")
        print(f"Found {len(self.route_ways)} road segments")
        print(f"Found {len(self.buildings)} buildings")
        
        logger.info(f"Parsing complete:")
        logger.info(f"  - Bus stops: {len(self.bus_stops)}")
        logger.info(f"  - Road segments: {len(self.route_ways)}")
        logger.info(f"  - Buildings: {len(self.buildings)}")
        
        # Count buildings with height data
        buildings_with_height = sum(1 for b in self.buildings if b.get('height', 0) > 0)
        print(f"  - {buildings_with_height} buildings have height information")
        logger.info(f"  - Buildings with height data: {buildings_with_height}")
        
        if len(self.bus_stops) == 0:
            logger.error("No bus stops found in OSM data!")
            print("Warning: No bus stops found in OSM data!")
            return
        
        # Use first bus stop as origin if not specified
        if origin_lat is None or origin_lon is None:
            origin_lat = self.bus_stops[0]['lat']
            origin_lon = self.bus_stops[0]['lon']
            print(f"Using origin coordinates: {origin_lat}, {origin_lon}")
            logger.info(f"Using first bus stop as origin: ({origin_lat}, {origin_lon})")
        else:
            logger.info(f"Using provided origin coordinates: ({origin_lat}, {origin_lon})")
        
        print("Creating directory structure...")
        logger.info("Creating directory structure...")
        try:
            base_dir, tiles_dir, busstops_dir = self.create_directory_structure(
                map_name, route_name
            )
            logger.info(f"Created directories:")
            logger.info(f"  - Base: {base_dir}")
            logger.info(f"  - Tiles: {tiles_dir}")
            logger.info(f"  - Bus stops: {busstops_dir}")
        except Exception as e:
            logger.error(f"Failed to create directory structure: {e}")
            raise
        
        print("Generating PBSU files...")
        logger.info("Generating PBSU files...")
        
        # Generate main map file
        try:
            map_txt = self.generate_map_txt(map_name, route_name)
            map_file = os.path.join(self.output_dir, f"{map_name}.map.txt")
            with open(map_file, 'w', encoding='utf-8') as f:
                f.write(map_txt)
            print(f"Created {map_file}")
            logger.info(f"Created main map file: {map_file}")
        except Exception as e:
            logger.error(f"Failed to generate map file: {e}")
            raise
        
        # Generate entrypoints_list.txt
        try:
            entrypoints_list = self.generate_entrypoints_list()
            entrypoints_list_file = os.path.join(tiles_dir, 'entrypoints_list.txt')
            with open(entrypoints_list_file, 'w', encoding='utf-8') as f:
                f.write(entrypoints_list)
            print(f"Created {entrypoints_list_file}")
            logger.info(f"Created entrypoints list: {entrypoints_list_file}")
        except Exception as e:
            logger.error(f"Failed to generate entrypoints list: {e}")
            raise
        
        # Generate entrypoints.txt
        try:
            entrypoints_txt = self.generate_entrypoints_txt(origin_lat, origin_lon)
            entrypoints_file = os.path.join(tiles_dir, 'entrypoints.txt')
            with open(entrypoints_file, 'w', encoding='utf-8') as f:
                f.write(entrypoints_txt)
            print(f"Created {entrypoints_file}")
            logger.info(f"Created entrypoints file: {entrypoints_file}")
        except Exception as e:
            logger.error(f"Failed to generate entrypoints: {e}")
            raise
        
        # Generate individual bus stop files
        try:
            for i, stop in enumerate(self.bus_stops, 1):
                busstop_txt = self.generate_busstop_txt(stop, i, origin_lat, origin_lon)
                internal_name = stop['name'].replace(' ', '_').replace('-', '_')
                internal_name = ''.join(c for c in internal_name if c.isalnum() or c == '_')
                busstop_file = os.path.join(busstops_dir, f"{internal_name}.txt")
                with open(busstop_file, 'w', encoding='utf-8') as f:
                    f.write(busstop_txt)
            print(f"Created {len(self.bus_stops)} bus stop configuration files")
            logger.info(f"Created {len(self.bus_stops)} bus stop configuration files")
        except Exception as e:
            logger.error(f"Failed to generate bus stop files: {e}")
            raise
        
        # Fetch elevation data for bus stops and key points
        print("\nFetching elevation data...")
        logger.info("Fetching elevation data...")
        locations = [(stop['lat'], stop['lon']) for stop in self.bus_stops]
        # Add some road points for terrain mapping
        for way in self.route_ways[:10]:  # Sample first 10 road segments
            for node in way['nodes'][::5]:  # Every 5th node
                locations.append((node['lat'], node['lon']))
        
        logger.info(f"Prepared {len(locations)} locations for elevation lookup")
        
        # Use LiDAR HD if available, otherwise use default values
        if lidar_file and os.path.exists(lidar_file):
            logger.info(f"Using LiDAR HD file for elevation: {lidar_file}")
            print(f"Loading LiDAR HD data from: {lidar_file}")
            elevations = self.load_lidar_elevation(lidar_file, locations)
        else:
            if lidar_file:
                logger.warning(f"LiDAR file not found: {lidar_file}, using default elevation")
            else:
                logger.info("No LiDAR file provided, using default elevation of 0m")
            elevations = self.fetch_elevation_data(locations)
        
        print(f"Fetched elevation data for {len(elevations)} points")
        logger.info(f"Elevation data ready for {len(elevations)} points")
        
        # Export geographic data (buildings, elevations) for 3D generation
        logger.info("Exporting geographic data...")
        geographic_data = {
            'origin': {'lat': origin_lat, 'lon': origin_lon},
            'buildings': [],
            'elevations': {},
            'bus_stops': []
        }
        
        # Convert buildings to Unity coordinates with height
        logger.info("Converting building data to Unity coordinates...")
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
        
        logger.info(f"Converted {len(geographic_data['buildings'])} buildings")
        
        # Add elevation data
        logger.info("Adding elevation data to geographic export...")
        for (lat, lon), elevation in elevations.items():
            x, y, z = self.lat_lon_to_unity_coords(lat, lon, origin_lat, origin_lon)
            geographic_data['elevations'][f"{lat},{lon}"] = {
                'x': x, 'y': elevation, 'z': z, 'elevation': elevation
            }
        
        logger.info(f"Added {len(geographic_data['elevations'])} elevation points")
        
        # Add bus stop data with positions
        logger.info("Adding bus stop data to geographic export...")
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
        
        logger.info(f"Added {len(geographic_data['bus_stops'])} bus stops")
        
        # Save geographic data
        try:
            geo_data_file = os.path.join(base_dir, 'geographic_data.json')
            with open(geo_data_file, 'w', encoding='utf-8') as f:
                json.dump(geographic_data, f, indent=2)
            print(f"Created {geo_data_file}")
            print(f"  - Exported {len(geographic_data['buildings'])} buildings with heights")
            print(f"  - Exported {len(geographic_data['elevations'])} elevation points")
            logger.info(f"Successfully saved geographic data to {geo_data_file}")
        except Exception as e:
            logger.error(f"Failed to save geographic data: {e}")
            raise
        
        # Create README with instructions
        logger.info("Creating README file...")
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
        
        try:
            readme_file = os.path.join(base_dir, 'README.md')
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"Created {readme_file}")
            logger.info(f"Created README file: {readme_file}")
        except Exception as e:
            logger.error(f"Failed to create README: {e}")
            raise
        
        print(f"\n✓ Conversion complete!")
        print(f"Output directory: {base_dir}")
        logger.info("="*60)
        logger.info("OSM to PBSU Conversion Complete!")
        logger.info(f"Output directory: {base_dir}")
        logger.info("="*60)
        
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
  
  # Use LiDAR HD data for accurate elevation
  python osm_to_pbsu.py route_data.json -m "My City" -r "Route 101" --lidar-file elevation.tif
  
  # Custom output directory
  python osm_to_pbsu.py route_data.json -m "My City" -r "Route 101" -o ./my_maps

Note: Input file should be OSM JSON format (from Overpass API or exported from JOSM)
      LiDAR HD files can be obtained from French government data portal (geoservices.ign.fr)
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
    parser.add_argument('--lidar-file', default=None,
                       help='LiDAR HD elevation data file (.tif, .xyz, .las, .laz)')
    parser.add_argument('--run-ai-automation', action='store_true',
                       help='Automatically run AI automation after conversion')
    parser.add_argument('--blender-path', default='blender',
                       help='Path to Blender executable for AI automation')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    if args.lidar_file and not os.path.exists(args.lidar_file):
        logger.warning(f"LiDAR file not found: {args.lidar_file}, will use default elevation")
        print(f"Warning: LiDAR file '{args.lidar_file}' not found, using default elevation")
    
    converter = OSMToPBSUConverter(output_dir=args.output)
    
    try:
        converter.convert(
            args.input_file,
            args.map_name,
            args.route_name,
            args.origin_lat,
            args.origin_lon,
            args.lidar_file
        )
        
        # Run AI automation if requested
        if args.run_ai_automation:
            logger.info("AI automation requested")
            print("\n" + "="*60)
            print("Running AI Automation...")
            print("="*60 + "\n")
            
            map_dir = os.path.join(args.output, args.map_name)
            
            # Import and run AI automation
            try:
                logger.info("Starting post-conversion automation...")
                # First run post-conversion setup
                from automate_post_conversion import PostConversionAutomator
                post_automator = PostConversionAutomator(map_dir)
                post_automator.run_all(enable_ai=False)
                
                logger.info("Starting AI automation...")
                # Then run AI automation (without streetview API key)
                from ai_automation import AIAutomation
                ai_automator = AIAutomation(map_dir, args.blender_path)
                ai_automator.run_full_automation(args.route_name, api_key=None)
                
                logger.info("AI automation completed successfully")
                
            except ImportError as e:
                logger.error(f"Could not import automation modules: {e}")
                print(f"Error: Could not import automation modules: {e}")
                print("Make sure ai_automation.py and automate_post_conversion.py are in the same directory")
            except Exception as e:
                logger.error(f"Error during AI automation: {e}")
                print(f"Error during AI automation: {e}")
                import traceback
                traceback.print_exc()
                print("\nYou can manually run automation later with:")
                print(f"  python ai_automation.py {map_dir} {args.route_name}")
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
