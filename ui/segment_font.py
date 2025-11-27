"""
neuro-casio-os/ui/segment_font.py

The Casio Visual Engine - Segment Font Renderer.
------------------------------------------------
Procedurally generates characters using line primitives.
No bitmaps. Pure vector math.

Aesthetics:
- 14-Segment Display style
- Green-on-Black
- "Ghosting" support (simulated phosphor persistence)
"""

import math

class SegmentFont:
    def __init__(self, width=20, height=40):
        self.width = width
        self.height = height
        self.stroke_width = 2
        
        # 14-Segment Map (Conceptual)
        #       A
        #     -----
        #  F |  |  | B
        #    | G|H |
        #     -- --
        #  E |  |  | C
        #    | L|M |
        #     -----
        #       D

    def draw_char(self, char: str, x: int, y: int, draw_func):
        """
        Draws a single character at (x, y) using the provided draw_func.
        draw_func signature: (x1, y1, x2, y2, brightness)
        """
        char = char.upper()
        w = self.width
        h = self.height
        
        # Coordinates
        x0, y0 = x, y
        x1, y1 = x + w, y + h
        xm, ym = x + w//2, y + h//2
        
        # Segment definitions (Start, End)
        segments = {
            'A': [(x0, y0), (x1, y0)], # Top
            'B': [(x1, y0), (x1, ym)], # Top-Right
            'C': [(x1, ym), (x1, y1)], # Bottom-Right
            'D': [(x0, y1), (x1, y1)], # Bottom
            'E': [(x0, ym), (x0, y1)], # Bottom-Left
            'F': [(x0, y0), (x0, ym)], # Top-Left
            'G': [(x0, ym), (xm, ym)], # Middle-Left
            'H': [(xm, ym), (x1, ym)], # Middle-Right
            'I': [(xm, y0), (xm, ym)], # Top-Vertical (Center)
            'J': [(xm, ym), (xm, y1)], # Bottom-Vertical (Center)
            'K': [(x0, y0), (xm, ym)], # Top-Left-Diagonal
            'L': [(xm, y0), (x1, ym)], # Top-Right-Diagonal
            'M': [(x0, y1), (xm, ym)], # Bottom-Left-Diagonal
            'N': [(xm, ym), (x1, y1)], # Bottom-Right-Diagonal
        }
        
        # Character Map (Which segments to turn on)
        char_map = {
            'A': ['A', 'B', 'C', 'E', 'F', 'G', 'H'],
            'B': ['A', 'B', 'C', 'D', 'I', 'J'], # Stylized B (looks like 8 but with vertical center)
            'C': ['A', 'D', 'E', 'F'],
            'O': ['A', 'B', 'C', 'D', 'E', 'F'],
            'S': ['A', 'F', 'G', 'H', 'C', 'D'], # 5-like S
            'I': ['A', 'D', 'I', 'J'],
            # Add more as needed...
        }
        
        active_segments = char_map.get(char, [])
        
        if not active_segments:
            # Draw a box for unknown char
            draw_func(x0, y0, x1, y0, 1.0)
            draw_func(x1, y0, x1, y1, 1.0)
            draw_func(x1, y1, x0, y1, 1.0)
            draw_func(x0, y1, x0, y0, 1.0)
            return

        for seg_id in active_segments:
            if seg_id in segments:
                start, end = segments[seg_id]
                draw_func(start[0], start[1], end[0], end[1], 1.0)

# Test block
if __name__ == "__main__":
    font = SegmentFont()
    print("--- Drawing 'A' ---")
    font.draw_char('A', 10, 10)
    print("\n--- Drawing 'B' ---")
    font.draw_char('B', 40, 10)
