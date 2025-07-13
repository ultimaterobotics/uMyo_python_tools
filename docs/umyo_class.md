# uMyo Class API Reference

## Overview

The `uMyo` class represents a single EMG sensor device and contains all real-time data streams including muscle signals, 3D orientation, and device status information.

## Class Definition

```python
class uMyo:
    """Represents a single uMyo EMG sensor device."""
```

## Constructor

### `__init__(self, uid: int) -> None`

Initialize a new uMyo device instance.

**Parameters:**
- `uid` (int): Unique identifier for this device

**Example:**
```python
device = uMyo(unit_id=12345)
```

## Attributes

### Device Identification
- `unit_id` (int): Unique 32-bit device identifier
- `version` (int): Firmware version number
- `packet_type` (int): Type of the last received packet

### EMG Signal Data
- `data_count` (int): Number of valid samples in data_array
- `data_array` (List[int]): Raw EMG samples [64] (16-bit signed integers)
- `device_spectr` (List[int]): Frequency spectrum analysis [16 bands]

### 3D Orientation
- `Qsg` (List[float]): Current quaternion orientation [w, x, y, z]
- `zeroQ` (List[float]): Reference quaternion for calibration
- `yaw` (float): Rotation around Z-axis (heading)
- `pitch` (float): Rotation around Y-axis (elevation)  
- `roll` (float): Rotation around X-axis (bank)

### Device Status
- `batt` (int): Battery voltage in millivolts (3100-4200 typical)
- `rssi` (int): Received Signal Strength Indicator (0-100, lower is better)
- `data_id` (int): Sequential packet counter for synchronization
- `update_time` (float): Timestamp of last data update

### Raw Sensor Data
- `ax, ay, az` (int): Raw accelerometer readings (ADC values)
- `mag_angle` (float): Magnetometer-derived compass angle

## Usage Examples

### Basic Data Access
```python
# Create device instance
device = uMyo(12345)

# Access latest EMG signal
if device.data_count > 0:
    latest_signal = device.data_array[0]
    print(f"EMG Signal: {latest_signal}")

# Get frequency spectrum
low_freq_power = device.device_spectr[0:4]   # Low frequency bands
mid_freq_power = device.device_spectr[4:8]   # Mid frequency bands
high_freq_power = device.device_spectr[8:16] # High frequency bands
```

### Orientation Data
```python
# Get quaternion orientation
w, x, y, z = device.Qsg
print(f"Quaternion: ({w:.3f}, {x:.3f}, {y:.3f}, {z:.3f})")

# Get Euler angles
print(f"Yaw: {device.yaw:.1f}°")
print(f"Pitch: {device.pitch:.1f}°") 
print(f"Roll: {device.roll:.1f}°")
```

### Device Health Monitoring
```python
# Check battery level (convert to percentage)
battery_percent = max(0, min(100, (device.batt - 3100) / 10))
print(f"Battery: {battery_percent:.1f}%")

# Check signal quality
if device.rssi > 0:
    signal_quality = max(0, 90 - device.rssi)
    if signal_quality > 70:
        print("Signal: Excellent")
    elif signal_quality > 50:
        print("Signal: Good")
    elif signal_quality > 30:
        print("Signal: Fair")
    else:
        print("Signal: Poor")
```

## Data Interpretation

### EMG Signal Values
- **Range**: -32768 to +32767 (16-bit signed)
- **Units**: Raw ADC values (proportional to muscle electrical activity)
- **Typical**: Resting muscle ~0, active muscle 500-5000+
- **Sampling**: Usually 16 samples per packet at 500Hz

### Frequency Spectrum
- **Bands**: 16 frequency bands from DC to ~250Hz
- **Bands 0-3**: Low frequency (0-50Hz) - movement artifacts
- **Bands 4-7**: Mid frequency (50-100Hz) - primary EMG content
- **Bands 8-15**: High frequency (100-250Hz) - motor unit recruitment

### Orientation Accuracy
- **Quaternion**: Normalized unit quaternion (magnitude ≈ 1.0)
- **Euler Angles**: Degrees or radians depending on implementation
- **Accuracy**: ±1-2° under normal conditions
- **Update Rate**: 100-500Hz depending on configuration

## Thread Safety

The `uMyo` class is **not thread-safe**. If accessing from multiple threads:

```python
import threading

# Use a lock when accessing device data
device_lock = threading.Lock()

def safe_read_emg(device):
    with device_lock:
        return device.data_array[0] if device.data_count > 0 else 0

def safe_read_orientation(device):
    with device_lock:
        return (device.yaw, device.pitch, device.roll)
```
