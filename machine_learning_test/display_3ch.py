#drawing via pygame

import sys, pygame
from math import *
pygame.init()

size = width, height = 1200, 500
screen = pygame.display.set_mode(size)

def draw_3ch(ch0, ch1, ch2):
    for event in pygame.event.get():
        if(event.type == pygame.QUIT): sys.exit()
    bsize = 150
    bratio = 3
    DX = 100
    DY = 300
    screen.fill([0,0,0])
    screen.lock()
    bx = DX
    sy = ch0 * bsize
    sx = bsize / bratio
    by = DY - sy
    cl = 0,120,160
    screen.fill(cl,(bx,by,sx,sy))
    bx += 2*sx
    sy = ch1 * bsize
    by = DY - sy
    screen.fill(cl,(bx,by,sx,sy))
    bx += 2*sx
    sy = ch2 * bsize
    by = DY - sy
    screen.fill(cl,(bx,by,sx,sy))
            
#    screen.blit(ball, ballrect)
    screen.unlock()
    pygame.display.flip()        
    return 0


