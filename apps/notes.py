from apps.base import App
from ui.widgets import Panel, Label, Button

class Notes(App):
    def on_start(self):
        self.log("NOTES EDITOR")
        self.log("Type to write. Commands: /save <name>, /load <name>, /clear, /quit")
        self.content = []
        self.build_ui()

    def build_ui(self):
        # Toolbar
        self.toolbar = Panel(20, 40, 600, 50)
        self.widgets.append(self.toolbar)
        
        btn_save = Button(0, 0, 10, 10, "SAVE", lambda: self.log("Type /save <filename>"))
        btn_load = Button(0, 0, 10, 10, "LOAD", lambda: self.log("Type /load <filename>"))
        btn_clear = Button(0, 0, 10, 10, "CLEAR", self.clear_content)
        btn_quit = Button(0, 0, 10, 10, "QUIT", self.quit_app)
        
        self.toolbar.add_child(btn_save)
        self.toolbar.add_child(btn_load)
        self.toolbar.add_child(btn_clear)
        self.toolbar.add_child(btn_quit)
        
        self.toolbar.set_grid_layout(rows=1, cols=4)
        
        # Text Area Display
        self.text_display = Label(20, 100, "", font_size=14, color="#00FF32")
        self.widgets.append(self.text_display)

    def on_input(self, user_input):
        cmd = user_input.strip()
        if cmd.startswith("/quit"):
            self.quit_app()
        elif cmd.startswith("/clear"):
            self.clear_content()
        elif cmd.startswith("/save"):
            parts = cmd.split(" ", 1)
            if len(parts) > 1:
                self.save_file(parts[1])
            else:
                self.log("Usage: /save <filename>")
        elif cmd.startswith("/load"):
            parts = cmd.split(" ", 1)
            if len(parts) > 1:
                self.load_file(parts[1])
            else:
                self.log("Usage: /load <filename>")
        else:
            # Append text
            self.content.append(user_input)
            self._update_display()

    def _update_display(self):
        self.text_display.text = "\n".join(self.content)
        self.kernel.render_ui()

    def clear_content(self):
        self.content = []
        self._update_display()
        self.log("Cleared.")

    def save_file(self, filename):
        data = "\n".join(self.content)
        if self.kernel.db.write_file(filename, data):
            self.log(f"Saved to {filename}")
        else:
            self.log("Error saving file.")

    def load_file(self, filename):
        data = self.kernel.db.read_file(filename)
        if data is not None:
            self.content = data.split("\n")
            self._update_display()
            self.log(f"Loaded {filename}")
        else:
            self.log("File not found.")

    def quit_app(self):
        self.kernel.close_app()
