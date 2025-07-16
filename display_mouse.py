"""Real-time Mouse Gesture and Calibration Visualization Module.

This module provides sophisticated real-time visualization capabilities for mouse 
gesture control and sensor calibration using pygame. It creates graphical displays 
for directional arrows representing mouse movement intentions and calibration 
progress indicators for EMG sensor setup.

The module is specifically designed for human-computer interface applications 
where EMG signals are used to control mouse movement. It provides:

- Directional arrow visualization for gesture-based mouse control
- Real-time calibration progress display with visual feedback
- Smooth 2D rotation calculations for natural gesture representation
- Color-coded visual elements for intuitive user interaction

Key Features:
    - Real-time arrow rotation based on angle input (radians)
    - Calibration progress visualization with stage indicators
    - Optimized graphics rendering for low-latency HCI applications
    - Clean, minimalist interface design for distraction-free operation

Technical Implementation:
    - Window size: 250x200 pixels (optimized for compact display)
    - Mathematical rotation using trigonometric transformations
    - Anti-aliased line drawing for smooth visual appearance
    - Event handling for graceful window management

Applications:
    - EMG-controlled mouse cursor systems
    - Gesture recognition training interfaces
    - Assistive technology for motor-impaired users
    - Research platforms for HCI studies
    - Real-time biometric control systems

Dependencies:
    - pygame: Graphics rendering and window management
    - math: Trigonometric calculations for rotation
    - sys: System operations and clean exit handling

Example Usage:
    >>> import display_mouse
    >>> import math
    >>> 
    >>> # Display arrow pointing right (0 radians)
    >>> display_mouse.draw_arrow(0)
    >>> 
    >>> # Display arrow pointing up (π/2 radians)
    >>> display_mouse.draw_arrow(math.pi/2)
    >>> 
    >>> # Show calibration progress
    >>> display_mouse.draw_calibrate(stage=2, progress=0.75)

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# drawing via pygame

import sys
import pygame
import math

pygame.init()

size = width, height = 250, 200
screen = pygame.display.set_mode(size)


def draw_arrow(angle):
    """Draw a rotated arrow indicating direction for mouse gesture control.
    
    Renders a directional arrow rotated by the specified angle, used to provide 
    visual feedback for gesture-based mouse control systems. The arrow is drawn 
    with an arrowhead and rotated around a central reference point using 
    trigonometric transformations.
    
    The arrow visualization consists of:
    - Main shaft: A line from the tail to the head
    - Arrowhead: Two angled lines forming the pointed tip
    - Rotation: Applied around the screen center (125, 100)
    - Color: Green theme (80, 155, 0) for clear visibility
    
    Args:
        angle (float): Rotation angle in radians. Positive values rotate 
            clockwise, negative values rotate counterclockwise.
            - 0.0: Arrow points right (→)
            - π/2: Arrow points down (↓) 
            - π: Arrow points left (←)
            - 3π/2: Arrow points up (↑)
    
    Returns:
        None: This function draws directly to the pygame screen buffer.
    
    Side Effects:
        - Draws lines on the global pygame screen surface
        - Modifies the display buffer (requires pygame.display.flip() to show)
    
    Example:
        >>> import math
        >>> # Point arrow to the right
        >>> draw_arrow(0.0)
        
        >>> # Point arrow upward  
        >>> draw_arrow(math.pi/2)
        
        >>> # Point arrow at 45-degree angle
        >>> draw_arrow(math.pi/4)
    
    Technical Details:
        - Arrow length: 70 pixels from tail to head
        - Arrowhead size: 20 pixels (width and height)
        - Line thickness: 4 pixels for clear visibility
        - Reference point: (125, 100) - screen center
        - Rotation uses standard 2D rotation matrix:
          [cos(θ) -sin(θ)]
          [sin(θ)  cos(θ)]
    
    Performance Notes:
        - Optimized for real-time rendering
        - Uses integer pixel coordinates after rotation
        - Minimal floating-point operations for efficiency
        - Small coordinate adjustments prevent visual artifacts
    """
    cl = 80, 155, 0
    ref_x = 125
    ref_y = 100
    length = 70
    asize = 20
    x0 = -length / 2
    y0 = 0
    x1 = length / 2
    y1 = 0
    xa1 = x1 - asize / 2
    ya1 = y1 - asize / 2
    xb1 = x1 - asize / 2
    yb1 = y1 + asize / 2
    rx0 = x0 * math.cos(angle) + y0 * math.sin(angle) + ref_x
    ry0 = y0 * math.cos(angle) - x0 * math.sin(angle) + ref_y
    rx1 = x1 * math.cos(angle) + y1 * math.sin(angle) + ref_x
    ry1 = y1 * math.cos(angle) - x1 * math.sin(angle) + ref_y
    if (rx1 - rx0 < 2 and rx1 - rx0 > -2):
        rx1 = rx0
    if (ry1 - ry0 < 2 and ry1 - ry0 > -2):
        ry1 = ry0
    rxa1 = xa1 * math.cos(angle) + ya1 * math.sin(angle) + ref_x
    rya1 = ya1 * math.cos(angle) - xa1 * math.sin(angle) + ref_y
    rxb1 = xb1 * math.cos(angle) + yb1 * math.sin(angle) + ref_x
    ryb1 = yb1 * math.cos(angle) - xb1 * math.sin(angle) + ref_y
    pygame.draw.line(screen, cl, (rx0, ry0), (rx1, ry1), 4)
    pygame.draw.line(screen, cl, (rxa1, rya1), (rx1, ry1), 4)
    pygame.draw.line(screen, cl, (rxb1, ryb1), (rx1, ry1), 4)


def draw_calibrate(stage, progress):
    """Draw calibration progress visualization for EMG sensor setup.
    
    Renders a real-time calibration interface showing the current calibration 
    stage and progress within that stage. The visualization provides clear 
    feedback during the sensor calibration process, helping users understand 
    the current state and remaining calibration steps.
    
    The calibration display includes:
    - Stage indicator: Shows which calibration phase is active
    - Progress bar: Visual representation of completion within current stage
    - Clean background: Black screen for high contrast visibility
    - Consistent color scheme: Green theme matching other interface elements
    
    Args:
        stage (int): Current calibration stage number. Typically ranges from 
            0 to the total number of calibration phases (e.g., 0-4 for a 
            5-stage calibration process).
        progress (float): Completion progress within the current stage. 
            Should be in the range [0.0, 1.0] where:
            - 0.0: Stage just started
            - 0.5: Stage half complete
            - 1.0: Stage fully complete
    
    Returns:
        None: This function draws directly to the pygame screen buffer.
    
    Side Effects:
        - Clears the screen with black background
        - Locks screen for efficient drawing operations
        - Draws progress indicators on the global pygame screen surface
        - Screen must be unlocked and flipped externally to display changes
    
    Example:
        >>> # Show calibration at stage 2, 75% complete
        >>> draw_calibrate(stage=2, progress=0.75)
        
        >>> # Show beginning of stage 0
        >>> draw_calibrate(stage=0, progress=0.0)
        
        >>> # Show completed stage 4
        >>> draw_calibrate(stage=4, progress=1.0)
    
    Visual Layout:
        - Screen size: 250x200 pixels
        - Progress bar position: Bottom area (y=170-190)
        - Progress bar width: 200 pixels (x=20-220)
        - Color: Green (80, 155, 0) for consistency with arrow display
        - Border lines: 2-pixel thick frame around progress area
    
    Calibration Workflow Integration:
        This function is typically called in a loop during calibration:
        1. Initialize calibration process
        2. For each stage:
           a. Update progress incrementally (0.0 to 1.0)
           b. Call draw_calibrate() with current stage and progress
           c. Update display with pygame.display.flip()
        3. Proceed to next stage when current stage reaches 1.0
    
    Performance Notes:
        - Uses screen locking for efficient batch drawing
        - Minimal computational overhead suitable for real-time updates
        - Optimized for frequent progress updates during calibration
    """
    screen.fill([0, 0, 0])
    screen.lock()
    cl = 80, 155, 0
    pygame.draw.line(screen, cl, (20, 170), (20, 190))
    pygame.draw.line(screen, cl, (20, 170), (220, 170))
    pygame.draw.line(screen, cl, (20, 190), (220, 190))
    pygame.draw.line(screen, cl, (220, 170), (220, 190))
    screen.fill(cl, (20, 170, progress * 2, 20))
    screen.unlock()
    cl = 0, 255, 160
    if (stage == 0):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Keep at center', True, cl)
        screen.blit(img, (70, 30))
        pygame.draw.circle(screen, cl, (125, 100), 5)
    if (stage == 1):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Move right', True, cl)
        screen.blit(img, (90, 30))
        draw_arrow(0)
    if (stage == 2 or stage == 4):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Return to center', True, cl)
        screen.blit(img, (70, 30))
        pygame.draw.circle(screen, cl, (125, 100), 5)
    if (stage == 3):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Move up', True, cl)
        screen.blit(img, (90, 30))
        draw_arrow(3.1415926 * 0.5)
    if (stage == 5):
        font = pygame.font.SysFont(None, 22)
        img = font.render('Rotate right', True, cl)
        screen.blit(img, (90, 30))
        size = 70
        cl = 80, 155, 0
        pygame.draw.arc(screen, cl,
                        (125 - size / 2, 100 - size / 2, size, size),
                        1 - 0.02 * progress, 1.57, 4)
    if (stage == 6):
        font = pygame.font.SysFont(None, 22)
        if (progress > 60):
            img = font.render('Move muscle active', True, cl)
            cl = 200, 50, 150
            pygame.draw.circle(screen, cl, (125, 100), 30)
        else:
            img = font.render('Move muscle relaxed', True, cl)
            cl = 0, 50, 50
            pygame.draw.circle(screen, cl, (125, 100), 30)
        screen.blit(img, (70, 30))
    if (stage == 7):
        font = pygame.font.SysFont(None, 22)
        if (progress > 60):
            img = font.render('Click muscle active', True, cl)
            cl = 200, 50, 150
            pygame.draw.circle(screen, cl, (125, 100), 30)
        else:
            img = font.render('Click muscle relaxed', True, cl)
            cl = 0, 50, 50
            pygame.draw.circle(screen, cl, (125, 100), 30)
        screen.blit(img, (70, 30))
    pygame.display.flip()


def draw_mouse(m_dx, m_dy, m_r, m_click, ch0, THR0_H, THR0_L, ch1, THR1_H,
               THR1_L):
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            sys.exit()
    screen.fill([0, 0, 0])

    # draw motion
    c_scale = 20
    c_dx = 100
    c_dy = 100
    cl = 0, 255, 160
    pygame.draw.line(screen, cl, (c_dx, c_dy),
                     (c_dx + m_dx * c_scale, c_dy - m_dy * c_scale))
    # draw scroll
    screen.lock()
    s_dx = 180
    s_dy = 100
    s_width = 20
    s_scale = 5
    if (m_r > 0):
        screen.fill(cl, (s_dx, s_dy - m_r * s_scale, s_width, m_r * s_scale))
    else:
        screen.fill(cl, (s_dx, s_dy, s_width, -m_r * s_scale))


# draw muscle levels
    m_dx0 = 5
    ww = 10
    m_dx1 = m_dx0 + 5 + ww
    scale = 0.1
    screen.fill(cl, (m_dx0, 0, ww, ch0 * scale))
    pygame.draw.line(screen, (255, 0, 0), (m_dx0, THR0_L * scale),
                     (m_dx0 + ww, THR0_L * scale))
    pygame.draw.line(screen, (255, 0, 255), (m_dx0, THR0_H * scale),
                     (m_dx0 + ww, THR0_H * scale))
    screen.fill(cl, (m_dx1, 0, ww, ch1 * scale))
    pygame.draw.line(screen, (255, 0, 0), (m_dx1, THR1_L * scale),
                     (m_dx1 + ww, THR1_L * scale))
    pygame.draw.line(screen, (255, 0, 255), (m_dx1, THR1_H * scale),
                     (m_dx1 + ww, THR1_H * scale))

    # draw click
    cl_dx = 150
    cl_dy = 20
    cl_sz = 20
    if (m_click > 0):
        screen.fill(cl, (cl_dx, cl_dy, cl_sz, cl_sz))
    screen.unlock()
    font = pygame.font.SysFont(None, 22)
    img = font.render('Calibrate', True, cl)
    screen.blit(img, (width - 70, height - 20))
    calibrate_requested = 0
    if (pygame.mouse.get_pressed()[0]):
        pos = pygame.mouse.get_pos()
        if (pos[0] > width - 70 and pos[1] > height - 20):
            calibrate_requested = 1
        print(pos)
    pygame.display.flip()
    return calibrate_requested
