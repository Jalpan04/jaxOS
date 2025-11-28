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
