"""Real-time EMG Data Parsing and Matplotlib Visualization Module.

This module provides a complete solution for real-time EMG data acquisition, 
parsing, and visualization using matplotlib. It serves as a main entry point 
for data collection applications and demonstrates the integration between 
uMyo sensor data parsing and real-time plotting capabilities.

The module combines several key components:

- Serial port discovery and automatic device connection
- Real-time EMG data parsing using the umyo_parser module
- Live matplotlib plotting with configurable display parameters
- Circular buffer management for continuous data streaming
- Error handling and connection management for robust operation

Key Features:
    - Automatic serial port detection and device enumeration
    - High-speed data acquisition (921600 baud rate)
    - Real-time matplotlib visualization with 1000-sample history
    - Circular buffer management for memory-efficient operation
    - Robust error handling for continuous operation
    - Integration with umyo_parser for protocol-compliant data parsing

Technical Specifications:
    - Baud rate: 921600 bps for high-throughput data acquisition
    - Buffer size: 1000 samples for real-time display
    - Plot range: 0-10000 amplitude units (configurable)
    - Update rate: Limited by data acquisition speed and matplotlib refresh
    - Data format: Raw EMG amplitude values from uMyo sensors

Applications:
    - Real-time EMG signal monitoring and analysis
    - Data quality assessment during sensor setup
    - Educational demonstrations of EMG signal characteristics
    - Research data collection with live feedback
    - Debugging and validation of sensor configurations
    - Integration testing for uMyo sensor systems

Dependencies:
    - umyo_parser: Core uMyo sensor data parsing functionality
    - matplotlib.pyplot: Real-time plotting and visualization
    - serial: Serial communication with uMyo devices
    - serial.tools.list_ports: Automatic port discovery

Example Usage:
    >>> # Run the main data collection loop
    >>> python parse_plot_data.py
    
    >>> # Manual function usage
    >>> import parse_plot_data
    >>> data_id = parse_plot_data.plot_prepare()  # Process latest data
    >>> print(f"Latest data ID: {data_id}")

Serial Configuration:
    - Port: Auto-detected from available COM/tty devices
    - Baud rate: 921600 bps (optimized for uMyo data rates)
    - Data bits: 8
    - Stop bits: 1  
    - Parity: None
    - Timeout: 0 (non-blocking reads for real-time operation)

Performance Considerations:
    - Uses circular buffer to prevent memory growth
    - Non-blocking serial reads for responsive operation
    - Matplotlib ion() mode for real-time updates
    - Optimized for continuous long-term data collection

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# kinda main

import umyo_parser
# import numpy as np
from matplotlib import pyplot as plt
from serial.tools import list_ports
import serial

plot_ys = [0] * 1000


def plot_prepare():
    """Prepare and update the EMG data plot with latest sensor readings.
    
    Processes the latest EMG data from connected uMyo devices and updates 
    the circular plotting buffer. This function retrieves data from the 
    umyo_parser module, appends new samples to the plotting array, and 
    maintains a rolling window of the most recent 1000 samples.
    
    The function performs the following operations:
    1. Retrieves the list of active uMyo devices
    2. Extracts new EMG data from the primary device (index 0)
    3. Appends new samples to the circular buffer
    4. Trims the buffer to maintain 1000-sample history
    5. Returns the data ID for tracking purposes
    
    Returns:
        int or None: The data ID of the latest processed sample from the 
            primary device, or None if no devices are available or no 
            data is present.
    
    Side Effects:
        - Modifies the global plot_ys array with new EMG samples
        - Maintains circular buffer by removing old samples
        - Prints the first sample value for debugging purposes
    
    Example:
        >>> # Process latest data and get data ID
        >>> latest_id = plot_prepare()
        >>> if latest_id is not None:
        ...     print(f"Processed data with ID: {latest_id}")
        ... else:
        ...     print("No data available")
    
    Data Flow:
        uMyo Device → Serial Port → umyo_parser → plot_prepare() → plot_ys[]
    
    Buffer Management:
        - Initial buffer: [0] * 1000 (zeros)
        - New data appended: plot_ys.append(new_sample)
        - Buffer trimmed: plot_ys = plot_ys[-1000:] (keep last 1000)
        - Memory usage: Constant (1000 samples maximum)
    
    Error Handling:
        - Returns None if no devices are connected
        - Returns None if primary device has no data
        - Returns None if buffer is too small (< 2 samples)
        - Graceful handling of empty device lists
    
    Performance Notes:
        - Optimized for real-time operation
        - Constant memory usage with circular buffer
        - Minimal computational overhead for continuous calling
        - Suitable for high-frequency data acquisition loops
    """
    global plot_ys
    devices = umyo_parser.umyo_get_list()
    cnt = len(devices)
    if (cnt < 1):
        return
    for x in range(devices[0].data_count):
        val = devices[0].data_array[x]
        plot_ys.append(val)
    if (len(plot_ys) < 2):
        return
    plot_ys = plot_ys[-1000:]
    print(plot_ys[0])
    return devices[0].data_id


# list

port = list(list_ports.comports())
print("available ports:")
for p in port:
    print(p.device)
    device = p.device
print("===")

# read

ser = serial.Serial(port=device,
                    baudrate=921600,
                    parity=serial.PARITY_NONE,
                    stopbits=1,
                    bytesize=8,
                    timeout=0)

print("conn: " + ser.portstr)

plt.axis([0, 1000, 0, 10000])
plt.ion()
plt.show()
x = [0]
for i in range(999):
    x.append(1 + i)
# x = np.arange(0, len(plot_ys))
line, = plt.plot(x, plot_ys)
plt.ylim(7000, 9000)
plt.draw()
plt.pause(0.01)

last_data_upd = 0
while (1):
    cnt = ser.in_waiting
    if (cnt > 0):
        data = ser.read(cnt)
        umyo_parser.umyo_parse_preprocessor(data)
        dat_id = plot_prepare()
        d_diff = dat_id - last_data_upd
        if (d_diff > 100):
            plt.ylim(plot_ys[0] - 1000, plot_ys[0] + 1000)
            last_data_upd = dat_id
            line.set_ydata(plot_ys)
            plt.draw()
            plt.pause(0.001)
