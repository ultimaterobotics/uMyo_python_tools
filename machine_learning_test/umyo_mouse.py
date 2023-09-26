#kinda main

import umyo_parser
import display_mouse
#import mouse
import pyautogui
from quat_math import *
#import os
import time

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001
# list
from serial.tools import list_ports
port = list(list_ports.comports())
print("available ports:")
for p in port:
    print(p.device)
    device = p.device
print("===")

#read
import serial
ser = serial.Serial(port=device, baudrate=921600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=0)

print("conn: " + ser.portstr)
last_data_upd = 0
parse_unproc_cnt = 0
ch0 = 0
ch1 = 0
avg0 = 0
savg0 = 0
savg1 = 0
zero_Q = sQ(1,0,0,0)
cur_Q = sQ(1,0,0,0)
need_zero_update = 1
rot_X = sV(1,0,0)
rot_Y = sV(0,1,0)
rot_Z = sV(0,0,1)
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

while(1):
    cnt = ser.in_waiting
    if(cnt > 0):
#        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt/200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        umyos = umyo_parser.umyo_get_list()
        if(len(umyos) < 2): continue
        if(need_zero_update > 0):
            zero_Q = sQ(umyos[0].Qsg[0], umyos[0].Qsg[1], umyos[0].Qsg[2], umyos[0].Qsg[3])
            zero_Q = q_renorm(zero_Q)
            need_zero_update = 0
        cur_Q = sQ(umyos[0].Qsg[0], umyos[0].Qsg[1], umyos[0].Qsg[2], umyos[0].Qsg[3])
        cur_Q = q_renorm(cur_Q)
#        mouse.is_pressed("left")
#        print(zero_Q.w, zero_Q.x, zero_Q.y, zero_Q.z)
#        print(cur_Q.w, cur_Q.x, cur_Q.y, cur_Q.z)
        zq_inv = q_make_conj(zero_Q)
        diff_Q = q_mult(cur_Q, zq_inv)
#        print(diff_Q)
        qV = sV(diff_Q.x, diff_Q.y, diff_Q.z)
#        print(diff_Q.w)
        ww = diff_Q.w
        if(diff_Q.w > 1): ww = 1
        qA = math.acos(ww)
        dx = qA * v_dot(rot_X, qV)
        dy = qA * v_dot(rot_Y, qV)
        dr = qA * v_dot(rot_Z, qV)
        dx = umyos[0].yaw
        dy = umyos[0].pitch
        dr = umyos[0].roll
        ddx = dx - prev_dx
        ddy = dy - prev_dy
        ddr = dr - prev_dr
        if(dy > 2000 and prev_dy < -2000): ddy = 0
        if(dy < -2000 and prev_dy > 2000): ddy = 0
#        print(dx, dy, dr)
#        print(ddx, ddy, ddr)
        prev_dx = dx
        prev_dy = dy
        prev_dr = dr
#        d_scale = 3000;
        d_scale = 0.1;
        ddx = -ddx * d_scale * 8
        ddy = ddy * d_scale * 8
        ddr = ddr * d_scale
        ch0 = ch0 * 0.9 + 0.1*(umyos[0].device_spectr[2] + umyos[0].device_spectr[3])
        ch1 = ch1 * 0.9 + 0.1*(umyos[1].device_spectr[2] + umyos[1].device_spectr[3])
        savg0 = savg0 * 0.9 + 0.1 * ch0
        savg1 = savg1 * 0.9 + 0.1 * ch1
        print(savg0, ch1)
        act_ch0 = savg0 #ch0 * (1 - 0.5*ch1 / THR1_H)
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
        
        if(savg0 > fix_TH0 and mouse_sticky_state < 1):
            mouse_sticky_state = 1
            if(mouse_sticky_move < 1): mouse_sticky_move = 1
            else: mouse_sticky_move = 0
        if(savg0 < fix_TH0*0.8): mouse_sticky_state = 0
        if(ch1 > fix_TH1): mouse_click_active = 1
        if(ch1 < fix_TH1 * 0.5):
            mouse_click_active = 0
            clicked = 0
        mouse_move_active = mouse_sticky_move
        mouse_scroll_active = mouse_sticky_move
        print(savg0, mouse_sticky_move, mouse_sticky_state)
        
        if(calibrate_requested == 0):
            if(mouse_scroll_active > 0 and (ddr > 1 or ddr < -1)): 
                pyautogui.scroll(round(-ddr))
#                mouse.wheel(round(ddr))
            if(mouse_move_active > 0 and (ddx > 1 or ddx < -1 or ddy > 1 or ddy < -1)): 
                pyautogui.move(ddx, -ddy)
#                mouse.move(ddx*math.sqrt(math.fabs(ddx)), -ddy*math.sqrt(math.fabs(ddy)), False)
            if(mouse_click_active > 0):
                if(clicked == 0):
                    pyautogui.click()
#                pyautogui.mouseDown()
#                mouse.click("left")
                has_click = 1
                clicked = 1
                
        scale = 1
        T = 300
        avg0 = avg0*0.999 + 0.001*ch0
        if(calibrate_requested > 0):
            calibrate_progress = (time.time() - calibrate_stage_start) * 30
            if(calibrate_progress > 100):
                calibrate_stage = calibrate_stage+1
                calibrate_stage_start = time.time()
                if(calibrate_stage > 7):
                    calibrate_requested = 0
            display_mouse.draw_calibrate(calibrate_stage, calibrate_progress)
            if(calibrate_stage == 0 and calibrate_progress > 60 and calibrate_progress < 70): need_zero_update = 1
            if(calibrate_stage == 1 and calibrate_progress > 80 and calibrate_progress < 90):
                rot_X = v_renorm(qV)
                print(rot_X)
            if(calibrate_stage == 3 and calibrate_progress > 80 and calibrate_progress < 90):
                rot_Y = v_renorm(qV)
                print(rot_Y)
            if(calibrate_stage == 5 and calibrate_progress > 80 and calibrate_progress < 90):
                rot_Z = v_renorm(qV)
                print(rot_Z)
            if(calibrate_stage == 6 and calibrate_progress < 50):
                relaxed_avg0 = ch0
            if(calibrate_stage == 7 and calibrate_progress < 50):
                relaxed_avg1 = ch1
            if(calibrate_stage == 6 and calibrate_progress > 70 and calibrate_progress < 80):
                active_avg0 = savg0
                THR0_H = active_avg0
                THR0_L = relaxed_avg0 + (active_avg0 - relaxed_avg0) * 0.8
            if(calibrate_stage == 7 and calibrate_progress > 70 and calibrate_progress < 80):
                active_avg1 = savg1
                THR1_H = active_avg1 * 1.2
                THR1_L = active_avg1
                print(ch0, relaxed_avg0, active_avg0, ch1, relaxed_avg1, active_avg1)
                print(THR0_H, THR0_L, THR1_H, THR1_L)
                
                
        else:    
            calibrate_requested = display_mouse.draw_mouse(ddx, ddy, ddr, has_click, ch0, THR0_H, THR0_L, ch1, THR1_H, THR1_L)
            if(calibrate_requested > 0):
                calibrate_stage_start = time.time()
                calibrate_stage = 0
