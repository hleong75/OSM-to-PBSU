#!/usr/bin/env python3
"""
Comprehensive tests for OSM to PBSU Converter

Tests cover:
- OSM data parsing
- Coordinate conversion
- File generation
- LiDAR elevation data loading
- Error handling
"""

import unittest
import tempfile
import os
import json
import shutil
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from osm_to_pbsu import OSMToPBSUConverter


class TestOSMParsing(unittest.TestCase):
    """Test OSM data parsing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = OSMToPBSUConverter(output_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_parse_bus_stops(self):
        """Test parsing bus stops from OSM data"""
        osm_data = {
            'elements': [
                {
                    'type': 'node',
                    'id': 1001,
                    'lat': 48.8566,
                    'lon': 2.3522,
                    'tags': {
                        'highway': 'bus_stop',
                        'name': 'Test Stop 1'
                    }
                },
                {
                    'type': 'node',
                    'id': 1002,
                    'lat': 48.8567,
                    'lon': 2.3523,
                    'tags': {
                        'public_transport': 'platform',
                        'name': 'Test Stop 2'
                    }
                }
            ]
        }
        
        self.converter.parse_osm_json(osm_data)
        
        self.assertEqual(len(self.converter.bus_stops), 2)
        self.assertEqual(self.converter.bus_stops[0]['name'], 'Test Stop 1')
        self.assertEqual(self.converter.bus_stops[1]['name'], 'Test Stop 2')
        
    def test_parse_roads(self):
        """Test parsing roads from OSM data"""
        osm_data = {
            'elements': [
                {
                    'type': 'node',
                    'id': 2001,
                    'lat': 48.8566,
                    'lon': 2.3522
                },
                {
                    'type': 'node',
                    'id': 2002,
                    'lat': 48.8567,
                    'lon': 2.3523
                },
                {
                    'type': 'way',
                    'id': 3001,
                    'nodes': [2001, 2002],
                    'tags': {
                        'highway': 'primary',
                        'name': 'Test Road'
                    }
                }
            ]
        }
        
        self.converter.parse_osm_json(osm_data)
        
        self.assertEqual(len(self.converter.route_ways), 1)
        self.assertEqual(len(self.converter.route_ways[0]['nodes']), 2)
        
    def test_parse_buildings(self):
        """Test parsing buildings from OSM data"""
        osm_data = {
            'elements': [
                {
                    'type': 'node',
                    'id': 4001,
                    'lat': 48.8566,
                    'lon': 2.3522
                },
                {
                    'type': 'node',
                    'id': 4002,
                    'lat': 48.8567,
                    'lon': 2.3523
                },
                {
                    'type': 'way',
                    'id': 5001,
                    'nodes': [4001, 4002, 4001],
                    'tags': {
                        'building': 'yes',
                        'building:levels': '3'
                    }
                }
            ]
        }
        
        self.converter.parse_osm_json(osm_data)
        
        self.assertEqual(len(self.converter.buildings), 1)
        self.assertEqual(self.converter.buildings[0]['height'], 10.5)  # 3 levels * 3.5m


class TestBuildingHeightExtraction(unittest.TestCase):
    """Test building height extraction from OSM tags"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = OSMToPBSUConverter()
        
    def test_extract_height_from_tag(self):
        """Test extracting height from height tag"""
        tags = {'height': '15m'}
        height = self.converter._extract_building_height(tags)
        self.assertEqual(height, 15.0)
        
    def test_extract_height_from_levels(self):
        """Test extracting height from building:levels tag"""
        tags = {'building:levels': '4'}
        height = self.converter._extract_building_height(tags)
        self.assertEqual(height, 14.0)  # 4 * 3.5m
        
    def test_extract_height_from_building_height(self):
        """Test extracting height from building:height tag"""
        tags = {'building:height': '20'}
        height = self.converter._extract_building_height(tags)
        self.assertEqual(height, 20.0)
        
    def test_default_height_by_type(self):
        """Test default height assignment by building type"""
        test_cases = [
            ({'building': 'house'}, 7.0),
            ({'building': 'apartments'}, 21.0),
            ({'building': 'office'}, 35.0),
            ({'building': 'yes'}, 10.0),  # default
        ]
        
        for tags, expected_height in test_cases:
            with self.subTest(tags=tags):
                height = self.converter._extract_building_height(tags)
                self.assertEqual(height, expected_height)


