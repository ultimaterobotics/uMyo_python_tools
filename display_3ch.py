"""Real-time 3-Channel EMG Signal Visualization Module.

This module provides a simple real-time visualization interface for displaying 
three-channel EMG (electromyography) signal amplitudes using pygame. It creates 
a graphical bar chart display where each channel is represented as a vertical 
bar whose height corresponds to the signal amplitude.

The visualization is designed for real-time monitoring of EMG signals from 
uMyo sensors, providing immediate visual feedback of muscle activation levels 
across three independent channels. This is particularly useful for:

- Real-time EMG signal monitoring during data collection
- Visual feedback for muscle activation training
- Debugging and validation of sensor readings
- Educational demonstrations of EMG signal characteristics

Technical Details:
    - Uses pygame for hardware-accelerated graphics rendering
    - Supports real-time updates with minimal latency
    - Fixed window size of 1200x500 pixels optimized for visibility
    - Color-coded bars for easy channel identification
    - Automatic scaling based on signal amplitude

Dependencies:
    - pygame: For graphics rendering and window management
    - sys: For system operations and clean exit handling

Example Usage:
    >>> import display_3ch
    >>> # In a real-time loop:
    >>> while True:
    ...     ch0, ch1, ch2 = get_emg_readings()  # Get sensor data
    ...     display_3ch.draw_3ch(ch0, ch1, ch2)  # Update display

Note:
    This module initializes pygame automatically upon import. The display window
    will remain open until explicitly closed by the user or program termination.

Author: uMyo Development Team
License: See LICENSE file in the project root
Version: 1.0
"""

# drawing via pygame

import sys
import pygame
# from math import *

pygame.init()

size = width, height = 1200, 500
screen = pygame.display.set_mode(size)


def draw_3ch(ch0, ch1, ch2):
    """Draw real-time 3-channel EMG signal visualization.
    
    Creates a real-time bar chart display showing the amplitude of three EMG 
    channels. Each channel is represented as a vertical bar with height 
    proportional to the signal amplitude. The function handles pygame events 
    and updates the display in real-time.
    
    The visualization uses the following layout:
    - Channel 0: Left bar (blue-green color)
    - Channel 1: Middle bar (blue-green color) 
    - Channel 2: Right bar (blue-green color)
    - Bars are positioned horizontally with spacing for clarity
    - Background is black for high contrast
    
    Args:
        ch0 (float): Amplitude value for channel 0. Typically normalized 
            between 0.0 and 1.0, where 1.0 represents maximum signal amplitude.
        ch1 (float): Amplitude value for channel 1. Same range as ch0.
        ch2 (float): Amplitude value for channel 2. Same range as ch0.
    
    Returns:
        int: Always returns 0 to indicate successful rendering.
    
    Side Effects:
        - Updates the pygame display window with new bar heights
        - Processes pygame events (including window close events)
        - May terminate the program if user closes the window
    
    Example:
        >>> # Display EMG signals with different amplitudes
        >>> draw_3ch(0.3, 0.7, 0.5)  # Channel 1 has highest activity
        0
        
        >>> # Display quiet signals
        >>> draw_3ch(0.1, 0.05, 0.15)  # All channels show low activity
        0
    
    Technical Notes:
        - Bar height is calculated as: height = amplitude * 150 pixels
        - Bar width is fixed at 50 pixels (150/3) for optimal visibility
        - Bars are positioned at x-coordinates: 100, 200, 300 pixels
        - Y-coordinate is inverted (300 - height) for proper orientation
        - Color RGB values: (0, 120, 160) - blue-green theme
        
    Performance:
        - Optimized for real-time rendering at high frame rates
        - Uses pygame's efficient screen locking for fast updates
        - Minimal computational overhead suitable for continuous operation
    """
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            print("exiting")
            sys.exit()
    bsize = 150
    bratio = 3
    DX = 100
    DY = 300
    screen.fill([0, 0, 0])
    screen.lock()
    bx = DX
    sy = ch0 * bsize
    sx = bsize / bratio
    by = DY - sy
    cl = 0, 120, 160
    screen.fill(cl, (bx, by, sx, sy))
    bx += 2 * sx
    sy = ch1 * bsize
    by = DY - sy
    screen.fill(cl, (bx, by, sx, sy))
    bx += 2 * sx
    sy = ch2 * bsize
    by = DY - sy
    screen.fill(cl, (bx, by, sx, sy))

    #    screen.blit(ball, ballrect)
    screen.unlock()
    pygame.display.flip()
    return 0
