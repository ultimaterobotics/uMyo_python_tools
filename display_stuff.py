#drawing via pygame

import sys, pygame
from math import *
pygame.init()

max_devices = 64
size = width, height = 1200, 500
screen = pygame.display.set_mode(size)

plot_len = 2000
spg_len = 200
plot_ys = []
plot_spg = []
plot_accel = []
plot_Q = []
dev_rssi = [0]*max_devices
dev_batt = [0]*max_devices
dev_mag_angle = [0]*max_devices
y_scale = [0.3]*max_devices
y_zero = [12000]*max_devices
last_data_id = [0]*max_devices
not_updated_cnt = [10000]*max_devices
active_devices = 0

def plot_init():
    global plot_ys, max_devices
    for i in range(max_devices):
        plot_ys.append([0]*plot_len)
        plot_spg.append([0]*spg_len*4)
        plot_accel.append([0]*spg_len*3)
        plot_Q.append([0]*spg_len*4)

def num_to_color(n):
    if(n == 0): return 0, 200, 0
    if(n == 1): return 0, 100, 200
    if(n == 2): return 150, 150, 0
    if(n == 3): return 200, 0, 250
    if(n == 4): return 100, 250, 100
    if(n == 5): return 100, 250, 250
    if(n == 6): return 250, 250, 100
    return 100, 100, 100

def plot_cycle_lines():
    global plot_ys, max_devices, last_data_id, y_zero, y_scale, plot_len, active_devices
    for event in pygame.event.get():
        if(event.type == pygame.QUIT): sys.exit()
    screen.fill([0,0,0])
    cur_devices = 0
    screen.lock()
    for d in range(max_devices):
        if(not_updated_cnt[d] > 1000): continue
        cur_devices += 1
        xy = []
        DX = 10
        DY = height/(1+active_devices) * (d+1)
        x_scale = (width - DX*2) / plot_len
        for x in range(plot_len):
            xy.append([DX+x*x_scale, DY+(plot_ys[d][x]-y_zero[d])*y_scale[d]])
        cl = num_to_color(d)
        
        pygame.draw.lines(screen, cl, False, xy)
#    screen.blit(ball, ballrect)
    screen.unlock()
    pygame.display.flip()        
    active_devices = cur_devices
    return active_devices

def val_to_color(val):
    color_scale = 100
    if(val < 0): val = 0
    tb = 10.0*color_scale*0.01
    tg = 100.0*color_scale*0.01;
    tr = 1000.0*color_scale*0.01;
    wg = tg-tb;
    wr = tr-tg;
    r = 0; g = 0; b = 0;
    if(val < tb):
        r = 10;
        g = 0;
        b = int(val/tb*255);
        return r,g,b
        
    if(val < tg):
        r = 0;
        b = int((tg-val-tb)/wg*255);
        if(b < 0): b = 0
        g = int((val-tb)/wg*255);
        return r,g,b

    if(val < tr):
        b = 0;
        g = int((tr-val-tg)/wr*255);
        if(g < 0): g = 0
        r = int((val-tg)/wr*255);
        return r,g,b

    r = 255;
    g = int(val/tr*2.5);
    b = int(val/tr*25.5);
    if(g > 255): g = 255;
    if(b > 255): b = 255;
    return r,g,b


def plot_cycle_spg():
    global plot_spg, max_devices, last_data_id, spg_len, active_devices
    for event in pygame.event.get():
        if(event.type == pygame.QUIT): sys.exit()
    screen.fill([0,0,0])
    cur_devices = 0
    screen.lock()
    for d in range(max_devices):
        if(not_updated_cnt[d] > 1000): continue
        cur_devices += 1
        DX = 10
        YS = height/6/(active_devices+1)
        DY = height/2 - YS*6*active_devices/2 + YS*6*(cur_devices-1) # (1+active_devices) * (d+1)
        x_scale = (width - DX*2) / spg_len
        for x in range(spg_len):
            for n in range(4):
                bx = DX+x*x_scale
                by = DY+YS*n
                rw = x_scale
                rh = YS
                val = plot_spg[d][x*4+3-n]
                if(n == 3): val *= 0.01
                cl = val_to_color(val)
                screen.fill(cl,(bx,by,rw,rh))
                xy = []
        
        pygame.draw.lines(screen, cl, False, xy)

        
