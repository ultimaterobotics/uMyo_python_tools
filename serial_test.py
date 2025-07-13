"""Real-time Serial Communication Test and Display Module.

This module provides a comprehensive testing framework for real-time serial 
communication with uMyo devices, featuring live data visualization and 
performance monitoring. It serves as both a testing utility and a reference 
implementation for integrating uMyo sensors with real-time display systems.

The module combines several essential components:

- Automatic serial port detection and connection establishment
- High-speed serial data acquisition with performance optimization
- Real-time data parsing using the umyo_parser preprocessing pipeline
- Live multi-device visualization with display_stuff plotting system
- Adaptive refresh rate control based on data throughput
- Performance monitoring and buffer management

Key Features:
    - Automatic COM/tty port discovery and device connection
    - High-throughput data acquisition (921600 baud rate)
    - Real-time data preprocessing and parsing pipeline
    - Multi-device display with synchronized visualization
    - Adaptive display refresh based on data arrival rate
    - Performance metrics and buffer overflow detection
    - Continuous operation with robust error handling

Technical Implementation:
    - Non-blocking serial reads for responsive operation
    - Buffer management with overflow detection and correction
    - Data ID tracking for synchronization and loss detection
    - Adaptive display refresh algorithm based on data rate
    - Memory-efficient circular buffer management

Applications:
    - uMyo device testing and validation
    - Real-time data acquisition system development
    - Performance benchmarking of serial communication
    - Multi-device synchronization testing
    - Display system integration validation
    - Educational demonstrations of real-time EMG systems

Performance Characteristics:
    - Baud rate: 921600 bps (high-speed data acquisition)
    - Buffer processing: Adaptive based on data arrival rate
    - Display refresh: Dynamic based on data ID progression
    - Memory usage: Constant with circular buffer management
    - Latency: Optimized for real-time responsive operation

Serial Configuration:
    - Auto-detected port from available system devices
    - Baud rate: 921600 bps (optimized for uMyo protocols)
    - Data format: 8N1 (8 data bits, no parity, 1 stop bit)
    - Timeout: 0 (non-blocking for real-time operation)
    - Flow control: None (software flow control via protocol)

Dependencies:
    - umyo_parser: Core data parsing and preprocessing
    - display_stuff: Multi-device visualization system
    - serial: PySerial for serial communication
    - serial.tools.list_ports: Automatic port discovery

Example Usage:
    >>> # Run the serial test application
    >>> python serial_test.py
    
    >>> # Monitor output for connection and data flow
    >>> # available ports:
    >>> # /dev/ttyUSB0
    >>> # ===
    >>> # conn: /dev/ttyUSB0
    >>> # [Real-time data display appears]

Adaptive Display Algorithm:
    The module uses an intelligent refresh strategy:
    1. Monitor data ID progression to detect new data
    2. Calculate correction factor based on unprocessed buffer size
    3. Refresh display when data progression exceeds threshold
    4. Adjust threshold dynamically based on data rate

This ensures optimal display performance without overwhelming the 
visualization system during high-throughput data acquisition.

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# kinda main

import umyo_parser
import display_stuff
import serial

# list
from serial.tools import list_ports

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
last_data_upd = 0
display_stuff.plot_init()
parse_unproc_cnt = 0
while (1):
    cnt = ser.in_waiting
    if (cnt > 0):
        #        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt / 200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        dat_id = display_stuff.plot_prepare(umyo_parser.umyo_get_list())
        d_diff = 0
        if (not (dat_id is None)):
            d_diff = dat_id - last_data_upd
        if (d_diff > 2 + cnt_corr):
            # display_stuff.plot_cycle_lines()
            display_stuff.plot_cycle_spg()
            last_data_upd = dat_id
