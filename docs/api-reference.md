# API Reference

## 📚 Core Modules

### umyo_class.py - Device Data Model

The fundamental data structure representing a single uMyo sensor device.

#### Class: uMyo

```python
class uMyo:
    """
    Represents a single uMyo sensor device with complete state information.
    
    Attributes:
        unit_id (int): Unique 32-bit device identifier
        data_array (list): EMG signal history buffer (64 samples)
        device_spectr (list): 16-band frequency spectrum analysis
        Qsg (list): Current quaternion [w, x, y, z] for orientation
        Acc (list): Accelerometer readings [x, y, z] in raw ADC values
        batt (int): Battery voltage in millivolts
        rssi (int): Received Signal Strength Indicator
        data_id (int): Sequential packet identifier
        data_count (int): Number of samples in current update
    """
```

#### Key Properties

```python
# EMG Data (muscle electrical activity)
data_array[64]      # Raw EMG signal samples 
device_spectr[16]   # Frequency spectrum bands (0-4: low freq, 5-15: higher freq)

# 3D Orientation (sensor fusion)
Qsg[4]              # Quaternion [w, x, y, z] - primary orientation
zeroQ[4]            # Reference quaternion for relative positioning
yaw, pitch, roll    # Euler angles derived from quaternion

# Device Health
batt                # Battery voltage in millivolts (3100-4200 typical)
rssi                # Signal strength (lower = better signal)
data_id             # Sequential packet identifier
```

### umyo_parser.py - Protocol Engine

Core communication engine for serial data parsing and device management.

#### Functions

```python
def umyo_parse_preprocessor(data: bytes) -> int:
    """
    Process raw serial data and parse complete uMyo protocol packets.
    
    Args:
        data: Raw serial data from uMyo devices
        
    Returns:
        Number of bytes remaining in unprocessed buffer
        
    Example:
        >>> raw_bytes = ser.read(1024)
        >>> unprocessed = umyo_parse_preprocessor(raw_bytes)
        >>> devices = umyo_get_list()
    """

def umyo_get_list() -> List[uMyo]:
    """
    Get the current list of active uMyo devices.
    
    Returns:
        List of active uMyo device instances with complete sensor data
        
    Example:
        >>> devices = umyo_get_list()
        >>> for device in devices:
        ...     print(f"Device {device.unit_id:08X}: {device.data_array[-1]}")
    """

def id2idx(uid: int) -> int:
    """
    Convert device unit ID to internal array index with lifecycle management.
    
    Args:
        uid: 32-bit device unit identifier
        
    Returns:
        Internal array index for device data access
    """
```

### quat_math.py - 3D Mathematics

Professional quaternion mathematics library for 3D orientation calculations.

#### Data Types

```python
from collections import namedtuple

sV = namedtuple("sV", "x y z")        # 3D Vector (x, y, z)
sQ = namedtuple("sQ", "w x y z")      # Quaternion (w + xi + yj + zk)
```

#### Core Functions

```python
def q_norm(q: sQ) -> float:
    """Calculate quaternion magnitude: √(w² + x² + y² + z²)"""

def q_renorm(q: sQ) -> sQ:
    """Normalize quaternion to unit length for valid rotation"""

def q_make_conj(q: sQ) -> sQ:
    """Compute quaternion conjugate: (w, -x, -y, -z)"""

def q_mult(q1: sQ, q2: sQ) -> sQ:
    """Multiply two quaternions (composition of rotations)"""

def rotate_v(q: sQ, v: sV) -> sV:
    """Rotate vector by quaternion: v' = q * v * q*"""

def q_from_vectors(u: sV, v: sV) -> sQ:
    """Compute rotation quaternion from vector u to vector v"""
```

## 🎮 Application Modules

### umyo_mouse.py - Gesture Mouse Control

Advanced EMG-based mouse control system.

#### Key Functions

```python
def calibrate_mouse_control():
    """
    Interactive calibration system for personalized mouse control.
    
    Calibration stages:
    1. Center position establishment
    2. X-axis movement mapping
    3. Y-axis movement mapping
    4. Z-axis rotation (scroll) mapping
    5. EMG threshold learning
    """

def process_mouse_movement(orientation_data, emg_data):
    """
    Convert sensor data to mouse movements and clicks.
    
    Args:
        orientation_data: Quaternion orientation from sensor
        emg_data: EMG signal amplitudes for click detection
    """
```

### display_stuff.py - Multi-Device Visualization

Comprehensive visualization system for multiple sensors.

#### Visualization Functions

```python
def plot_init():
    """Initialize plotting buffers for all supported devices (up to 64)"""

def plot_cycle_spg():
    """Display spectrogram visualization with color-coded frequency bands"""

def plot_cycle_tester():
    """Comprehensive analysis view with EMG, accelerometer, and status"""

def num_to_color(device_id: int) -> tuple:
    """Convert device ID to unique RGB color for visual identification"""
```

## 🔧 Utility Modules

### bootloader_usb.py - Firmware Management

Complete firmware upload system for device programming.

#### Key Functions

```python
def fw_upload_parser(data: bytes):
    """Parse firmware upload responses and handle error codes"""

def send_data_serial(data: bytes, data_len: int):
    """Send firmware data with checksum verification"""
```

#### Error Codes

