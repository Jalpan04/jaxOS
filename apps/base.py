from typing import List
from ui.widgets import Widget

class App:
    def __init__(self, kernel):
        self.kernel = kernel
        self.widgets: List[Widget] = []
        self.is_active = False
        self.content_start_y = 30 # Default start position for text logs

    def on_start(self):
        """Called when the app is launched."""
        self.is_active = True
        self.build_ui()

    def on_stop(self):
        """Called when the app is closed."""
        self.is_active = False
        self.widgets.clear()

    def build_ui(self):
        """Override this to add widgets."""
        pass

    def on_input(self, user_input: str):
        """Handle text input from the terminal."""
        pass

    def log(self, message: str):
        """Helper to log to the kernel."""
        self.kernel.log(message)
