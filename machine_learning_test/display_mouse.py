#drawing via pygame

import sys, pygame
from math import *
pygame.init()

size = width, height = 250, 200
screen = pygame.display.set_mode(size)


def draw_arrow(angle):
    cl = 80,155,0
    ref_x = 125
    ref_y = 100
    length = 70
    asize = 20
    x0 = -length/2
    y0 = 0
    x1 = length/2
    y1 = 0
    xa1 = x1 - asize/2
    ya1 = y1 - asize/2
    xb1 = x1 - asize/2
    yb1 = y1 + asize/2
    rx0 = x0 * cos(angle) + y0 * sin(angle) + ref_x
    ry0 = y0 * cos(angle) - x0 * sin(angle) + ref_y
    rx1 = x1 * cos(angle) + y1 * sin(angle) + ref_x
    ry1 = y1 * cos(angle) - x1 * sin(angle) + ref_y
    if(rx1 - rx0 < 2 and rx1 - rx0 > -2): rx1 = rx0
    if(ry1 - ry0 < 2 and ry1 - ry0 > -2): ry1 = ry0
    rxa1 = xa1 * cos(angle) + ya1 * sin(angle) + ref_x
    rya1 = ya1 * cos(angle) - xa1 * sin(angle) + ref_y
    rxb1 = xb1 * cos(angle) + yb1 * sin(angle) + ref_x
    ryb1 = yb1 * cos(angle) - xb1 * sin(angle) + ref_y
    pygame.draw.line(screen, cl, (rx0, ry0), (rx1, ry1), 4)
    pygame.draw.line(screen, cl, (rxa1, rya1), (rx1, ry1), 4)
    pygame.draw.line(screen, cl, (rxb1, ryb1), (rx1, ry1), 4)

def draw_calibrate(stage, progress):
    screen.fill([0,0,0])
    screen.lock()
    cl = 80,155,0
    pygame.draw.line(screen, cl, (20, 170), (20, 190))
    pygame.draw.line(screen, cl, (20, 170), (220, 170))
    pygame.draw.line(screen, cl, (20, 190), (220, 190))
    pygame.draw.line(screen, cl, (220, 170), (220, 190))
    screen.fill(cl,(20, 170, progress*2, 20))    
    screen.unlock()
    cl = 0,255,160
    if(stage == 0):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Keep at center', True, cl)
        screen.blit(img, (70, 30))    
        pygame.draw.circle(screen, cl, (125, 100), 5)
    if(stage == 1):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Move right', True, cl)
        screen.blit(img, (90, 30))
        draw_arrow(0) 
    if(stage == 2 or stage == 4):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Return to center', True, cl)
        screen.blit(img, (70, 30))    
        pygame.draw.circle(screen, cl, (125, 100), 5)
    if(stage == 3):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Move up', True, cl)
        screen.blit(img, (90, 30))
        draw_arrow(3.1415926*0.5) 
    if(stage == 5):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Rotate right', True, cl)
        screen.blit(img, (90, 30))
        size = 70
        cl = 80,155,0
        pygame.draw.arc(screen, cl, (125-size/2, 100-size/2, size, size), 1-0.02*progress, 1.57, 4)
    if(stage == 6):
        font = pygame.font.SysFont(None, 22)
        if(progress > 60):
            img = font.render('Move muscle active', True, cl)
            cl = 200,50,150
            pygame.draw.circle(screen, cl, (125, 100), 30)
        else:
            img = font.render('Move muscle relaxed', True, cl)
            cl = 0,50,50
            pygame.draw.circle(screen, cl, (125, 100), 30)
        screen.blit(img, (70, 30))
    if(stage == 7):
        font = pygame.font.SysFont(None, 22)
        if(progress > 60):
            img = font.render('Click muscle active', True, cl)
            cl = 200,50,150
            pygame.draw.circle(screen, cl, (125, 100), 30)
        else:
            img = font.render('Click muscle relaxed', True, cl)
            cl = 0,50,50
            pygame.draw.circle(screen, cl, (125, 100), 30)
        screen.blit(img, (70, 30))
    pygame.display.flip()

def draw_mouse(m_dx, m_dy, m_r, m_click, ch0, THR0_H, THR0_L, ch1, THR1_H, THR1_L):
    for event in pygame.event.get():
        if(event.type == pygame.QUIT): sys.exit()
    screen.fill([0,0,0])    
        
#draw motion
    c_scale = 20
    c_dx = 100
    c_dy = 100
    cl = 0,255,160
    pygame.draw.line(screen, cl, (c_dx, c_dy), (c_dx + m_dx*c_scale, c_dy - m_dy*c_scale))
#draw scroll 
    screen.lock()
    s_dx = 180
    s_dy = 100
    s_width = 20
    s_scale = 5   
    if(m_r > 0):
        screen.fill(cl,(s_dx, s_dy - m_r*s_scale, s_width, m_r*s_scale))
    else:
        screen.fill(cl,(s_dx, s_dy, s_width, -m_r*s_scale))
#draw muscle levels
    m_dx0 = 5
    ww = 10
    m_dx1 = m_dx0 + 5 + ww
    scale = 0.1
    screen.fill(cl,(m_dx0, 0, ww, ch0*scale))
    pygame.draw.line(screen, (255,0,0), (m_dx0, THR0_L*scale), (m_dx0 + ww, THR0_L*scale))
    pygame.draw.line(screen, (255,0,255), (m_dx0, THR0_H*scale), (m_dx0 + ww, THR0_H*scale))
    screen.fill(cl,(m_dx1, 0, ww, ch1*scale))
    pygame.draw.line(screen, (255,0,0), (m_dx1, THR1_L*scale), (m_dx1 + ww, THR1_L*scale))
    pygame.draw.line(screen, (255,0,255), (m_dx1, THR1_H*scale), (m_dx1 + ww, THR1_H*scale))

#draw click
    cl_dx = 150
    cl_dy = 20
    cl_sz = 20
    if(m_click > 0):
        screen.fill(cl,(cl_dx, cl_dy, cl_sz, cl_sz))
    screen.unlock()
    font = pygame.font.SysFont(None, 22)
    img = font.render('Calibrate', True, cl)
    screen.blit(img, (width-70, height-20))    
    calibrate_requested = 0
    if(pygame.mouse.get_pressed()[0]):
        pos = pygame.mouse.get_pos()
        if(pos[0] > width-70 and pos[1] > height-20):
            calibrate_requested = 1
        print(pos)
    pygame.display.flip()        
    return calibrate_requested



