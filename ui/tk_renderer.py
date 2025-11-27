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
import queue
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
class TkRenderer:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.font_renderer = None # Set by kernel
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("jaxOS // Neural Kernel")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg=COLOR_BLACK)
        self.root.resizable(True, True)
        
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

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Input Handling
        self.input_queue = queue.Queue()
        self.current_input = ""
        self.root.bind('<Key>', self.on_key)
        
        # Font State
        self.font_size = 14
        self.root.bind('<Control-plus>', self.increase_font)
        self.root.bind('<Control-equal>', self.increase_font)
        self.root.bind('<Control-minus>', self.decrease_font)
        self.root.bind('<MouseWheel>', self.on_mousewheel)

        self.root.bind('<Control-v>', self.on_paste)
        
        # Store last frame data for re-rendering on font change
        self.last_header = []
        self.last_logs = []
        self.last_prompt = ""
        self.last_input = ""
        
    def increase_font(self, event):
        self.font_size += 2
        self.render_last_frame()

    def decrease_font(self, event):
        if self.font_size > 8:
            self.font_size -= 2
            self.render_last_frame()

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_key(self, event):
        """Handles key presses for interactive input."""
        if event.keysym == 'Return':
            self.input_queue.put(self.current_input)
            self.current_input = ""
        elif event.keysym == 'BackSpace':
            self.current_input = self.current_input[:-1]
        elif len(event.char) == 1 and event.char.isprintable():
            self.current_input += event.char

    def on_paste(self, event):
        """Handles Paste (Ctrl+V)."""
        try:
            text = self.root.clipboard_get()
            self.current_input += text
        except:
            pass
            
    def get_input(self):
        """Blocking get from input queue."""
        return self.input_queue.get()

    def start(self):
        """Starts the Tkinter main loop. Blocking."""
        self.root.mainloop()

    def stop(self):
        """Stops the GUI."""
        self.root.quit()
        
    def render_last_frame(self):
        if hasattr(self, 'last_header'):
            self.render_screen(self.last_header, self.last_logs, self.last_prompt, self.last_input)

    def render_screen(self, header_lines, log_lines, input_prompt, current_input):
        """
        Atomically renders the entire screen frame with dynamic wrapping and scrolling.
        """
        # Save state
        self.last_header = header_lines
        self.last_logs = log_lines
        self.last_prompt = input_prompt
        self.last_input = current_input

        def _draw():
            # Check if at bottom before clearing
            try:
                # yview returns (top, bottom) fractions. If bottom is near 1.0, we are at the bottom.
                was_at_bottom = self.canvas.yview()[1] >= 0.95
            except:
                was_at_bottom = True

            self.canvas.delete("all")
            width = self.root.winfo_width() - 20 # Account for scrollbar
            max_text_width = width - 40
            font_spec = ("Courier New", self.font_size, "bold")
            
            # Draw Header
            y = 20
            for line in header_lines:
                text_id = self.canvas.create_text(
                    20, y, 
                    text=line, 
                    fill=COLOR_GREEN, 
                    font=font_spec, 
                    anchor="nw",
                    width=max_text_width
                )
                bbox = self.canvas.bbox(text_id)
                y = bbox[3] + 5 
                
            # Draw Log
            y += 10
            for line in log_lines:
                text_id = self.canvas.create_text(
                    20, y, 
                    text=line, 
                    fill=COLOR_GREEN, 
                    font=font_spec, 
                    anchor="nw",
                    width=max_text_width
                )
                bbox = self.canvas.bbox(text_id)
                y = bbox[3] + 5
                
            # Draw Input
            if input_prompt: # Only draw if prompt is present
                cursor = "_" if (len(current_input) % 2 == 0) else " "
                full_input = f"{input_prompt}{current_input}{cursor}"
                
                text_id = self.canvas.create_text(
                    20, y + 10, 
                    text=full_input, 
                    fill=COLOR_GREEN, 
                    font=font_spec, 
                    anchor="nw",
                    width=max_text_width
                )
                bbox = self.canvas.bbox(text_id)
                y = bbox[3] + 20
            
            # Update Scroll Region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Only auto-scroll if we were already at the bottom
            if was_at_bottom:
                self.canvas.yview_moveto(1.0)
            
        self.root.after(0, _draw)

    # Legacy methods kept for compatibility but redirected or deprecated
    def clear(self): pass
    def render_text(self, *args): pass
    def render_input_line(self, *args): pass

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
