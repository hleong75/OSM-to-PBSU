#!/usr/bin/env python3
"""
OSM Data Fetcher
Helper script to download OpenStreetMap data for bus routes

This script uses the Overpass API to download bus stops and road data
from OpenStreetMap for a specified area.
"""

import json
import sys
import argparse
import urllib.request
import urllib.parse


def fetch_osm_data(bbox: str, output_file: str = "osm_data.json"):
    """
    Fetch OSM data from Overpass API
    
    Args:
        bbox: Bounding box as "south,west,north,east" (latitude,longitude)
        output_file: Output file path
    """
    
    # Parse bounding box
    try:
        coords = [float(x.strip()) for x in bbox.split(',')]
        if len(coords) != 4:
            raise ValueError
        south, west, north, east = coords
    except (ValueError, IndexError):
        print("Error: Bounding box must be in format: south,west,north,east")
        print("Example: 40.7,74.0,40.8,74.1")
        sys.exit(1)
    
    # Build Overpass query
    overpass_query = f"""
    [out:json][timeout:60];
    (
      // Get all bus stops
      node["highway"="bus_stop"]({south},{west},{north},{east});
      node["public_transport"="platform"]({south},{west},{north},{east});
      node["public_transport"="stop_position"]({south},{west},{north},{east});
      
      // Get roads
      way["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential"]({south},{west},{north},{east});
      
      // Get bus routes
      relation["type"="route"]["route"="bus"]({south},{west},{north},{east});
    );
    out body;
    >;
    out skel qt;
    """
    
    # Overpass API endpoint
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    print(f"Fetching OSM data for bbox: {bbox}")
    print(f"This may take a moment...")
    
    try:
        # Encode query
        data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
        
        # Make request
        with urllib.request.urlopen(overpass_url, data=data, timeout=120) as response:
            osm_data = json.loads(response.read().decode('utf-8'))
        
        # Count elements
        elements = osm_data.get('elements', [])
        nodes = sum(1 for e in elements if e['type'] == 'node')
        ways = sum(1 for e in elements if e['type'] == 'way')
        relations = sum(1 for e in elements if e['type'] == 'relation')
        
        print(f"\nFetched {len(elements)} elements:")
        print(f"  - Nodes: {nodes}")
        print(f"  - Ways: {ways}")
        print(f"  - Relations: {relations}")
        
        # Count bus stops
        bus_stops = sum(1 for e in elements 
                       if e['type'] == 'node' and 
                       e.get('tags', {}).get('highway') == 'bus_stop' or
                       e.get('tags', {}).get('public_transport') in ['platform', 'stop_position'])
        print(f"  - Bus stops: {bus_stops}")
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(osm_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data saved to {output_file}")
        print(f"\nNext step:")
        print(f"  python osm_to_pbsu.py {output_file} -m YourMapName -r YourRouteName")
        
    except urllib.error.URLError as e:
        print(f"Error fetching data from Overpass API: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def fetch_by_relation_id(relation_id: int, output_file: str = "osm_data.json"):
    """
    Fetch OSM data for a specific bus route relation
    
    Args:
        relation_id: OSM relation ID for the bus route
        output_file: Output file path
    """
    
    overpass_query = f"""
    [out:json][timeout:60];
    (
      // Get the relation and all its members
      relation({relation_id});
      >;
      
      // Get nearby bus stops (within 100m of route)
      node(around:100)["highway"="bus_stop"];
      node(around:100)["public_transport"="platform"];
    );
    out body;
    >;
    out skel qt;
    """
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    print(f"Fetching OSM data for relation ID: {relation_id}")
    print(f"This may take a moment...")
    
    try:
        data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
        
        with urllib.request.urlopen(overpass_url, data=data, timeout=120) as response:
            osm_data = json.loads(response.read().decode('utf-8'))
        
        elements = osm_data.get('elements', [])
        print(f"\nFetched {len(elements)} elements")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(osm_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to {output_file}")
        print(f"\nNext step:")
        print(f"  python osm_to_pbsu.py {output_file} -m YourMapName -r YourRouteName")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch OpenStreetMap data for bus routes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch by bounding box (lat,lon format)
  python fetch_osm_data.py --bbox "40.7,-74.0,40.8,-73.9" -o route_data.json
  
  # Fetch a specific bus route by OSM relation ID
  python fetch_osm_data.py --relation 123456 -o route_data.json

How to find coordinates:
  1. Go to https://www.openstreetmap.org
  2. Navigate to your area of interest
  3. Click "Export" in the top menu
  4. The bounding box coordinates will be shown
  
How to find relation IDs:
  1. Search for a bus route on OpenStreetMap
  2. Click on the route
  3. The relation ID is shown in the left panel
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--bbox', type=str,
                      help='Bounding box as "south,west,north,east"')
    group.add_argument('--relation', type=int,
                      help='OSM relation ID for a bus route')
    
    parser.add_argument('-o', '--output', default='osm_data.json',
                       help='Output file (default: osm_data.json)')
    
    args = parser.parse_args()
    
    if args.bbox:
        fetch_osm_data(args.bbox, args.output)
    elif args.relation:
        fetch_by_relation_id(args.relation, args.output)


if __name__ == '__main__':
    main()
