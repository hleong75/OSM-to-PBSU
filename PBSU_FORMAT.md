# PBSU Format Reference

Technical reference for the Proton Bus Simulator map format.

## Overview

PBSU maps consist of:
- Configuration text files (.txt, .map.txt)
- 3D models (.3ds format, created in Blender 2.79)
- Textures (PNG format, max 2048x2048 for mobile)
- Destination displays (image files)

## Directory Structure

```
MapName.map.txt                    # Main configuration file
MapName/                           # Base directory
├── textures/                      # Texture files (PNG)
├── dest/                          # Destination displays
│   └── DestinationName/          # One folder per destination
│       ├── dest_front.png        # Front display
│       └── dest_side.png         # Side display
├── skins/                         # Bus paint jobs (optional)
│   └── 0/
│       └── pbc/                  # Per bus type
└── tiles/                         # Required name
    └── RouteName/                # Models directory
        ├── *.3ds                 # 3D model files
        ├── *.blend               # Blender source (optional)
        ├── entrypoints.txt       # Bus stop positions
        ├── entrypoints_list.txt  # Bus stop names
        └── aipeople/             # Passenger/NPC configs
            ├── busstops/         # Bus stop configs
            │   └── *.txt
            ├── people/           # Pedestrian configs
            │   └── *.txt
            └── traffic/          # Vehicle traffic configs
                └── *.txt
```

## Main Configuration (.map.txt)

```ini
[map]
baseDir=MapName                   # Base directory name
modelsDir=RouteName              # Models subdirectory in tiles/
textures=textures                # Textures directory name
mapModVersion=2                  # Version (2 for Phase 2, 3 for Phase 3)
preview=preview.png              # Preview image
```

## Entry Points (entrypoints.txt)

Bus stop positions where the bus can spawn:

```ini
[entrypoint_1]
name=BusStopName                 # Internal name (no spaces)
posX=0.0                         # X coordinate (meters, east+)
posY=0.0                         # Y coordinate (meters, up+)
posZ=0.0                         # Z coordinate (meters, north+)
rotX=0                           # Rotation X (usually 0)
rotY=180                         # Rotation Y (heading, 0=north)
rotZ=0                           # Rotation Z (usually 0)
```

**Important Coordinate Notes:**
- Unity uses Y-up coordinate system
- Blender uses Z-up (Y and Z are swapped!)
- Origin point: Choose first bus stop or city center
- Units: 1 unit = 1 meter

## Entry Points List (entrypoints_list.txt)

Simple list of entry point names:
```
BusStop1
BusStop2
BusStop3
```

## Bus Stop Configuration

File: `aipeople/busstops/BusStopName.txt`

```ini
[busstop]
name=Bus Stop Display Name       # Human-readable name
side=right                        # Which side (right/left)
radius=1                          # Trigger radius (deprecated)
paxAmount=5                       # Number of passengers

[from_3d]
readFrom3D=1                      # Always 1 (read from 3D model)
prefix=BusStopName               # Must match 3D object prefix
rotY=0                            # Passenger rotation
```

## 3D Model Requirements

Each bus stop needs these objects in Blender:

1. **Trigger**: `BusStopName_trigger`
   - Box collider where bus stops
   - Tag as "bustrigger"

2. **Passenger Spawn Points**: `BusStopName.000`, `BusStopName.001`, etc.
   - Small planes (0.001 scale)
   - Where passengers wait
   - Number based on paxAmount

3. **Optional Features**:
   - `BusStopName_leftside_trigger` - For left-side stops
   - `terminal` - Mark terminals (no speed complaints)
   - `endpoint` - Force all passengers to exit

## Coordinate Conversion

### From GPS (Latitude/Longitude) to Unity:

```python
# Earth radius in meters
R = 6371000

# Origin point (reference coordinates)
origin_lat, origin_lon = ref_lat, ref_lon

# Convert point to meters
def latlon_to_unity(lat, lon):
    dlat = math.radians(lat - origin_lat)
    dlon = math.radians(lon - origin_lon)
    
    x = dlon * R * math.cos(math.radians(origin_lat))  # East-West
    z = dlat * R                                        # North-South  
    y = 0.0                                             # Ground level
    
    return (x, y, z)
```

### Rotation Calculation:

