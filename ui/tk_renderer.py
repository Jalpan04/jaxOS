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
from typing import Tuple, Callable, List
from widgets import Widget, Label, Button

# Colors
COLOR_BLACK = "#000000"
COLOR_GREEN = "#00FF32"
COLOR_DIM_GREEN = "#006414"
COLOR_WHITE = "#FFFFFF"

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
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Input Handling
        self.input_queue = queue.Queue()
        self.current_input = ""
        self.root.bind('<Key>', self.on_key)
        self.root.bind('<Button-1>', self.on_click) # Mouse Click
        
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
        
        # Widgets List
        # Widgets List
        self.widgets: List[Widget] = []
        
        # Cursor State
        self.cursor_visible = True
        self._blink_cursor()

    def _blink_cursor(self):
        """Toggles cursor visibility every 500ms."""
        self.cursor_visible = not self.cursor_visible
        self.render_last_frame()
        self.root.after(500, self._blink_cursor)

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
            
    def on_click(self, event):
        """Handle mouse clicks on widgets."""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        for widget in self.widgets:
            if widget.on_click(canvas_x, canvas_y):
                return # Handled
        
        # Check for text clicks (specifically Recovery Key)
        item = self.canvas.find_closest(canvas_x, canvas_y)
        if item:
            tags = self.canvas.gettags(item)
            # In Tkinter canvas, text items don't have tags by default unless added.
            # But we can get the text content.
            item_type = self.canvas.type(item)
            if item_type == "text":
                text_content = self.canvas.itemcget(item, "text")
                if "Recovery Key:" in text_content:
                    # Extract key
                    try:
                        key = text_content.split("Recovery Key:")[1].strip()
                        self.root.clipboard_clear()
                        self.root.clipboard_append(key)
                        self.root.update() # Required for clipboard
                        
                        # Visual Feedback (Flash White)
                        original_fill = self.canvas.itemcget(item, "fill")
                        self.canvas.itemconfig(item, fill=COLOR_WHITE)
                        self.root.after(200, lambda: self.canvas.itemconfig(item, fill=original_fill))
                        
                        # Optional: Show a temporary "Copied" message
                        # For now, the visual flash is sufficient feedback
                    except IndexError:
                        pass
            
    def get_input(self):
        """Blocking get from input queue."""
        return self.input_queue.get()

    def start(self):
        """Starts the Tkinter main loop. Blocking."""
        self._blink_cursor() # Start blinking
        self.root.mainloop()

    def stop(self):
        """Stops the GUI."""
        self.root.quit()
        
    def render_last_frame(self):
        if hasattr(self, 'last_header'):
            start_y = getattr(self, 'last_start_y', 30)
            self.render_screen(self.last_header, self.last_logs, self.last_prompt, self.last_input, start_y)

    def render_screen(self, header_lines, log_lines, input_prompt, current_input, start_y=30):
        """
        Atomically renders the entire screen frame with dynamic wrapping and scrolling.
        """
        # Save state
        self.last_header = header_lines
        self.last_logs = log_lines
        self.last_prompt = input_prompt
        self.last_input = current_input
        self.last_start_y = start_y

        def _draw():
            # Check if at bottom before clearing
            try:
                was_at_bottom = self.canvas.yview()[1] >= 0.95
            except:
                was_at_bottom = True

            self.canvas.delete("all")
            width = self.root.winfo_width() - 20 # Account for scrollbar
            max_text_width = width - 40
            font_spec = ("Courier New", self.font_size, "bold")
            
            # --- STATUS BAR ---
            status_text = time.strftime("%H:%M:%S") + " | MEM: 64KB | NET: ON"
            self.canvas.create_text(
                width - 10, 10,
                text=status_text,
                fill=COLOR_DIM_GREEN,
                font=("Courier New", 12),
                anchor="ne"
            )
            
            # Draw Widgets
            for widget in self.widgets:
                widget.draw(self.canvas, self)

            # Draw Header
            y = start_y 
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
            if input_prompt: 
                # Cursor Logic
                cursor_char = "_" if self.cursor_visible else " "
                full_input = f"{input_prompt}{current_input}{cursor_char}"
                
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
        pass

if __name__ == "__main__":
    # Test stub
    r = TkRenderer()
    r.start()