#    screen.blit(ball, ballrect)
    screen.unlock()
    pygame.display.flip()        
    active_devices = cur_devices
    return active_devices

def plot_cycle_tester():
    global plot_spg, max_devices, last_data_id, spg_len, active_devices
    for event in pygame.event.get():
        if(event.type == pygame.QUIT): sys.exit()
    screen.fill([0,0,0])
    cur_devices = 0
    screen.lock()
    for d in range(max_devices):
        if(not_updated_cnt[d] > 1000): continue
        cur_devices += 1
        DX = 10
        YS = height/6/(active_devices+1)
        DY = height/2 - YS*6*active_devices/2 + YS*6*(cur_devices-1) # (1+active_devices) * (d+1)
        x_scale = 0.4*(width - DX*2) / spg_len

        xy = []

        for x in range(spg_len):
            for n in range(4):
                bx = DX+x*x_scale
                by = DY+YS*n
                rw = x_scale
                rh = YS
                val = plot_spg[d][x*4+3-n]
                if(n == 3): val *= 0.01
                cl = val_to_color(val)
                screen.fill(cl,(bx,by,rw,rh))
            gg = plot_accel[d][3*x]*plot_accel[d][3*x] + plot_accel[d][3*x+1]*plot_accel[d][3*x+1] + plot_accel[d][3*x+2]*plot_accel[d][3*x+2]
            gg /= 8192*8129
            gg *= YS
            xy.append([DX+x*x_scale, DY*1.2+gg])

        cl = num_to_color(d)        
        pygame.draw.lines(screen, cl, False, xy)

        DX = 10 + x_scale*spg_len + 10
#        DY = height/2 - YS*6*active_devices/2 + YS*6*(cur_devices-1) # (1+active_devices) * (d+1)
#        DY = height/(1+active_devices) * (d+1)
        x_scale = 0.4*(width - 20) / plot_len
        for x in range(plot_len):
#            xy.append([DX+x*x_scale, DY+(plot_ys[d][x]-y_zero[d])*y_scale[d]])
            xy.append([DX+x*x_scale, DY+(plot_ys[d][x]-0)*height*0.5/32768])
        cl = num_to_color(d)
        pygame.draw.lines(screen, cl, False, xy)

        DX = 10
        

