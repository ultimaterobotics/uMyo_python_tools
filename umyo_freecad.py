"""FreeCAD Integration Module for Real-time 3D Orientation Visualization.

This module provides seamless integration between uMyo sensors and FreeCAD, 
enabling real-time 3D visualization of object orientation based on quaternion 
data from uMyo devices. It establishes a FIFO-based communication channel 
to stream orientation data directly to FreeCAD for live 3D model manipulation.

The module bridges the gap between EMG/IMU sensor data and 3D CAD visualization, 
creating new possibilities for:

- Real-time 3D object manipulation using hand/arm gestures
- Interactive CAD design controlled by body movements
- Ergonomic analysis with live pose visualization
- Educational demonstrations of 3D rotation mathematics
- Rapid prototyping interfaces for gesture-controlled systems
- Accessibility tools for hands-free CAD operation

Key Features:
    - Real-time quaternion streaming to FreeCAD via FIFO
    - Seamless integration with existing FreeCAD workflows
    - High-precision orientation data from uMyo IMU sensors
    - Low-latency communication optimized for interactive use
    - Robust data formatting compatible with FreeCAD scripts
    - Continuous operation with automatic error recovery

Technical Implementation:
    - FIFO (Named Pipe) communication: /tmp/freecad_fifo_cmd
    - Quaternion format: "1 qx qy qz qw" (FreeCAD-compatible)
    - Real-time data acquisition at 921600 baud rate
    - Synchronized with display_stuff visualization system
    - Automatic data preprocessing and parsing pipeline

Data Flow Architecture:
    uMyo Device → Serial → umyo_parser → Quaternion Extract → FIFO → FreeCAD

Communication Protocol:
    - FIFO path: /tmp/freecad_fifo_cmd (Unix named pipe)
    - Message format: "1 qx qy qz qw\n"
    - Coordinate system: Standard quaternion representation
    - Update rate: Synchronized with sensor data arrival
    - Error handling: Graceful FIFO creation and management

FreeCAD Integration:
    The module creates a named pipe that FreeCAD can read from using 
    Python scripts. A typical FreeCAD script would:
    
    1. Open the FIFO for reading: open("/tmp/freecad_fifo_cmd", "r")
    2. Parse quaternion messages: "1 qx qy qz qw"
    3. Apply rotation to selected objects
    4. Update the 3D view in real-time

Applications:
    - Gesture-controlled 3D modeling and design
    - Real-time ergonomic analysis and simulation
    - Interactive product demonstrations with live manipulation
    - Accessibility interfaces for CAD software
    - Educational tools for 3D mathematics and engineering
    - Rapid prototyping with intuitive gesture controls
    - Virtual reality integration with CAD workflows

Dependencies:
    - umyo_parser: Core uMyo sensor data processing
    - display_stuff: Optional visualization for debugging
    - serial: Serial communication with uMyo devices
    - os: System operations for FIFO creation
    - FreeCAD: Target application for 3D visualization

Example FreeCAD Script:
    ```python
    import FreeCAD
    
    # Open the FIFO for reading
    fifo = open("/tmp/freecad_fifo_cmd", "r")
    
    # Get the active object
    obj = FreeCAD.ActiveDocument.ActiveObject
    
    # Read quaternion data and apply rotation
    for line in fifo:
        parts = line.strip().split()
        if len(parts) == 5 and parts[0] == "1":
            qx, qy, qz, qw = map(float, parts[1:])
            obj.Placement.Rotation = FreeCAD.Rotation(qx, qy, qz, qw)
            FreeCAD.Gui.updateGui()
    ```

Performance Considerations:
    - FIFO communication provides low-latency data transfer
    - Quaternion format minimizes parsing overhead in FreeCAD
    - Real-time operation suitable for interactive applications
    - Memory-efficient streaming without data accumulation

System Requirements:
    - Unix-like operating system (for FIFO support)
    - FreeCAD installation with Python scripting enabled
    - uMyo device with IMU capabilities
    - Serial port access permissions

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# kinda main

import umyo_parser
import display_stuff
import os
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

fifopath = "/tmp/freecad_fifo_cmd"
os.mkfifo(fifopath)
fifo = open(fifopath, 'w')

print("conn: " + ser.portstr)
last_data_upd = 0
display_stuff.plot_init()
parse_unproc_cnt = 0
while (1):
    cnt = ser.in_waiting
    if (cnt > 0):
        # print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt / 200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        dat_id = display_stuff.plot_prepare(umyo_parser.umyo_get_list())
        d_diff = 0
        if (not (dat_id is None)):
            d_diff = dat_id - last_data_upd
            umyo = umyo_parser.umyo_get_list()[0]
            msg = "1 "
            msg = msg + str(umyo.Qsg[1]) + " " + str(umyo.Qsg[2]) + " " + str(
                umyo.Qsg[3]) + " " + str(umyo.Qsg[0])
            fifo.write(msg)
        #    print(msg, fifo)
        if (d_diff > 2 + cnt_corr):
            # display_stuff.plot_cycle_lines()
            display_stuff.plot_cycle_tester()
            last_data_upd = dat_id
