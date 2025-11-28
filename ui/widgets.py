from typing import Callable, Optional

class Widget:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True

    def draw(self, canvas, renderer):
        """Draw the widget on the canvas."""
        pass

    def on_click(self, x: int, y: int) -> bool:
        """Handle click event. Returns True if handled."""
        if not self.visible:
            return False
        return self.x <= x <= self.x + self.width and \
               self.y <= y <= self.y + self.height

class Label(Widget):
    def __init__(self, x: int, y: int, text: str, font_size: int = 14, color: str = "#00FF32"):
        # Width/Height are approximate for hit testing, though labels usually aren't clickable
        super().__init__(x, y, len(text) * 10, font_size + 4)
        self.text = text
        self.font_size = font_size
        self.color = color

    def draw(self, canvas, renderer):
        if not self.visible: return
        canvas.create_text(
            self.x, self.y,
            text=self.text,
            fill=self.color,
            font=("Courier New", self.font_size, "bold"),
            anchor="nw"
        )

class Button(Widget):
    def __init__(self, x: int, y: int, width: int, height: int, text: str, command: Callable):
        super().__init__(x, y, width, height)
        self.text = text
        self.command = command
        self.bg_color = "#006414" # Dim Green
        self.fg_color = "#00FF32" # Bright Green

    def draw(self, canvas, renderer):
        if not self.visible: return
        
        # Draw Box
        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            outline=self.fg_color,
            fill=self.bg_color,
            width=2
        )
        
        # Draw Text (Centered)
        center_x = self.x + (self.width / 2)
        center_y = self.y + (self.height / 2)
        
        canvas.create_text(
            center_x, center_y,
            text=self.text,
            fill=self.fg_color,
            font=("Courier New", 12, "bold"),
            anchor="center"
        )

    def on_click(self, x: int, y: int) -> bool:
        if super().on_click(x, y):
            if self.command:
                self.command()
            return True
        return False

class Panel(Widget):
    """A container widget that arranges children using a grid layout."""
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.children = []
        self.padding = 5
        self.bg_color = "#001000" # Very dark green
        self.border_color = "#004400"

    def add_child(self, widget: Widget):
        self.children.append(widget)

    def set_grid_layout(self, rows: int, cols: int):
        """Auto-arranges children in a grid."""
        if not self.children: return
        
        cell_width = (self.width - (self.padding * (cols + 1))) // cols
        cell_height = (self.height - (self.padding * (rows + 1))) // rows
        
        for i, widget in enumerate(self.children):
            row = i // cols
            col = i % cols
            
            if row >= rows: break # Overflow
            
            widget.x = self.x + self.padding + (col * (cell_width + self.padding))
            widget.y = self.y + self.padding + (row * (cell_height + self.padding))
            widget.width = cell_width
            widget.height = cell_height

    def draw(self, canvas, renderer):
        if not self.visible: return
        
        # Draw Panel Background
        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            outline=self.border_color,
            fill=self.bg_color,
            width=1
        )
        
        # Draw Children
        for child in self.children:
            child.draw(canvas, renderer)

    def on_click(self, x: int, y: int) -> bool:
        if not self.visible: return False
        
        # Check children first (top-most)
        for child in reversed(self.children):
            if child.on_click(x, y):
                return True
        
        return False
