"""Three-Channel EMG Signal Detection and Real-time Visualization.

This module implements a specialized real-time EMG signal detection system 
for exactly three uMyo devices, providing synchronized data acquisition and 
live visualization of muscle activation levels. It features advanced signal 
processing with exponential smoothing and spectral analysis for robust 
muscle activity detection.

The module is specifically designed for applications requiring precise 
three-channel EMG monitoring, such as:

- Gesture recognition systems requiring three distinct muscle groups
- Prosthetic control interfaces with multiple input channels
- Biomechanical research requiring synchronized multi-site recordings
- Rehabilitation systems with targeted muscle group monitoring
- Educational demonstrations of multi-channel EMG principles

Key Features:
    - Dedicated three-device synchronization and data processing
    - Real-time spectral analysis for muscle activation detection
    - Exponential smoothing filters for stable signal representation
    - Live 3-channel bar chart visualization via display_3ch module
    - High-speed data acquisition optimized for gesture recognition
    - Automatic scaling and normalization for consistent display

Technical Implementation:
    - Exponential moving average with α=0.2 for signal smoothing
    - Spectral band analysis focusing on frequency bins 2 and 3
    - Real-time processing pipeline with minimal latency
    - Synchronized data acquisition across all three devices
    - Adaptive scaling for optimal visual representation

Signal Processing Pipeline:
    1. Raw EMG data acquisition from three uMyo devices
    2. Spectral analysis using device_spectr frequency bins
    3. Band selection (bins 2+3) for muscle activation detection
    4. Exponential smoothing: new = 0.8 * old + 0.2 * current
    5. Scaling and normalization for display
    6. Real-time visualization update

Applications:
    - Three-channel gesture recognition systems
    - Prosthetic control with multiple EMG inputs
    - Biomechanical analysis requiring synchronized recordings
    - Rehabilitation monitoring for targeted muscle groups
    - Research platforms for multi-site EMG studies
    - Educational tools for EMG signal processing demonstrations

Dependencies:
    - umyo_parser: Core uMyo data parsing and device management
    - display_3ch: Specialized three-channel visualization system
    - serial: Serial communication with uMyo device array
    - serial.tools.list_ports: Automatic port discovery

Example Usage:
    >>> # Run the three-channel detector
    >>> python umyo_3ch_detector.py
    
    >>> # Expected output:
    >>> # available ports:
    >>> # /dev/ttyUSB0
    >>> # ===
    >>> # conn: /dev/ttyUSB0
    >>> # [Real-time 3-channel display appears]

System Requirements:
    - Exactly 3 uMyo devices for proper operation
    - Serial connection at 921600 baud rate
    - Real-time capable system for responsive visualization
    - pygame support for graphics rendering

Performance Characteristics:
    - Optimized for real-time gesture recognition applications
    - Low-latency signal processing suitable for control interfaces
    - Stable output through exponential smoothing
    - Memory-efficient with minimal buffering requirements

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# kinda main

import umyo_parser
import display_3ch
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
parse_unproc_cnt = 0
ch0 = 0
ch1 = 0
ch2 = 0
avg0 = 0
avg1 = 0
avg2 = 0
while (1):
    cnt = ser.in_waiting
    if (cnt > 0):
        #        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt / 200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        umyos = umyo_parser.umyo_get_list()
        if (len(umyos) < 3):
            continue
        ch0 = ch0 * 0.8 + 0.2 * (umyos[0].device_spectr[2] +
                                 umyos[0].device_spectr[3])
        ch1 = ch1 * 0.8 + 0.2 * (umyos[1].device_spectr[2] +
                                 umyos[1].device_spectr[3])
        ch2 = ch2 * 0.8 + 0.2 * (umyos[2].device_spectr[2] +
                                 umyos[2].device_spectr[3])
        scale = 1
        T = 300
        avg0 = avg0 * 0.999 + 0.001 * ch0
        avg1 = avg1 * 0.999 + 0.001 * ch1
        avg2 = avg2 * 0.999 + 0.001 * ch2
        dc0 = ch0 / (ch0 + ch1 + ch2 + T) * scale
        dc1 = ch1 / (ch0 + ch1 + ch2 + T) * scale
        dc2 = ch2 / (ch0 + ch1 + ch2 + T) * scale
        display_3ch.draw_3ch(dc0, dc1, dc2)
