"""
jaxOS/ui/tk_renderer.py

The Casio Visual Engine - Native Tkinter Renderer
-------------------------------------------------
Simulates the CRT/LCD hardware interface using a native OS window.
- Resolution: 640x480
- Color: Monochrome Green
- Threading: GUI runs on Main Thread, Kernel runs on Background Thread.

Research Note:
Tkinter is not thread-safe. All drawing commands from the Kernel thread
must be marshaled to the Main thread using `root.after` or a queue.
"""

import tkinter as tk
import time
from typing import Tuple, Callable

# Colors
COLOR_BLACK = "#000000"
COLOR_GREEN = "#00FF32"
COLOR_DIM_GREEN = "#006414"

class TkRenderer:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.font_renderer = None # Will be injected
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("jaxOS // Neural Kernel")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg=COLOR_BLACK)
        self.root.resizable(False, False)
        
        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.root, 
            width=width, 
            height=height, 
            bg=COLOR_BLACK, 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Ghosting layer (simulated by not clearing fully or using semi-transparent rectangles)
        # Tkinter doesn't support alpha on canvas primitives easily without PIL.
        # We will simulate ghosting by clearing the screen less frequently or 
        # just redrawing everything. For simplicity in Tkinter, we'll just clear.
        
    def start(self):
        """Starts the Tkinter main loop. Blocking."""
        self.root.mainloop()

    def stop(self):
        """Stops the GUI."""
        self.root.quit()

    def clear(self):
        """Schedules a clear operation on the main thread."""
        self.root.after(0, lambda: self.canvas.delete("all"))

    def draw_line(self, x1, y1, x2, y2, brightness=1.0):
        """
        Draws a vector line. Thread-safe wrapper.
        """
        color = COLOR_GREEN if brightness > 0.8 else COLOR_DIM_GREEN
        self.root.after(0, lambda: self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2))

    def render_text(self, text: str, x: int, y: int, font_engine=None):
        """
        Draws text using native Tkinter font for maximum readability.
        Ignores font_engine (SegmentFont) to fix readability issues.
        """
        self.root.after(0, lambda: self.canvas.create_text(
            x, y, 
            text=text, 
            fill=COLOR_GREEN, 
            font=("Courier New", 14, "bold"),
            anchor="nw"
        ))

    def boot_sequence(self):
        """
        Simulates a CRT turn-on effect.
        """
        pass

if __name__ == "__main__":
    # Test stub
    r = TkRenderer()
    r.root.after(1000, lambda: r.draw_line(10, 10, 100, 100))
    r.start()
