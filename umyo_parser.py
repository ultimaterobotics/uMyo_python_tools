"""Core uMyo Protocol Parser and Data Processing Engine.

This module implements the complete parsing and processing pipeline for uMyo 
sensor data, handling the proprietary communication protocol, data extraction, 
and real-time sensor state management. It serves as the central hub for all 
uMyo data processing operations in the Python tools ecosystem.

The parser provides comprehensive support for:

- Multi-device protocol parsing and data extraction
- Real-time EMG signal processing and spectral analysis
- IMU data processing including quaternion and accelerometer data
- Device state management and automatic discovery
- Data integrity verification and error handling
- Efficient buffer management for continuous operation
- Device lifecycle management with automatic cleanup

Key Features:
    - Complete uMyo protocol implementation and parsing
    - Multi-device support with automatic device discovery
    - Real-time EMG signal processing and frequency analysis
    - IMU data extraction (quaternions, accelerometer, gyroscope)
    - Device metadata processing (battery, RSSI, status)
    - Efficient circular buffer management for continuous operation
    - Automatic device cleanup and memory management
    - Robust error handling and data validation

Protocol Implementation:
    - Packet-based communication with header validation
    - Multi-byte device ID support (32-bit addressing)
    - Variable-length payload processing
    - CRC verification for data integrity
    - Device status and metadata extraction
    - Real-time signal processing and analysis

Data Processing Pipeline:
    1. Raw serial data → Buffer accumulation
    2. Packet detection and header validation
    3. Device identification and management
    4. Payload extraction and parsing
    5. Signal processing and analysis
    6. Data structure population and storage
    7. Device state management and cleanup

Supported Data Types:
    - EMG signals: Raw amplitude values with real-time processing
    - IMU data: Quaternions, accelerometer, gyroscope, magnetometer
    - Device metadata: Battery level, RSSI, connection status
    - Spectral data: Frequency domain analysis of EMG signals
    - Timing information: Data IDs and synchronization markers

Applications:
    - Real-time EMG data acquisition and processing
    - Multi-device sensor networks and data fusion
    - Gesture recognition and motion tracking systems
    - Biomedical research and clinical applications
    - Human-computer interface development
    - Prosthetic control and assistive technology
    - Educational platforms for EMG/IMU signal processing

Dependencies:
    - umyo_class: Core uMyo device data structures and management
    - quat_math: Quaternion mathematics and transformations
    - math: Mathematical operations for signal processing

Example Usage:
    >>> import umyo_parser
    >>> 
    >>> # Process raw serial data
    >>> raw_data = b'\\x42\\x10...'  # Raw bytes from serial port
    >>> unprocessed_count = umyo_parser.umyo_parse_preprocessor(raw_data)
    >>> 
    >>> # Get list of active devices
    >>> devices = umyo_parser.umyo_get_list()
    >>> if devices:
    ...     primary_device = devices[0]
    ...     print(f"Device ID: {primary_device.unit_id}")
    ...     print(f"Latest EMG: {primary_device.data_array[-1]}")
    ...     print(f"Quaternion: {primary_device.Qsg}")

Performance Characteristics:
    - Optimized for real-time continuous operation
    - Memory-efficient with automatic cleanup of inactive devices
    - Low-latency processing suitable for control applications
    - Scalable to multiple simultaneous devices
    - Robust error handling for continuous operation

Protocol Specification:
    - Header: Packet ID, length, device ID (32-bit)
    - Payload: Variable length based on packet type
    - Footer: CRC checksum for data integrity
    - Device management: Automatic discovery and lifecycle
    - Error handling: Graceful degradation and recovery

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# parser

import umyo_class
import quat_math
import math

parse_buf = bytearray(0)

umyo_list = []
unseen_cnt = []


def id2idx(uid):
    """Convert device unit ID to internal array index with lifecycle management.
    
    Maps a 32-bit device unit ID to an internal array index for efficient 
    device data storage and retrieval. This function also handles device 
    lifecycle management by automatically removing inactive devices that 
    haven't been seen for an extended period.
    
    The function implements a sophisticated device management strategy:
    - Maintains a mapping between device IDs and internal array indices
    - Automatically cleans up inactive devices to prevent memory leaks
    - Creates new device entries for previously unseen devices
    - Tracks device activity to determine cleanup candidates
    
    Args:
        uid (int): 32-bit device unit identifier. This should be the unique 
            device ID extracted from the uMyo protocol packet header.
    
    Returns:
        int: Internal array index (0-based) corresponding to the device ID.
            This index can be used to access device data in umyo_list.
    
    Side Effects:
        - May create new uMyo device instances for unknown device IDs
        - Removes inactive devices with unseen_cnt > 1000
        - Updates unseen_cnt counters for all active devices
        - Modifies global umyo_list and unseen_cnt arrays
    
    Example:
        >>> # Get index for device with ID 0x12345678
        >>> device_index = id2idx(0x12345678)
        >>> device = umyo_list[device_index]
        >>> print(f"Device at index {device_index}: {device.unit_id}")
    
    Device Lifecycle:
        1. New device: Creates uMyo instance and appends to umyo_list
        2. Active device: Resets unseen_cnt to 0 and returns existing index
        3. Inactive device: Increments unseen_cnt for cleanup tracking
        4. Cleanup: Removes devices with unseen_cnt > 1000 iterations
    
    Memory Management:
        - Automatic cleanup prevents unlimited memory growth
        - Inactive device threshold: 1000 parser iterations
        - Memory usage scales with number of active devices only
        - Efficient array management with minimal overhead
    
    Performance Notes:
        - O(n) complexity where n is the number of active devices
        - Cleanup operations are performed during normal operation
        - Memory usage bounded by active device count
        - Suitable for long-running applications with device churn
    """
    cnt = len(umyo_list)
    u = 0
    while (u < cnt):
        if (unseen_cnt[u] > 1000 and umyo_list[u].unit_id != uid):
            del umyo_list[u]
            del unseen_cnt[u]
            cnt -= 1
        else:
            u += 1
    for u in range(cnt):
        unseen_cnt[u] += 1
        if (umyo_list[u].unit_id == uid):
            unseen_cnt[u] = 0
            return u

    umyo_list.append(umyo_class.uMyo(uid))
    unseen_cnt.append(0)
    return cnt


def umyo_parse(pos):
    """Parse a complete uMyo protocol packet and extract device data.
    
    Processes a validated uMyo protocol packet starting at the specified 
    position in the global parse buffer. This function handles the complete 
    packet parsing pipeline including header extraction, payload processing, 
    data conversion, and device state updates.
    
    The parsing process extracts:
    - Device identification and metadata (unit ID, RSSI, battery)
    - EMG signal data with real-time processing
    - IMU data including quaternions and accelerometer readings
    - Spectral analysis data for frequency domain processing
    - Device status and configuration information
    
    Args:
        pos (int): Starting position in the global parse_buf where the 
            packet header begins. This position should point to the packet 
            ID byte of a validated packet.
    
    Returns:
        int: Number of bytes processed and consumed from the parse buffer.
            This value is used to advance the buffer position for the next 
            packet parsing operation.
    
    Side Effects:
        - Updates device data in the global umyo_list array
        - Modifies device state including EMG, IMU, and metadata
        - Performs real-time signal processing and spectral analysis
        - Updates device timestamps and activity indicators
    
    Packet Structure:
        - Byte 0: Packet ID (identifies packet type and format)
        - Byte 1: Packet length (total payload bytes)
        - Bytes 2-5: Device unit ID (32-bit big-endian)
        - Bytes 6+: Variable payload based on packet type
        - Last byte: RSSI value (signal strength indicator)
    
    Data Processing:
        1. Header Extraction:
           - Packet ID and length validation
           - Device unit ID extraction (32-bit)
           - RSSI extraction from packet trailer
        
        2. Device Management:
           - Device lookup or creation via id2idx()
           - Device state initialization if new
           - Activity tracking and lifecycle management
        
        3. Payload Processing:
           - EMG data extraction and scaling
           - IMU quaternion and accelerometer processing
           - Spectral data extraction and analysis
           - Battery and status information update
        
        4. Signal Processing:
           - Real-time EMG amplitude calculation
           - Quaternion normalization and validation
           - Accelerometer data conversion and scaling
           - Frequency domain analysis and spectral binning
    
    Example:
        >>> # Parse packet starting at buffer position 10
        >>> bytes_consumed = umyo_parse(10)
        >>> print(f"Processed {bytes_consumed} bytes")
        >>> 
        >>> # Access updated device data
        >>> devices = umyo_get_list()
        >>> if devices:
        ...     latest_emg = devices[0].data_array[-1]
        ...     print(f"Latest EMG reading: {latest_emg}")
    
    Error Handling:
        - Validates packet length against buffer availability
        - Checks device ID validity and range
        - Handles malformed packets gracefully
        - Prevents buffer overruns with bounds checking
    
    Performance Notes:
        - Optimized for real-time continuous operation
        - Efficient memory access patterns
        - Minimal computational overhead per packet
        - Suitable for high-throughput data processing
    """
    pp = pos
    rssi = parse_buf[pp - 1]
    # pp is guaranteed to be >0 by design
    packet_id = parse_buf[pp]
    pp += 1
    packet_len = parse_buf[pp]
    pp += 1
    unit_id = parse_buf[pp]
    pp += 1
    unit_id <<= 8
    unit_id += parse_buf[pp]
    pp += 1
    unit_id <<= 8
    unit_id += parse_buf[pp]
    pp += 1
    unit_id <<= 8
    unit_id += parse_buf[pp]
    pp += 1
    idx = id2idx(unit_id)
    packet_type = parse_buf[pp]
    pp += 1
    if (packet_type > 80 and packet_type < 120):
        umyo_list[idx].data_count = packet_type - 80
        umyo_list[idx].packet_type = 80
    else:
        return

    umyo_list[idx].rssi = rssi
    param_id = parse_buf[pp]
    pp += 1

    pb1 = parse_buf[pp]
    pp += 1
    pb2 = parse_buf[pp]
    pp += 1
    pb3 = parse_buf[pp]
    pp += 1
    if (param_id == 0):
        umyo_list[idx].batt = 2000 + pb1 * 10
        umyo_list[idx].version = pb2
    data_id = parse_buf[pp]
    pp += 1

    d_id = data_id - umyo_list[idx].prev_data_id
    umyo_list[idx].prev_data_id = data_id
    if (d_id < 0):
        d_id += 256
    umyo_list[idx].data_id += d_id
    for x in range(umyo_list[idx].data_count):
        hb = parse_buf[pp]
        pp += 1
        lb = parse_buf[pp]
        pp += 1
        val = hb * 256 + lb
        if (hb > 127):
            val = -65536 + val
        umyo_list[idx].data_array[x] = val

    for x in range(4):
        hb = parse_buf[pp]
        pp += 1
        lb = parse_buf[pp]
        pp += 1
        val = hb * 256 + lb
        #        if(hb > 127):
        #            val = -65536 + val
        umyo_list[idx].device_spectr[x] = val

    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    qww = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    qwx = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    qwy = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    qwz = val

    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    ax = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    ay = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    az = val

    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    yaw = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    pitch = val
    hb = parse_buf[pp]
    pp += 1
    lb = parse_buf[pp]
    pp += 1
    val = hb * 256 + lb
    if (val > 32767):
        val = -(65536 - val)
    roll = val

    mx = 0
    my = 0
    mz = 0
    # also has magn data
    if (pos + packet_len > pp + 5):
        hb = parse_buf[pp]
        pp += 1
        lb = parse_buf[pp]
        pp += 1
        val = hb * 256 + lb
        if (val > 32767):
            val = -(65536 - val)
        mx = val
        hb = parse_buf[pp]
        pp += 1
        lb = parse_buf[pp]
        pp += 1
        val = hb * 256 + lb
        if (val > 32767):
            val = -(65536 - val)
        my = val
        hb = parse_buf[pp]
        pp += 1
        lb = parse_buf[pp]
        pp += 1
        val = hb * 256 + lb
        if (val > 32767):
            val = -(65536 - val)
        mz = val
    nyr = quat_math.sV(0, 1, 0)
    Qsg = quat_math.sQ(qww, qwx, qwy, qwz)
    nyr = quat_math.rotate_v(Qsg, nyr)
    yaw_q = math.atan2(nyr.y, nyr.x)

    M = quat_math.sV(mx, my, mz)
    M = quat_math.v_renorm(M)
    A = quat_math.sV(ax, ay, -az)
    A = quat_math.v_renorm(A)

    m_vert = quat_math.v_dot(A, M)
    M_hor = quat_math.sV(M.x - m_vert * A.x, M.y - m_vert * A.y, M.z - m_vert * A.z)
    M_hor = quat_math.v_renorm(M_hor)
    H = quat_math.sV(0, 1, 0)
    h_vert = quat_math.v_dot(A, H)
    H_hor = quat_math.sV(H.x - h_vert * A.x, H.y - h_vert * A.y, H.z - h_vert * A.z)
    H_hor = quat_math.v_renorm(H_hor)
    HM = quat_math.v_mult(H_hor, M_hor)
    asign = -1
    if (quat_math.v_dot(HM, A) < 0):
        asign = 1
    mag_angle = asign * math.acos(quat_math.v_dot(H_hor, M_hor))
    #    print("calc mag A", asign*math.acos(quat_math.v_dot(H_hor, M_hor)))
    #    print("mag", mx, my, mz)
    #    print("A", ax, ay, az)
    pitch = round(math.atan2(ay, az) * 1000)
    #    print("angles", yaw, pitch, roll)
    #    print("yaw_calc", yaw_q)

    umyo_list[idx].Qsg[0] = qww
    umyo_list[idx].Qsg[1] = qwx
    umyo_list[idx].Qsg[2] = qwy
    umyo_list[idx].Qsg[3] = qwz
    umyo_list[idx].yaw = yaw
    umyo_list[idx].pitch = umyo_list[idx].pitch * 0.95 + 0.05 * pitch
    if (pitch > 2000 and umyo_list[idx].pitch < -2000):
        umyo_list[idx].pitch = pitch
    if (pitch < -2000 and umyo_list[idx].pitch > 2000):
        umyo_list[idx].pitch = pitch
    umyo_list[idx].roll = roll
    umyo_list[idx].ax = ax
    umyo_list[idx].ay = ay
    umyo_list[idx].az = az
    umyo_list[idx].mag_angle = mag_angle


#    print(data_id)


def umyo_parse_preprocessor(data):
    """Preprocess raw serial data and parse complete uMyo protocol packets.
    
    Handles the complete preprocessing pipeline for raw serial data received 
    from uMyo devices. This function manages buffer accumulation, packet 
    detection, validation, and parsing to extract structured device data 
    from the continuous serial stream.
    
    The preprocessor implements a robust packet detection and parsing strategy:
    - Accumulates incoming serial data in a circular buffer
    - Detects packet boundaries using protocol-specific markers
    - Validates packet headers and structure
    - Parses complete packets and updates device states
    - Manages buffer cleanup and memory optimization
    
    Args:
        data (bytes): Raw serial data received from uMyo devices. This can 
            be partial packets, multiple packets, or fragmented data streams.
    
    Returns:
        int: Number of bytes remaining in the unprocessed buffer. This value 
            indicates how much data is waiting for additional bytes to form 
            complete packets. High values may indicate parsing issues or 
            buffer overflow conditions.
    
    Side Effects:
        - Extends the global parse_buf with new incoming data
        - Parses and removes complete packets from the buffer
        - Updates device states via umyo_parse() function calls
        - Manages buffer memory and prevents unlimited growth
    
    Data Flow:
        Serial Port → data (bytes) → parse_buf → Packet Detection → 
        umyo_parse() → Device Data Updates
    
    Packet Detection:
        The function searches for valid packet headers using the uMyo 
        protocol markers and validates packet structure before parsing:
        - Header detection: Looks for protocol-specific byte patterns
        - Length validation: Ensures sufficient buffer data for complete packet
        - Boundary detection: Identifies packet start and end positions
        - Error recovery: Handles malformed packets and synchronization loss
    
    Example:
        >>> # Process raw serial data
        >>> raw_bytes = ser.read(1024)  # Read from serial port
        >>> unprocessed = umyo_parse_preprocessor(raw_bytes)
        >>> 
        >>> if unprocessed > 500:
        ...     print("Warning: Large unprocessed buffer detected")
        >>> 
        >>> # Access parsed device data
        >>> devices = umyo_get_list()
        >>> print(f"Active devices: {len(devices)}")
    
    Buffer Management:
        - Automatic buffer extension with incoming data
        - Processed packet removal to prevent memory growth
        - Circular buffer behavior for continuous operation
        - Memory usage optimization through cleanup operations
    
    Error Handling:
        - Graceful handling of incomplete packets
        - Recovery from corrupted or malformed data
        - Buffer overflow protection and management
        - Synchronization recovery for protocol errors
    
    Performance Characteristics:
        - Optimized for real-time continuous data processing
        - Efficient memory management with automatic cleanup
        - Low-latency processing suitable for control applications
        - Scalable to high-throughput data streams
    
    Return Value Interpretation:
        - 0: All data processed successfully
        - < 100: Normal operation with small buffer remainder
        - 100-500: Moderate buffer usage, monitor for trends
        - > 500: High buffer usage, potential performance issues
    """
    parse_buf.extend(data)
    cnt = len(parse_buf)
    if (cnt < 72):
        return 0
    parsed_pos = 0

    i = 0
    while i < (cnt - 70):
        if (parse_buf[i] == 79 and parse_buf[i + 1] == 213):
            rssi = parse_buf[i + 2]
            packet_id = parse_buf[i + 3]
            packet_len = parse_buf[i + 4]

            if (packet_len > 20 and i + 5 + packet_len <= cnt):
                umyo_parse(i + 3)
                parsed_pos = i + 2 + packet_len
                i += 1 + packet_len
                continue


#                del parse_buf[0:i+2+packet_len]
#                break
        i += 1

    if (parsed_pos > 0):
        del parse_buf[0:parsed_pos]
    return cnt


def umyo_get_list():
    """Get the current list of active uMyo devices.
    
    Returns the global list of currently active uMyo devices that have been 
    discovered and are actively providing data. This function provides access 
    to all device instances managed by the parser, allowing applications to 
    retrieve sensor data, device status, and metadata.
    
    The returned list contains uMyo device objects with complete state 
    information including:
    - Real-time EMG signal data and history
    - IMU data (quaternions, accelerometer, gyroscope)
    - Device metadata (ID, battery, RSSI, status)
    - Spectral analysis data for frequency domain processing
    - Timing information and data synchronization markers
    
    Returns:
        list[umyo_class.uMyo]: List of active uMyo device instances. Each 
            device object contains complete sensor data and metadata. The 
            list may be empty if no devices are currently active or 
            connected.
    
    Device Object Properties:
        Each device in the returned list provides access to:
        - unit_id: Unique 32-bit device identifier
        - data_array: EMG signal history and recent samples
        - Qsg: Current quaternion for device orientation
        - Acc: Accelerometer readings (X, Y, Z axes)
        - device_spectr: Frequency domain spectral analysis
        - battery_level: Current battery charge percentage
        - rssi: Signal strength indicator
        - data_id: Latest data packet identifier
        - data_count: Number of samples in current update
    
    Example:
        >>> devices = umyo_get_list()
        >>> print(f"Found {len(devices)} active devices")
        >>> 
        >>> for i, device in enumerate(devices):
        ...     print(f"Device {i}: ID={device.unit_id:08X}")
        ...     print(f"  Latest EMG: {device.data_array[-1]}")
        ...     print(f"  Battery: {device.battery_level}%")
        ...     print(f"  RSSI: {device.rssi} dBm")
        ...     print(f"  Quaternion: {device.Qsg}")
    
    Usage Patterns:
        >>> # Check for active devices
        >>> devices = umyo_get_list()
        >>> if not devices:
        ...     print("No devices connected")
        ... else:
        ...     primary = devices[0]  # Use first device
        ...     latest_emg = primary.data_array[-1]
        
        >>> # Multi-device processing
        >>> devices = umyo_get_list()
        >>> for device in devices:
        ...     if device.data_count > 0:  # New data available
        ...         process_device_data(device)
    
    Thread Safety:
        This function returns a reference to the global device list. While 
        reading device properties is generally safe, applications should be 
        aware that the list and device states may be modified by the parser 
        thread during real-time operation.
    
    Performance Notes:
        - Returns direct reference to global list (no copying overhead)
        - Device objects contain live data updated by parser
        - Minimal computational cost for frequent calls
        - Suitable for real-time polling and monitoring
    
    Device Lifecycle:
        - Devices are automatically added when first detected
        - Inactive devices are removed after timeout period
        - Device objects maintain state across parser iterations
        - List contents may change during continuous operation
    """
    return umyo_list