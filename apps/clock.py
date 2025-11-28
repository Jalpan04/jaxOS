
from apps.base import App
import time
from ui.widgets import Label

class Clock(App):
    def on_start(self):
        self.log("DIGITAL CLOCK")
        self.log("Press Q to quit.")
        self.running = True
        self._tick()

    def on_input(self, user_input):
        if user_input.lower() == 'q':
            self.running = False
            self.kernel.close_app()

    def _tick(self):
        if not self.running:
            return
            
        current_time = time.strftime("%H:%M:%S")
        self.kernel.app_log_lines = [
            "",
            "   " + current_time,
            ""
        ]
        self.kernel.render_ui()
        
        # Schedule next tick (hacky via tk root)
        self.kernel.renderer.root.after(1000, self._tick)
