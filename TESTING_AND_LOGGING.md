# Testing and Logging Guide

## Overview

The OSM to PBSU Converter now includes comprehensive logging and automated testing to improve debugging, especially for Blender-related issues.

## Logging

### Log Files

Two log files are automatically created:

1. **osm_to_pbsu.log** - Main conversion process logs
2. **ai_automation.log** - AI automation and Blender execution logs

### Log Format

```
2025-11-11 16:21:28,857 - module_name - LEVEL - Message
```

- **Timestamp**: ISO format with milliseconds
- **Module**: Source module (osm_to_pbsu or ai_automation)
- **Level**: DEBUG, INFO, WARNING, or ERROR
- **Message**: Detailed log message

### What Gets Logged

#### osm_to_pbsu.log
- ✅ OSM file loading and parsing
- ✅ Bus stop, road, and building extraction
- ✅ Coordinate conversions
- ✅ File generation (map files, entrypoints, etc.)
- ✅ Geographic data export
- ✅ Elevation data processing
- ✅ LiDAR file loading (when used)
- ✅ All errors with stack traces

#### ai_automation.log
- ✅ Blender script generation
- ✅ Blender command execution
- ✅ Blender process output (stdout/stderr)
- ✅ Blender return codes
- ✅ 3DS file validation (size, existence)
- ✅ Texture generation progress
- ✅ Each automation step with timing
- ✅ All errors with detailed diagnostics

### Example Log Output

```
2025-11-11 16:21:28,857 - __main__ - INFO - Starting OSM to PBSU Conversion
2025-11-11 16:21:28,857 - __main__ - INFO - OSM file: examples/sample_route.json
2025-11-11 16:21:28,857 - __main__ - INFO - Map name: Test_City
2025-11-11 16:21:28,857 - __main__ - INFO - Found 5 elements in OSM data
2025-11-11 16:21:28,857 - __main__ - INFO - First pass complete: 5 nodes, 5 bus stops found
```

### Viewing Logs

```bash
# View conversion logs
cat osm_to_pbsu.log

# View last 50 lines
tail -50 osm_to_pbsu.log

# Follow log in real-time
tail -f osm_to_pbsu.log

# View automation logs
cat ai_automation.log

# Search for errors
grep ERROR *.log
```

### Debugging Blender Issues

When Blender fails ("blender quit"), check `ai_automation.log`:

```bash
# Find Blender errors
grep -A 10 "Blender process failed" ai_automation.log

# View full Blender output
grep "Blender stdout:" -A 100 ai_automation.log

# Check return code
grep "return code" ai_automation.log
```

The log will show:
1. **Exact Blender command** executed
2. **Full output** from Blender
3. **Return code** (0 = success, non-zero = error)
4. **3DS file status** (size, existence)
5. **Last 50 lines** of output on error

## Testing

### Test Suite

The test suite (`test_osm_to_pbsu.py`) includes 18 tests covering all major functionality.

### Running Tests

```bash
# Run all tests
python test_osm_to_pbsu.py

# Run with unittest (more verbose)
python -m unittest test_osm_to_pbsu -v

# Run specific test class
python -m unittest test_osm_to_pbsu.TestOSMParsing

# Run specific test
python -m unittest test_osm_to_pbsu.TestOSMParsing.test_parse_bus_stops
```

### Test Categories

#### 1. OSM Parsing (3 tests)
```python
test_parse_bus_stops        # Bus stop extraction
test_parse_roads           # Road segment extraction
test_parse_buildings       # Building extraction with heights
```

#### 2. Building Height Extraction (4 tests)
```python
test_extract_height_from_tag           # Direct height tag
test_extract_height_from_levels        # Building levels calculation
test_extract_height_from_building_height  # building:height tag
test_default_height_by_type           # Default heights by type
```

#### 3. Coordinate Conversion (2 tests)
```python
test_lat_lon_to_unity_coords  # Lat/lon to Unity conversion
test_zero_offset             # Same coordinates = zero offset
```

#### 4. File Generation (3 tests)
```python
test_generate_map_txt          # Main map file
test_generate_entrypoints_list  # Entrypoints list
test_generate_busstop_txt      # Bus stop configs
```

#### 5. Directory Structure (1 test)
```python
test_create_directory_structure  # PBSU directory creation
```

#### 6. Elevation Data (2 tests)
```python
test_fetch_elevation_data_returns_zero  # API disabled behavior
test_load_lidar_elevation_nonexistent_file  # LiDAR error handling
```

