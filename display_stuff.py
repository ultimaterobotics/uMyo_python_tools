#drawing via pygame

import sys, pygame
pygame.init()

size = width, height = 1200, 500
screen = pygame.display.set_mode(size)

plot_len = 2000
plot_ys = [0]*plot_len
y_scale = 0.3
y_zero = 12000
last_data_id = 0

def draw_cycle():
    global plot_ys, last_data_id, y_zero, y_scale, plot_len
    for event in pygame.event.get():
        if(event.type == pygame.QUIT): sys.exit()
    xy = []
    DX = 10
    DY = height/2
    x_scale = (width - DX*2) / plot_len
    for x in range(plot_len):
        xy.append([DX+x*x_scale, DY+(plot_ys[x]-y_zero)*y_scale])
    screen.fill([0,0,0])
    cl = 0,255,0
    pygame.draw.lines(screen, cl, False, xy)
#    screen.blit(ball, ballrect)
    pygame.display.flip()        

def plot_prepare(devices):
    global plot_ys, last_data_id, y_zero
    cnt = len(devices)
    if(cnt < 1): return
    if(devices[0].data_id != last_data_id):
        for x in range(devices[0].data_count):
            val = devices[0].data_array[x]
            plot_ys.append(val)
            y_zero = 0.997*y_zero + 0.003*val
            
    last_data_id = devices[0].data_id
    if(len(plot_ys) < 2): return
    plot_ys = plot_ys[-plot_len:]
    print(plot_ys[0])
    return devices[0].data_id

