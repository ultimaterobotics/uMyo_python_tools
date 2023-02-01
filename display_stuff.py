#drawing via pygame

import sys, pygame
pygame.init()

max_devices = 64
size = width, height = 1200, 500
screen = pygame.display.set_mode(size)

plot_len = 2000
spg_len = 200
plot_ys = []
plot_spg = []
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
            
        last_data_id[d] = devices[d].data_id
        if(len(plot_ys[d]) < 2): return
        plot_ys[d] = plot_ys[d][-plot_len:]
        plot_spg[d] = plot_spg[d][-spg_len*4:]
#    print(plot_ys[0])
    return devices[0].data_id

