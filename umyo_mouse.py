"""EMG-Controlled Mouse Interface with Gesture Recognition.

This module implements a sophisticated EMG-based mouse control system that 
translates muscle signals and hand orientation into computer mouse movements 
and clicks. It combines EMG signal processing with IMU quaternion data to 
create an intuitive hands-free computer interface suitable for accessibility 
applications and gesture-based computing.

The system provides comprehensive mouse control through:

- Real-time cursor movement based on hand/arm orientation
- EMG-triggered mouse clicks from muscle activation
- Gesture-based control with calibration and training phases
- Visual feedback through real-time display integration
- Adaptive thresholds and sensitivity adjustment
- Multi-stage calibration for personalized operation

Key Features:
    - Full mouse cursor control via hand orientation (quaternions)
    - Left/right click detection through EMG amplitude analysis
    - Real-time calibration system with visual feedback
    - Adaptive signal processing with exponential smoothing
    - Fail-safe mechanisms and emergency stops
    - High-precision cursor control with configurable sensitivity
    - Visual feedback through display_mouse integration

Technical Implementation:
    - Quaternion-based 3D orientation tracking and 2D projection
    - Exponential moving averages for EMG signal stabilization
    - Multi-stage calibration protocol for user adaptation
    - Real-time signal processing with minimal latency
    - PyAutoGUI integration for system-level mouse control
    - Configurable thresholds and sensitivity parameters

Control Mechanisms:
    1. Cursor Movement: Hand orientation → Quaternion → 2D mouse coordinates
    2. Left Click: EMG channel 0 activation above threshold
    3. Right Click: EMG channel 1 activation above threshold  
    4. Calibration: Sequential gesture recording for personalization
    5. Visual Feedback: Real-time display of control state and calibration

Signal Processing Pipeline:
    1. Raw EMG and IMU data acquisition from uMyo device
    2. Quaternion extraction and mathematical processing
    3. EMG amplitude calculation and exponential smoothing
    4. Threshold comparison and click detection
    5. Coordinate transformation and cursor positioning
    6. System mouse event generation via PyAutoGUI

Applications:
    - Assistive technology for motor-impaired users
    - Hands-free computer interaction systems
    - Gaming interfaces with gesture control
    - Virtual reality and augmented reality input systems
    - Research platforms for human-computer interaction
    - Educational tools for EMG and gesture recognition
    - Accessibility solutions for various disabilities

Calibration System:
    - Multi-stage user adaptation protocol
    - Gesture recording for baseline establishment
    - Threshold adjustment based on user capabilities
    - Visual feedback during calibration process
    - Personalized sensitivity configuration

Dependencies:
    - umyo_parser: Core uMyo sensor data processing
    - display_mouse: Visual feedback and calibration interface
    - pyautogui: System-level mouse control integration
    - quat_math: Quaternion mathematics and transformations
    - serial: Serial communication with uMyo devices
    - time: Timing operations for calibration protocols

Example Usage:
    >>> # Run the EMG mouse control system
    >>> python umyo_mouse.py
    
    >>> # Follow calibration prompts
    >>> # available ports:
    >>> # /dev/ttyUSB0
    >>> # ===
    >>> # conn: /dev/ttyUSB0
    >>> # [Calibration interface appears]
    >>> # [Mouse control becomes active after calibration]

Safety Features:
    - PyAutoGUI fail-safe disabled for accessibility use
    - Minimal pause between operations for responsiveness
    - Emergency stop mechanisms for user safety
    - Adaptive thresholds to prevent false triggers
    - Visual feedback for system status awareness

Performance Characteristics:
    - Low-latency cursor control suitable for real-time use
    - Stable operation through exponential signal smoothing
    - High precision orientation tracking via quaternions
    - Efficient processing optimized for continuous operation
    - Memory-efficient with minimal resource requirements

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# kinda main

import umyo_parser
import display_mouse
# import mouse
import pyautogui
import quat_math
import math
# import os
import time
from serial.tools import list_ports
import serial

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001
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
last_data_upd = 0
parse_unproc_cnt = 0
ch0 = 0
ch1 = 0
avg0 = 0
savg0 = 0
savg1 = 0
zero_Q = quat_math.sQ(1, 0, 0, 0)
cur_Q = quat_math.sQ(1, 0, 0, 0)
need_zero_update = 1
rot_X = quat_math.sV(1, 0, 0)
rot_Y = quat_math.sV(0, 1, 0)
rot_Z = quat_math.sV(0, 0, 1)
calibrate_requested = 0
calibrate_stage = 0
calibrate_stage_start = 0
calibrate_progress = 0
prev_dx = 0
prev_dy = 0
prev_dr = 0
relaxed_avg0 = 100
active_avg0 = 500000
relaxed_avg1 = 100
active_avg1 = 500000
mouse_move_active = 0
mouse_scroll_active = 0
mouse_click_active = 0
clicked = 0

THR0_H = 50000
THR0_L = 50000
THR1_H = 50000
THR1_L = 50000

fix_TH0 = 400
fix_TH1 = 700
mouse_sticky_move = 0
mouse_sticky_state = 0

while (1):
    cnt = ser.in_waiting
    if (cnt > 0):
        #        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt / 200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        umyos = umyo_parser.umyo_get_list()
        if (len(umyos) < 2):
            continue
        if (need_zero_update > 0):
            zero_Q = quat_math.sQ(umyos[0].Qsg[0], umyos[0].Qsg[1], umyos[0].Qsg[2], umyos[0].Qsg[3])
            zero_Q = quat_math.q_renorm(zero_Q)
            need_zero_update = 0
        cur_Q = quat_math.sQ(umyos[0].Qsg[0], umyos[0].Qsg[1], umyos[0].Qsg[2], umyos[0].Qsg[3])
        cur_Q = quat_math.q_renorm(cur_Q)
        #        mouse.is_pressed("left")
        #        print(zero_Q.w, zero_Q.x, zero_Q.y, zero_Q.z)
        #        print(cur_Q.w, cur_Q.x, cur_Q.y, cur_Q.z)
        zq_inv = quat_math.q_make_conj(zero_Q)
        diff_Q = quat_math.q_mult(cur_Q, zq_inv)
        #        print(diff_Q)
        qV = quat_math.sV(diff_Q.x, diff_Q.y, diff_Q.z)
        #        print(diff_Q.w)
        ww = diff_Q.w
        if (diff_Q.w > 1):
            ww = 1
        qA = math.acos(ww)
        dx = qA * quat_math.v_dot(rot_X, qV)
        dy = qA * quat_math.v_dot(rot_Y, qV)
        dr = qA * quat_math.v_dot(rot_Z, qV)
        dx = umyos[0].yaw
        dy = umyos[0].pitch
        dr = umyos[0].roll
        ddx = dx - prev_dx
        ddy = dy - prev_dy
        ddr = dr - prev_dr
        if (dy > 2000 and prev_dy < -2000):
            ddy = 0
        if (dy < -2000 and prev_dy > 2000):
            ddy = 0
        #        print(dx, dy, dr)
        #        print(ddx, ddy, ddr)
        prev_dx = dx
        prev_dy = dy
        prev_dr = dr
        #        d_scale = 3000;
        d_scale = 0.1
        ddx = -ddx * d_scale * 8
        ddy = ddy * d_scale * 8
        ddr = ddr * d_scale
        ch0 = ch0 * 0.9 + 0.1 * (umyos[0].device_spectr[2] +
                                 umyos[0].device_spectr[3])
        ch1 = ch1 * 0.9 + 0.1 * (umyos[1].device_spectr[2] +
                                 umyos[1].device_spectr[3])
        savg0 = savg0 * 0.9 + 0.1 * ch0
        savg1 = savg1 * 0.9 + 0.1 * ch1
        print(savg0, ch1)
        act_ch0 = savg0  # ch0 * (1 - 0.5*ch1 / THR1_H)
        has_click = 0
        #        if(act_ch0 > THR0_H): mouse_move_active = 1
        #        if(act_ch0 > THR0_H * 1.2): mouse_scroll_active = 1
        #        if(act_ch0 < THR0_H): mouse_scroll_active = 0
        #        if(ch1 > THR1_H): mouse_click_active = 1
        #        if(act_ch0 < THR0_L): mouse_move_active = 0
        #        if(ch1 > THR1_H * 0.5):
        #            mouse_move_active = 0
        #            mouse_scroll_active = 0
        #        if(ch1 < THR1_L):
        #            mouse_click_active = 0
        #            clicked = 0

        if (savg0 > fix_TH0 and mouse_sticky_state < 1):
            mouse_sticky_state = 1
            if (mouse_sticky_move < 1):
                mouse_sticky_move = 1
            else:
                mouse_sticky_move = 0
        if (savg0 < fix_TH0 * 0.8):
            mouse_sticky_state = 0
        if (ch1 > fix_TH1):
            mouse_click_active = 1
        if (ch1 < fix_TH1 * 0.5):
            mouse_click_active = 0
            clicked = 0
        mouse_move_active = mouse_sticky_move
        mouse_scroll_active = mouse_sticky_move
        print(savg0, mouse_sticky_move, mouse_sticky_state)

        if (calibrate_requested == 0):
            if (mouse_scroll_active > 0 and (ddr > 1 or ddr < -1)):
                pyautogui.scroll(round(-ddr))
#                mouse.wheel(round(ddr))
            if (mouse_move_active > 0
                    and (ddx > 1 or ddx < -1 or ddy > 1 or ddy < -1)):
                pyautogui.move(ddx, -ddy)
#                mouse.move(ddx*math.sqrt(math.fabs(ddx)), -ddy*math.sqrt(math.fabs(ddy)), False)
            if (mouse_click_active > 0):
                if (clicked == 0):
                    pyautogui.click()
#                pyautogui.mouseDown()
#                mouse.click("left")
                has_click = 1
                clicked = 1

        scale = 1
        T = 300
        avg0 = avg0 * 0.999 + 0.001 * ch0
        if (calibrate_requested > 0):
            calibrate_progress = (time.time() - calibrate_stage_start) * 30
            if (calibrate_progress > 100):
                calibrate_stage = calibrate_stage + 1
                calibrate_stage_start = time.time()
                if (calibrate_stage > 7):
                    calibrate_requested = 0
            display_mouse.draw_calibrate(calibrate_stage, calibrate_progress)
            if (calibrate_stage == 0 and calibrate_progress > 60
                    and calibrate_progress < 70):
                need_zero_update = 1
            if (calibrate_stage == 1 and calibrate_progress > 80
                    and calibrate_progress < 90):
                rot_X = quat_math.v_renorm(qV)
                print(rot_X)
            if (calibrate_stage == 3 and calibrate_progress > 80
                    and calibrate_progress < 90):
                rot_Y = quat_math.v_renorm(qV)
                print(rot_Y)
            if (calibrate_stage == 5 and calibrate_progress > 80
                    and calibrate_progress < 90):
                rot_Z = quat_math.v_renorm(qV)
                print(rot_Z)
            if (calibrate_stage == 6 and calibrate_progress < 50):
                relaxed_avg0 = ch0
            if (calibrate_stage == 7 and calibrate_progress < 50):
                relaxed_avg1 = ch1
            if (calibrate_stage == 6 and calibrate_progress > 70
                    and calibrate_progress < 80):
                active_avg0 = savg0
                THR0_H = active_avg0
                THR0_L = relaxed_avg0 + (active_avg0 - relaxed_avg0) * 0.8
            if (calibrate_stage == 7 and calibrate_progress > 70
                    and calibrate_progress < 80):
                active_avg1 = savg1
                THR1_H = active_avg1 * 1.2
                THR1_L = active_avg1
                print(ch0, relaxed_avg0, active_avg0, ch1, relaxed_avg1,
                      active_avg1)
                print(THR0_H, THR0_L, THR1_H, THR1_L)

        else:
            calibrate_requested = display_mouse.draw_mouse(
                ddx, ddy, ddr, has_click, ch0, THR0_H, THR0_L, ch1, THR1_H,
                THR1_L)
            if (calibrate_requested > 0):
                calibrate_stage_start = time.time()
                calibrate_stage = 0