```python
err_code_ok = 11              # Successful operation
err_code_toolong = 100        # Packet too large  
err_code_wrongcheck = 101     # Checksum mismatch
err_code_wronglen = 102       # Incorrect packet length
err_code_packmiss = 103       # Missing packet in sequence
err_code_timeout = 104        # Communication timeout
```

## 📊 Configuration Parameters

### Serial Communication

```python
SERIAL_CONFIG = {
    'baudrate': 921600,           # High-speed for real-time data
    'parity': serial.PARITY_NONE, # No parity checking
    'stopbits': 1,                # Single stop bit
    'bytesize': 8,                # 8 data bits
    'timeout': 0                  # Non-blocking reads
}
```

### Mouse Control Settings

```python
MOVEMENT_CONFIG = {
    'base_scale': 0.1,            # Overall sensitivity multiplier
    'max_movement': 50,           # Maximum pixels per update
    'deadzone': 0.02,             # Center deadzone threshold
}

EMG_CONFIG = {
    'muscle_smoothing': 0.9,      # Exponential smoothing factor
    'activation_delay': 0.1,      # Minimum activation time (seconds)
    'threshold_adaptation': True   # Enable adaptive thresholds
}
```

### Display Configuration

```python
DISPLAY_CONFIG = {
    'window_size': (1200, 500),   # Main window dimensions
    'refresh_rate': 60,           # Target FPS for smooth animation
    'color_scheme': 'professional' # Visual theme selection
}

DEVICE_COLORS = [
    (0, 200, 0),      # Device 0: Green
    (0, 100, 200),    # Device 1: Blue
    (150, 150, 0),    # Device 2: Yellow
    (200, 0, 250),    # Device 3: Magenta
    # ... extends to 64 devices
]
```

## 🔍 Protocol Specification

### Packet Structure

```
uMyo Communication Protocol:
[Header: 0x4F 0xD5] [RSSI] [Packet ID] [Length] [Device ID: 4 bytes] 
[Packet Type] [Parameters] [EMG Data: 32 bytes] [Spectrum: 8 bytes]
[Quaternion: 8 bytes] [Accelerometer: 6 bytes] [Euler Angles: 6 bytes]
[Magnetometer: 6 bytes] [Checksum]
```

### Data Formats

```python
# EMG Samples: 16-bit signed integers
emg_value = struct.unpack('>h', raw_bytes[0:2])[0]  # Big-endian signed short

# Quaternion: 16-bit signed fixed-point (divide by 32768)
qw = struct.unpack('>h', raw_bytes[0:2])[0] / 32768.0

# Accelerometer: 16-bit signed raw ADC values
ax = struct.unpack('>h', raw_bytes[0:2])[0]
```

## 🎯 Usage Examples

### Basic Device Connection

```python
import umyo_parser
import serial
from serial.tools import list_ports

# Connect to uMyo device
ports = list(list_ports.comports())
ser = serial.Serial(ports[-1].device, 921600, timeout=0)

# Process data in real-time loop
while True:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        umyo_parser.umyo_parse_preprocessor(data)
        
        devices = umyo_parser.umyo_get_list()
        if devices:
            device = devices[0]
            print(f"EMG: {device.data_array[-1]}, Battery: {device.batt}mV")
```

### 3D Orientation Tracking

```python
import quat_math

# Get orientation from device
device = umyo_parser.umyo_get_list()[0]
current_q = quat_math.sQ(*device.Qsg)

# Calculate relative rotation
reference_q = quat_math.sQ(1, 0, 0, 0)  # Identity quaternion
relative_q = quat_math.q_mult(current_q, quat_math.q_make_conj(reference_q))

# Convert to Euler angles
yaw = device.yaw
pitch = device.pitch  
roll = device.roll
print(f"Orientation: Y={yaw:.1f}°, P={pitch:.1f}°, R={roll:.1f}°")
```

### Multi-Device Monitoring

```python
import display_stuff

# Initialize visualization system
display_stuff.plot_init()

# Process multiple devices
while True:
    # ... data acquisition loop ...
    devices = umyo_parser.umyo_get_list()
    
    for i, device in enumerate(devices):
        color = display_stuff.num_to_color(i)
        print(f"Device {i} (color={color}): EMG={device.data_array[-1]}")
    
    # Update visualization
    display_stuff.plot_cycle_spg()
```

## 🚨 Error Handling

### Common Exception Types

```python
# Serial communication errors
try:
    ser = serial.Serial(port, 921600)
except serial.SerialException as e:
    print(f"Serial connection failed: {e}")

# Data parsing errors
try:
    umyo_parser.umyo_parse_preprocessor(data)
except ValueError as e:
    print(f"Invalid data format: {e}")

# Device access errors
devices = umyo_parser.umyo_get_list()
if not devices:
    print("No active devices found")
else:
    device = devices[0]
    if device.data_count == 0:
        print("No new data available")
```

### Best Practices

```python
# Always check for data availability
if ser.in_waiting > 0:
    data = ser.read(ser.in_waiting)
    # Process data...

# Validate device list before access
devices = umyo_parser.umyo_get_list()
if devices and len(devices) > 0:
    device = devices[0]
    # Use device data...

# Handle quaternion normalization
import quat_math
q = quat_math.sQ(*device.Qsg)
if quat_math.q_norm(q) > 0.1:  # Valid quaternion
    q_normalized = quat_math.q_renorm(q)
    # Use normalized quaternion...
```
