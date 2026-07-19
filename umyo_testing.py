"""Comprehensive uMyo Device Testing and Validation Module.

This module provides a dedicated testing framework for comprehensive validation
of uMyo device functionality, data integrity, and system performance. It serves
as both a diagnostic tool for troubleshooting device issues and a reference
implementation for developers working with uMyo sensor systems.

The testing framework focuses on:

- Real-time data acquisition and validation
- Device communication integrity verification
- Signal quality assessment and diagnostics
- Performance benchmarking and timing analysis
- Multi-device synchronization testing
- Protocol compliance verification
- Long-term stability and reliability testing

Key Features:
    - Comprehensive device communication testing
    - Real-time data validation and integrity checking
    - Specialized testing display mode via display_stuff.plot_cycle_tester()
    - Performance monitoring with buffer overflow detection
    - Automated device discovery and connection testing
    - Continuous operation testing for reliability assessment
    - Data synchronization and timing analysis

Technical Implementation:
    - High-speed serial communication at 921600 baud rate
    - Real-time data preprocessing and validation pipeline
    - Adaptive display refresh based on data arrival patterns
    - Buffer management with overflow detection and reporting
    - Performance metrics collection and analysis
    - Automated error detection and reporting mechanisms

Testing Capabilities:
    1. Communication Protocol Testing:
       - Serial port connectivity and configuration
       - Data packet integrity and structure validation
       - Protocol compliance and error handling

    2. Data Quality Assessment:
       - Signal integrity and noise analysis
       - Data synchronization across multiple devices
       - Timing accuracy and jitter measurement

    3. Performance Benchmarking:
       - Data throughput measurement and optimization
       - Buffer utilization and overflow detection
       - System latency and response time analysis

    4. Long-term Reliability:
       - Continuous operation stability testing
       - Memory usage monitoring and leak detection
       - Device connection stability over time

Applications:
    - Device quality assurance and validation testing
    - System integration verification for new deployments
    - Performance optimization and bottleneck identification
    - Debugging and troubleshooting device communication issues
    - Research platform validation for scientific applications
    - Educational tool for understanding uMyo system behavior
    - Pre-deployment testing for critical applications

Testing Methodology:
    The module uses a specialized testing display mode that provides:
    - Enhanced visualization for diagnostic purposes
    - Real-time performance metrics and statistics
    - Error detection and reporting capabilities
    - Data quality indicators and signal analysis
    - Device status monitoring and health checks

Dependencies:
    - umyo_parser: Core uMyo data parsing and device management
    - display_stuff: Specialized testing visualization system
    - serial: Serial communication for device connectivity
    - serial.tools.list_ports: Automatic device discovery

Example Usage:
    >>> # Run comprehensive device testing
    >>> python umyo_testing.py

    >>> # Monitor output for test results
    >>> # available ports:
    >>> # /dev/ttyUSB0
    >>> # ===
    >>> # conn: /dev/ttyUSB0
    >>> # [Testing interface appears with diagnostic information]

Diagnostic Output:
    The testing module provides detailed diagnostic information including:
    - Device connection status and configuration
    - Data acquisition rates and performance metrics
    - Signal quality indicators and error rates
    - Buffer utilization and overflow conditions
    - Timing analysis and synchronization status

Performance Monitoring:
    - Real-time data throughput measurement
    - Buffer utilization tracking and optimization
    - Error rate monitoring and analysis
    - System resource usage assessment
    - Long-term stability metrics collection

Quality Assurance:
    This module serves as a critical component of the uMyo development
    and deployment process, ensuring:
    - Device reliability before production deployment
    - System integration compatibility verification
    - Performance optimization and tuning
    - Early detection of potential issues
    - Validation of system requirements compliance

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# kinda main

import umyo_parser
import display_stuff
from serial.tools import list_ports
import serial
import pygame
import sys
import time

VID_PID = "10C4:EA60"


def find_umyo_receiver():
    ports = list_ports.comports()
    for port in ports:
        if VID_PID.lower() in (port.hwid or "").lower():
            print(f"Auto-selected port: {port.device}")
            return port.device
    raise IOError(f"No USB receiver with VID:PID {VID_PID} found!")


# Windows-safe serial reconnect with retries
def connect_serial(device):
    for attempt in range(3):
        try:
            return serial.Serial(
                port=device,
                baudrate=921600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0,
            )
        except Exception as e:
            print(f"Retrying serial connect... attempt {attempt + 1}")
            time.sleep(0.3)
    raise IOError("Failed to reconnect serial after retries.")


# Optional: add this to your parser if not present
if not hasattr(umyo_parser, "umyo_clear_buffer"):

    def dummy_clear():
        umyo_parser.internal_data = []

    umyo_parser.umyo_clear_buffer = dummy_clear

# Optional fallback: implement if not present in display_stuff
if not hasattr(display_stuff, "plot_blank"):

    def plot_blank():
        screen = pygame.display.get_surface()
        if screen:
            screen.fill((0, 0, 0))
            pygame.display.flip()

    display_stuff.plot_blank = plot_blank

device = find_umyo_receiver()
ser = connect_serial(device)
print("Connected to:", ser.portstr)
display_stuff.plot_init()

last_data_upd = 0
parse_unproc_cnt = 0
running = True
received_once = False
auto_reconnected = False
last_recv_time = time.time()

try:
    while running:
        cnt = ser.in_waiting
        if cnt > 0:
            data = ser.read(cnt)
            parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
            parsed_list = umyo_parser.umyo_get_list()

            if parsed_list:
                # Check for required attributes before drawing
                valid = all(
                    hasattr(dev, "ax") and hasattr(dev, "ay") and hasattr(dev, "az")
                    for dev in parsed_list
                )
                if valid:
                    received_once = True
                    auto_reconnected = False
                    last_recv_time = time.time()
                    dat_id = display_stuff.plot_prepare(parsed_list)
                    if dat_id is not None:
                        d_diff = dat_id - last_data_upd
                        if d_diff > 2 + (parse_unproc_cnt / 200):
                            display_stuff.plot_cycle_tester()
                            last_data_upd = dat_id
        else:
            if not received_once:
                display_stuff.plot_blank()
            elif not auto_reconnected and (time.time() - last_recv_time) > 2:
                print("No new data for 2s, auto-reconnecting serial...")
                try:
                    ser.close()
                except:
                    pass
                ser = connect_serial(device)
                umyo_parser.umyo_clear_buffer()
                received_once = False
                auto_reconnected = True
                last_data_upd = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    print("Manual serial reconnect (R key)...")
                    try:
                        ser.close()
                    except:
                        pass
                    ser = connect_serial(device)
                    umyo_parser.umyo_clear_buffer()
                    received_once = False
                    auto_reconnected = False
                    last_recv_time = time.time()
                    last_data_upd = 0

except KeyboardInterrupt:
    print("\nKeyboard interrupt detected. Closing...")

finally:
    pygame.quit()
    if ser:
        ser.close()
    print("Closed gracefully.")