#RSSI drawing        
        xy = []
        xy.append([DX + width*0.05, DY - 30])
        xy.append([DX + width*0.35, DY - 30])
        xy.append([DX + width*0.35, DY - 5])
        xy.append([DX + width*0.05, DY - 5])
        xy.append([DX + width*0.05, DY - 30])
        cl = 255,255,255
        pygame.draw.lines(screen, cl, False, xy)
        
        sig_level = 0
        if(dev_rssi[d] > 1):
            sig_level = (90 - dev_rssi[d])*1.6 #reasonable 0-100 scale
        if(sig_level < 0): sig_level = 0
        if(sig_level > 100): sig_level = 100
        cl = 200,0,0
        if(sig_level > 30): cl = 200,100,0
        if(sig_level > 55): cl = 0,100,150
        if(sig_level > 80): cl = 0,200,0
        
        x_sz = sig_level*0.01 * width*0.3 - 2
        screen.fill(cl,(DX + width*0.05+1,DY - 29,x_sz,23))
        
        mag_angle = 3.1415 - dev_mag_angle[d]
        compass_R = YS*2
        compass_D = 0.1 * compass_R
        compass_cx = DX + width*0.85
        compass_cy = DY + compass_R
        N_x = compass_cx + compass_R * sin(mag_angle)
        N_y = compass_cy + compass_R * cos(mag_angle)
        S_x = compass_cx + compass_R * sin(3.1415 + mag_angle)
        S_y = compass_cy + compass_R * cos(3.1415 + mag_angle)
        E_x = compass_cx + compass_D * sin(3.1415/2 + mag_angle)
        E_y = compass_cy + compass_D * cos(3.1415/2 + mag_angle)
        W_x = compass_cx + compass_D * sin(3*3.1415/2 + mag_angle)
        W_y = compass_cy + compass_D * cos(3*3.1415/2 + mag_angle)
        xy = []
        xy.append([N_x, N_y])
        xy.append([E_x, E_y])
        xy.append([W_x, W_y])
        xy.append([N_x, N_y])
        cl = 0,0,255
        pygame.draw.lines(screen, cl, False, xy)
        xy = []
        xy.append([S_x, S_y])
        xy.append([E_x, E_y])
        xy.append([W_x, W_y])
        xy.append([S_x, S_y])
        cl = 255,0,0
        pygame.draw.lines(screen, cl, False, xy)
        
        batt_perc = (dev_batt[d] - 3100)/10
        if(batt_perc < 0): batt_perc = 0
        batt_dx = DX + width*0.95
        batt_w = width * 0.03
        batt_dy = DY + YS
        batt_h = YS*3
        xy = []
        xy.append([batt_dx, batt_dy])
        xy.append([batt_dx, batt_dy + batt_h])
        xy.append([batt_dx + batt_w, batt_dy + batt_h])
        xy.append([batt_dx + batt_w, batt_dy])
        xy.append([batt_dx, batt_dy])
        cl = 50,150,150
        if(batt_perc < 20): cl = 150,0,0
        pygame.draw.lines(screen, cl, False, xy)
        cl = 0,200,0
        if(batt_perc < 70): cl = 0,100,150
        if(batt_perc < 40): cl = 150,150,0
        if(batt_perc < 15): cl = 255,0,0
        batt_fh = batt_h * batt_perc / 100 - 1
        if(batt_fh < 2): batt_fh = 2
        screen.fill(cl,(batt_dx+1,batt_dy + batt_h - batt_fh - 1, batt_w - 2, batt_fh))
        
        
        
            
#    screen.blit(ball, ballrect)
    screen.unlock()
    pygame.display.flip()        
    active_devices = cur_devices
    return active_devices

def plot_prepare(devices):
    global plot_ys, plot_spg, max_devices, last_data_id, y_zero, active_devices
    for i in range(max_devices): not_updated_cnt[i] += 1
    cnt = len(devices)
    if(cnt < 1): return
    for d in range(cnt):
        if(devices[d].data_id != last_data_id[d]):
            not_updated_cnt[d] = 0
            for n in range(4):
                plot_spg[d].append(devices[d].device_spectr[n])
            for x in range(devices[d].data_count):
                val = devices[d].data_array[x]
                plot_ys[d].append(val)
                y_zero[d] = 0.997*y_zero[d] + 0.003*val
            
            plot_accel[d].append(devices[d].ax)
            plot_accel[d].append(devices[d].ay)
            plot_accel[d].append(devices[d].az)
            plot_Q[d].append(devices[d].Qsg[0])
            plot_Q[d].append(devices[d].Qsg[1])
            plot_Q[d].append(devices[d].Qsg[2])
            plot_Q[d].append(devices[d].Qsg[3])
            
        last_data_id[d] = devices[d].data_id
        if(hasattr(devices[d], 'rssi')):
            dev_rssi[d] = devices[d].rssi
        if(hasattr(devices[d], 'mag_angle')):
            dev_mag_angle[d] = devices[d].mag_angle
        if(hasattr(devices[d], 'batt')):
            dev_batt[d] = devices[d].batt
        if(len(plot_ys[d]) < 2): return
        plot_ys[d] = plot_ys[d][-plot_len:]
        plot_spg[d] = plot_spg[d][-spg_len*4:]
        plot_accel[d] = plot_accel[d][-spg_len*3:]
        plot_Q[d] = plot_Q[d][-spg_len*4:]
#    print(plot_ys[0])
    return devices[0].data_id

