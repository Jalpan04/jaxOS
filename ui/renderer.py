"""
jaxOS/ui/renderer.py

The Casio Visual Engine - Hardware Renderer (Pygame)
----------------------------------------------------
Simulates the CRT/LCD hardware interface.
- Resolution: 640x480 (Virtual 320x240)
- Color: Monochrome Green (0, 255, 0)
- Effect: Phosphor Persistence (Ghosting)

Research Note:
In a real Unikernel, this would write directly to the framebuffer memory address.
Here, we use Pygame to create a window that acts as the physical display.
"""

import pygame
import sys
import time
from typing import Tuple

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 50)
COLOR_DIM_GREEN = (0, 100, 20)

class Renderer:
    def __init__(self, width=640, height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("jaxOS // Neural Kernel")
        
        # Surface for persistence effect
        self.phosphor_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self.phosphor_layer.fill((0, 0, 0, 0))
        
        self.font_renderer = None # Will be injected

    def clear(self):
        """
        Applies the ghosting effect instead of a hard clear.
        """
        # Fade out the current screen
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.set_alpha(40) # Decay rate (higher = faster decay)
        fade_surface.fill(COLOR_BLACK)
        self.screen.blit(fade_surface, (0, 0))

    def draw_line(self, x1, y1, x2, y2, brightness=1.0):
        """
        Draws a vector line.
        """
        color = COLOR_GREEN if brightness > 0.8 else COLOR_DIM_GREEN
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)

    def render_text(self, text: str, x: int, y: int, font_engine):
        """
        Delegates text drawing to the procedural font engine.
        """
        cursor_x = x
        for char in text:
            # Pass our draw_line method to the font engine
            font_engine.draw_char(char, cursor_x, y, self.draw_line)
            cursor_x += font_engine.width + 5 # Kerning

    def update(self):
        """
        Flips the buffer and handles window events.
        """
        pygame.display.flip()
        
        # Handle window close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def boot_sequence(self):
        """
        Simulates a CRT turn-on effect.
        """
        for i in range(0, 255, 5):
            self.screen.fill((0, i, 0))
            pygame.display.flip()
            pygame.time.delay(5)
        self.screen.fill(COLOR_BLACK)
        pygame.display.flip()

if __name__ == "__main__":
    # Test stub
    r = Renderer()
    r.boot_sequence()
    while True:
        r.clear()
        r.draw_line(10, 10, 100, 100)
        r.update()
        pygame.time.delay(16)
