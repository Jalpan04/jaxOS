from apps.base import App
from ui.widgets import Panel, Label
import time
import random

class SysMon(App):
    def on_start(self):
        # Don't log text, use Labels to avoid overlap with shell prompt
        self.running = True
        self.build_ui()
        self._tick()

    def build_ui(self):
        # Title Labels
        self.widgets.append(Label(20, 50, "SYSTEM MONITOR", font_size=18, color="#00FF32"))
        self.widgets.append(Label(20, 75, "Press Q to quit.", font_size=12, color="#006414"))

        # Main Container (Moved down to avoid prompt overlap)
        self.main_panel = Panel(20, 100, 600, 300)
        self.main_panel.bg_color = "#000000" # Transparent-ish
        self.widgets.append(self.main_panel)
        
        # 4 Cards
        self.cpu_panel = self._create_card("CPU")
        self.ram_panel = self._create_card("RAM")
        self.net_panel = self._create_card("NET")
        self.disk_panel = self._create_card("DISK")
        
        self.main_panel.add_child(self.cpu_panel)
        self.main_panel.add_child(self.ram_panel)
        self.main_panel.add_child(self.net_panel)
        self.main_panel.add_child(self.disk_panel)
        
        self.main_panel.set_grid_layout(rows=2, cols=2)
        
        # Re-layout children now that they have correct positions
        self.cpu_panel.set_grid_layout(2, 1)
        self.ram_panel.set_grid_layout(2, 1)
        self.net_panel.set_grid_layout(2, 1)
        self.disk_panel.set_grid_layout(2, 1)
        
        # Labels for updating
        self.cpu_label = self.cpu_panel.children[1]
        self.ram_label = self.ram_panel.children[1]
        self.net_label = self.net_panel.children[1]
        self.disk_label = self.disk_panel.children[1]

    def _create_card(self, title):
        p = Panel(0, 0, 10, 10) # Size set by layout
        p.add_child(Label(0, 0, title, font_size=16, color="#00FF32"))
        p.add_child(Label(0, 0, "Loading...", font_size=12, color="#006414"))
        return p

    def on_input(self, user_input):
        if user_input.lower() == 'q':
            self.running = False
            self.kernel.close_app()

    def _tick(self):
        if not self.running: return
        
        # Update Stats
        self.cpu_label.text = f"{random.randint(10, 90)}%"
        self.ram_label.text = "64KB / 64KB"
        self.net_label.text = "CONNECTED"
        self.disk_label.text = "RW / SQLITE"
        
        self.kernel.render_ui()
        self.kernel.renderer.root.after(1000, self._tick)
