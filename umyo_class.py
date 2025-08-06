"""uMyo EMG Sensor Device Class

This module defines the uMyo class which represents a single EMG sensor device
and contains all its real-time data including muscle signals, orientation, and status.

Classes:
    uMyo: Represents a single uMyo EMG sensor device with all its data streams.

Example:
    ```python
    from umyo_class import uMyo

    # Create a new device instance
    device = uMyo(unit_id=12345)

    # Access EMG data
    muscle_signal = device.data_array[0]
    spectrum_band = device.device_spectr[2]

    # Access orientation data
    quaternion = device.Qsg  # [w, x, y, z]
    yaw_angle = device.yaw
    ```
"""

from typing import List


class uMyo:
    """Represents a single uMyo EMG sensor device.

    This class stores all real-time data from a uMyo device including:
    - EMG signal data and frequency spectrum
    - 3D orientation (quaternions and Euler angles)
    - Device status (battery, version, signal strength)
    - Timing and synchronization information

    Attributes:
        unit_id (int): Unique identifier for this device
        data_array (List[int]): Raw EMG signal samples (up to 64 values)
        device_spectr (List[int]): Frequency spectrum analysis (16 bands)
        Qsg (List[float]): Quaternion orientation [w, x, y, z]
        yaw (float): Yaw angle in radians
        pitch (float): Pitch angle in radians
        roll (float): Roll angle in radians
        batt (int): Battery level in millivolts
        rssi (int): Received signal strength indicator
        data_id (int): Sequential data packet identifier

    Example:
        ```python
        device = uMyo(12345)

        # Check if device has new data
        if device.data_count > 0:
            latest_signal = device.data_array[0]

        # Get device orientation
        w, x, y, z = device.Qsg
        orientation_angles = (device.yaw, device.pitch, device.roll)

        # Check device status
        battery_percent = (device.batt - 3100) / 10  # Approximate percentage
        signal_quality = 90 - device.rssi if device.rssi > 0 else 0
        ```
    """

    def __init__(self, uid):
        """Initialize a new uMyo device instance.

        Args:
            uid (int): Unique identifier for this device

        Note:
            All data arrays and values are initialized to zero. Real data
            will be populated by the parser as packets are received.
        """
        self.last_pack_id = 0
        self.unit_id = uid
        self.packet_type = 0
        self.data_count = 0
        self.batt = 0
        self.version = 0
        self.steps = 0
        self.data_id = 0
        self.prev_data_id = 0
        self.data_array = [
            0
        ] * 64  # in case of further changes, right now 16 data points
        self.device_spectr = [0] * 16
        # sQ Qsg;
        # sQ zeroQ;
        self.Qsg = [0, 0, 0, 0]
        self.zeroQ = [0, 0, 0, 0]
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.dev_yaw = 0
        self.dev_pitch = 0
        self.dev_roll = 0
        self.update_time = 0
        self.yaw_speed = 0
        self.pitch_speed = 0
        self.roll_speed = 0
        self.mag_angle = 0