#### 7. Integration (1 test)
```python
test_full_conversion  # Complete workflow test
```

#### 8. Error Handling (2 tests)
```python
test_missing_input_file  # Missing file handling
test_invalid_json       # Invalid JSON handling
```

### Test Output

```
test_parse_bus_stops ... ok
test_parse_roads ... ok
test_parse_buildings ... ok
...
----------------------------------------------------------------------
Ran 18 tests in 0.011s

OK
```

### Writing New Tests

```python
import unittest
from osm_to_pbsu import OSMToPBSUConverter

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.converter = OSMToPBSUConverter()
    
    def test_something(self):
        result = self.converter.some_method()
        self.assertEqual(result, expected_value)
```

## Troubleshooting with Logs

### Problem: Blender Quits Unexpectedly

**Solution:** Check `ai_automation.log`

```bash
# Find the error
grep -A 20 "Blender process failed" ai_automation.log

# Look for specific Blender errors
grep -i "error\|exception\|failed" ai_automation.log
```

**Common Issues:**
1. **Blender not found**: Check Blender path in log
2. **Script error**: Check "Blender stdout" section
3. **Empty 3DS**: Check "3DS file size: 0 bytes" message

### Problem: Conversion Fails

**Solution:** Check `osm_to_pbsu.log`

```bash
# Find the error
grep ERROR osm_to_pbsu.log

# See full context
tail -100 osm_to_pbsu.log
```

**Common Issues:**
1. **Missing bus stops**: Check "Found 0 bus stops" message
2. **File not found**: Check file paths in log
3. **Invalid JSON**: Check "Failed to load OSM file" message

### Problem: No Elevation Data

**Solution:** Check log messages

```bash
grep -i "elevation" osm_to_pbsu.log
```

**Messages:**
- "API calls disabled - using default elevation of 0m"
- "Using LiDAR HD file for elevation"
- "LiDAR file not found"

### Problem: Tests Fail

**Solution:** Run specific test to see details

```bash
# Run failing test with verbose output
python -m unittest test_osm_to_pbsu.TestClassName.test_name -v

# Check test logs
grep -i "test_" osm_to_pbsu.log
```

## Best Practices

### 1. Always Check Logs After Errors

```bash
# Quick check
tail -50 osm_to_pbsu.log
tail -50 ai_automation.log
```

### 2. Run Tests Before Committing Changes

```bash
python test_osm_to_pbsu.py
```

### 3. Keep Logs Clean

```bash
# Archive old logs
mkdir logs_archive
mv *.log logs_archive/

# Or delete old logs
rm *.log
```

### 4. Enable Debug Logging (if needed)

In the Python files, change:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### 5. Use Log Rotation (for production)

Add to beginning of main():
```python
import logging.handlers
handler = logging.handlers.RotatingFileHandler(
    'osm_to_pbsu.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Run tests
        run: python test_osm_to_pbsu.py
      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v2
        with:
          name: logs
          path: '*.log'
```

## Performance Monitoring

### Check Conversion Time

```bash
# Add timing
time python osm_to_pbsu.py examples/sample_route.json -m Test -r Route1

# Check log timestamps
grep "Starting OSM\|Conversion Complete" osm_to_pbsu.log
```

### Monitor Log Size

```bash
# Check log file sizes
ls -lh *.log

# If logs get too large, rotate them
mv osm_to_pbsu.log osm_to_pbsu.log.1
mv ai_automation.log ai_automation.log.1
```

## FAQ

**Q: Can I disable logging?**
A: Modify the logging setup in the Python files to set level to WARNING or ERROR.

**Q: Where are logs stored?**
A: In the same directory as the Python scripts.

**Q: Can I change log format?**
A: Yes, modify the `format` parameter in `logging.basicConfig()`.

**Q: How do I test only one feature?**
A: Use `python -m unittest test_osm_to_pbsu.TestClassName`.

**Q: Why are logs so verbose?**
A: DEBUG level captures everything. Change to INFO for less detail.

**Q: Can I redirect logs to another file?**
A: Yes, modify the `FileHandler` path in the logging setup.

## Summary

- ✅ Comprehensive logging for debugging
- ✅ Especially detailed for Blender operations
- ✅ 18 automated tests covering all features
- ✅ Easy to troubleshoot issues with log files
- ✅ No API calls - everything runs offline
- ✅ LiDAR HD support for accurate elevation
- ✅ Test suite ensures quality

For more information, see [CHANGELOG.md](CHANGELOG.md).