```python
def calculate_heading(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2"""
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    angle = math.atan2(dlon, dlat)
    angle_deg = math.degrees(angle)
    
    # Normalize to 0-360
    return (angle_deg + 360) % 360
```

## File Naming Rules

**IMPORTANT:**
- No spaces in filenames
- No accents or special characters (é, ñ, ç, etc.)
- Use underscores: `Bus_Stop_Name`
- Case sensitive on some systems
- Internal names != Display names

**Good:**
- `Central_Station.txt` ✓
- `Linha_9001` ✓
- `Sao_Paulo_Map` ✓

**Bad:**
- `Central Station.txt` ✗ (space)
- `Línea_9001` ✗ (accent)
- `São Paulo Map` ✗ (multiple issues)

## Texture Requirements

- **Format**: PNG (avoid JPG, causes issues)
- **Max size**: 2048x2048 pixels for mobile
- **Power of 2**: Preferably 512, 1024, 2048
- **Optimization**: Use smaller textures when possible
- **Transparency**: Supported in PNG

## Map Version Support

### Version 2 (Phase 2):
- Bus stops with passengers
- Basic traffic
- Entry points
- Destinations

### Version 3 (Phase 3):
- All Phase 2 features
- Traffic lights (`mapModVersion=3`)
- Street lights
- Advanced traffic control
- GPS waypoints

This converter generates **Version 2** files.

## Performance Considerations

### Mobile Devices:
- Keep total polygons under 400k triangles
- Use textures ≤ 2048px
- Optimize colliders
- Test on target devices

### Route Size:
- Limit to 20-40 minutes of driving
- Split large cities into multiple maps
- Each map is loaded entirely (no streaming)

### Known Limitations:
- Floating point precision issues beyond 10km from origin
- Physics reset needed when driving far from (0,0,0)
- Unity engine limitation (32-bit floats)

## Advanced Features (Phase 3)

Not generated by this converter, but can be added manually:

### Traffic Lights:
```ini
[trafficlight_1]
posX=100.0
posY=0.0
posZ=200.0
# ... additional config
```

### Pedestrians:
```ini
[people_1]
prefix=ped_group_1
amount=10
# ... paths and behavior
```

### AI Traffic:
```ini
[traffic_1]
prefix=traffic_spawn_1
vehicleType=car
# ... spawn settings
```

See `ajuda - help/Tutorial Mods de mapas - Fase 3.pdf` for details.

## Tools Used

- **Blender 2.79**: 3D modeling (required version!)
- **Modified 3DS exporter**: Supports longer names (>12 chars)
- **Python 3**: For this converter
- **OpenStreetMap**: Source of real-world data

## References

- Official PBSU Documentation: `ajuda - help/` folder
- PBSU Website: http://www.protonbus.com.br
- Mods Portal: http://busmods.com
- Community: Facebook groups (see main README)

## Contributing to This Converter

Want to extend the converter? Here are areas for improvement:

1. **Phase 3 Support**: Add traffic light generation
2. **Better Rotation**: Calculate stop orientation from road direction
3. **Pedestrian Paths**: Generate walking paths between stops
4. **Traffic Generation**: Create AI vehicle spawn points
5. **OSM Relations**: Better handling of bus route relations
6. **UI/GUI**: Desktop application instead of CLI
7. **Blender Export**: Direct .blend file generation (if possible)

See the code in `osm_to_pbsu.py` - it's designed to be extended!

## Debugging Tips

### View Generated Coordinates:
```bash
cat output/MapName/tiles/RouteName/entrypoints.txt
```

### Check Bus Stop Names:
```bash
ls output/MapName/tiles/RouteName/aipeople/busstops/
```

### Validate Structure:
```bash
tree output/MapName/
```

### Test Coordinate Conversion:
```python
from osm_to_pbsu import OSMToPBSUConverter
converter = OSMToPBSUConverter()
x, y, z = converter.lat_lon_to_unity_coords(40.7580, -73.9855, 40.7580, -73.9855)
print(f"Origin: ({x}, {y}, {z})")  # Should be (0, 0, 0)
```

## License & Attribution

- This converter: Open source
- PBSU: Proprietary (Via Mep)
- OpenStreetMap data: © OSM contributors (ODbL license)
- Generated maps: Your content, but OSM attribution required

When publishing maps, credit OpenStreetMap contributors!

---

For more information, see the main README.md and PBSU documentation in `ajuda - help/`.