class TestCoordinateConversion(unittest.TestCase):
    """Test coordinate conversion functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = OSMToPBSUConverter()
        
    def test_lat_lon_to_unity_coords(self):
        """Test conversion from lat/lon to Unity coordinates"""
        # Test with Paris coordinates
        origin_lat, origin_lon = 48.8566, 2.3522
        test_lat, test_lon = 48.8567, 2.3523
        
        x, y, z = self.converter.lat_lon_to_unity_coords(
            test_lat, test_lon, origin_lat, origin_lon
        )
        
        # Check that x, z are reasonable distances (roughly 111m per degree)
        self.assertGreater(x, 0)  # East is positive
        self.assertGreater(z, 0)  # North is positive
        self.assertEqual(y, 0.0)  # Ground level
        
    def test_zero_offset(self):
        """Test that same coordinates give zero offset"""
        origin_lat, origin_lon = 48.8566, 2.3522
        
        x, y, z = self.converter.lat_lon_to_unity_coords(
            origin_lat, origin_lon, origin_lat, origin_lon
        )
        
        self.assertAlmostEqual(x, 0.0, places=5)
        self.assertAlmostEqual(y, 0.0, places=5)
        self.assertAlmostEqual(z, 0.0, places=5)


class TestFileGeneration(unittest.TestCase):
    """Test file generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = OSMToPBSUConverter(output_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_map_txt(self):
        """Test generation of main map file"""
        content = self.converter.generate_map_txt("TestMap", "TestRoute")
        
        self.assertIn("[map]", content)
        self.assertIn("baseDir=TestMap", content)
        self.assertIn("modelsDir=TestRoute", content)
        self.assertIn("mapModVersion=2", content)
        
    def test_generate_entrypoints_list(self):
        """Test generation of entrypoints list"""
        self.converter.bus_stops = [
            {'name': 'Stop One', 'lat': 48.0, 'lon': 2.0, 'tags': {}},
            {'name': 'Stop Two', 'lat': 48.1, 'lon': 2.1, 'tags': {}}
        ]
        
        content = self.converter.generate_entrypoints_list()
        
        self.assertIn("Stop_One", content)
        self.assertIn("Stop_Two", content)
        
    def test_generate_busstop_txt(self):
        """Test generation of bus stop configuration"""
        stop = {
            'name': 'Test Stop',
            'lat': 48.8566,
            'lon': 2.3522,
            'tags': {}
        }
        
        content = self.converter.generate_busstop_txt(stop, 1, 48.8566, 2.3522)
        
        self.assertIn("[busstop]", content)
        self.assertIn("name=Test Stop", content)
        self.assertIn("[from_3d]", content)
        self.assertIn("readFrom3D=1", content)


class TestDirectoryStructure(unittest.TestCase):
    """Test directory structure creation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = OSMToPBSUConverter(output_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_directory_structure(self):
        """Test creation of PBSU directory structure"""
        base_dir, tiles_dir, busstops_dir = self.converter.create_directory_structure(
            "TestMap", "TestRoute"
        )
        
        self.assertTrue(os.path.exists(base_dir))
        self.assertTrue(os.path.exists(tiles_dir))
        self.assertTrue(os.path.exists(busstops_dir))
        self.assertTrue(os.path.exists(os.path.join(base_dir, 'textures')))
        self.assertTrue(os.path.exists(os.path.join(base_dir, 'dest')))


class TestElevationData(unittest.TestCase):
    """Test elevation data functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = OSMToPBSUConverter()
        
    def test_fetch_elevation_data_returns_zero(self):
        """Test that fetch_elevation_data returns zero (API calls disabled)"""
        locations = [(48.8566, 2.3522), (48.8567, 2.3523)]
        
        elevations = self.converter.fetch_elevation_data(locations)
        
        self.assertEqual(len(elevations), 2)
        for elevation in elevations.values():
            self.assertEqual(elevation, 0.0)
            
    def test_load_lidar_elevation_nonexistent_file(self):
        """Test loading LiDAR data from non-existent file"""
        locations = [(48.8566, 2.3522)]
        
        elevations = self.converter.load_lidar_elevation('/nonexistent/file.tif', locations)
        
        # Should return default values
        self.assertEqual(len(elevations), 1)
        self.assertEqual(elevations[locations[0]], 0.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for full conversion process"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_osm_file = os.path.join(self.temp_dir, 'test_route.json')
        
        # Create test OSM data
        osm_data = {
            'version': 0.6,
            'elements': [
                {
                    'type': 'node',
                    'id': 1001,
                    'lat': 48.8566,
                    'lon': 2.3522,
                    'tags': {
                        'highway': 'bus_stop',
                        'name': 'Central Station'
                    }
                },
                {
                    'type': 'node',
                    'id': 1002,
                    'lat': 48.8567,
                    'lon': 2.3523,
                    'tags': {
                        'highway': 'bus_stop',
                        'name': 'Main Street'
                    }
                },
                {
                    'type': 'node',
                    'id': 2001,
                    'lat': 48.8566,
                    'lon': 2.3522
                },
                {
                    'type': 'node',
                    'id': 2002,
                    'lat': 48.8567,
                    'lon': 2.3523
                },
                {
                    'type': 'way',
                    'id': 3001,
                    'nodes': [2001, 2002],
                    'tags': {
                        'highway': 'primary',
                        'name': 'Main Road'
                    }
                }
            ]
        }
        
        with open(self.test_osm_file, 'w') as f:
            json.dump(osm_data, f)
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_conversion(self):
        """Test full conversion process"""
        converter = OSMToPBSUConverter(output_dir=self.temp_dir)
        
        converter.convert(
            self.test_osm_file,
            'TestMap',
            'TestRoute',
            origin_lat=48.8566,
            origin_lon=2.3522
        )
        
        # Check that files were created
        map_file = os.path.join(self.temp_dir, 'TestMap.map.txt')
        self.assertTrue(os.path.exists(map_file))
        
        base_dir = os.path.join(self.temp_dir, 'TestMap')
        self.assertTrue(os.path.exists(base_dir))
        
        tiles_dir = os.path.join(base_dir, 'tiles', 'TestRoute')
        self.assertTrue(os.path.exists(tiles_dir))
        
        # Check entrypoints files
        entrypoints_file = os.path.join(tiles_dir, 'entrypoints.txt')
        self.assertTrue(os.path.exists(entrypoints_file))
        
        entrypoints_list_file = os.path.join(tiles_dir, 'entrypoints_list.txt')
        self.assertTrue(os.path.exists(entrypoints_list_file))
        
        # Check geographic data file
        geo_data_file = os.path.join(base_dir, 'geographic_data.json')
        self.assertTrue(os.path.exists(geo_data_file))
        
        # Verify geographic data content
        with open(geo_data_file, 'r') as f:
            geo_data = json.load(f)
        
        self.assertEqual(len(geo_data['bus_stops']), 2)
        self.assertIn('origin', geo_data)
        self.assertIn('buildings', geo_data)
        self.assertIn('elevations', geo_data)
        
        # Check README
        readme_file = os.path.join(base_dir, 'README.md')
        self.assertTrue(os.path.exists(readme_file))


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_missing_input_file(self):
        """Test handling of missing input file"""
        converter = OSMToPBSUConverter(output_dir=self.temp_dir)
        
        with self.assertRaises(FileNotFoundError):
            converter.convert(
                '/nonexistent/file.json',
                'TestMap',
                'TestRoute'
            )
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        invalid_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(invalid_file, 'w') as f:
            f.write('invalid json content {')
        
        converter = OSMToPBSUConverter(output_dir=self.temp_dir)
        
        with self.assertRaises(json.JSONDecodeError):
            converter.convert(
                invalid_file,
                'TestMap',
                'TestRoute'
            )


class TestAIAutomation(unittest.TestCase):
    """Test AI automation functionality"""
    
    def test_ai_automation_timeout_configuration(self):
        """Test that AIAutomation accepts custom timeout"""
        from ai_automation import AIAutomation
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test default timeout
            automator = AIAutomation(temp_dir)
            self.assertEqual(automator.blender_timeout, 600)
            
            # Test custom timeout
            automator_custom = AIAutomation(temp_dir, blender_timeout=900)
            self.assertEqual(automator_custom.blender_timeout, 900)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOSMParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildingHeightExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinateConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestFileGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestElevationData))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestAIAutomation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
