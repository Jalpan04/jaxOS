from apps.base import App
from ui.widgets import Button, Label, Panel

class Calculator(App):
    def build_ui(self):
        self.expression = ""
        
        # Display
        self.display_label = Label(20, 40, "0", font_size=24, color="#00FF32")
        self.widgets.append(self.display_label)
        
        # Keypad Panel
        panel = Panel(20, 90, 300, 200)
        self.widgets.append(panel)
        
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]
        
        for text in buttons:
            # Capture text in closure
            cmd = lambda t=text: self.on_button_click(t)
            # Size doesn't matter here, layout will override
            btn = Button(0, 0, 10, 10, text, cmd)
            panel.add_child(btn)
            
        panel.set_grid_layout(rows=4, cols=4)

        self.content_start_y = 300 # Logs below calculator

    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
        elif char == '=':
            try:
                # Safe eval
                result = str(eval(self.expression))
                self.expression = result
            except:
                self.expression = "Error"
        else:
            if self.expression == "Error":
                self.expression = ""
            self.expression += char
            
        # Update Display
        self.display_label.text = self.expression if self.expression else "0"
        
        # Force re-render
        self.kernel.render_ui(show_prompt=True)

    def on_input(self, user_input: str):
        # Allow keyboard input too
        if user_input.lower() == "exit":
            self.kernel.close_app()
            return
            
        # Map keyboard to calculator logic
        for char in user_input:
            if char in "0123456789+-*/.":
                self.on_button_click(char)
            elif char == "=":
                self.on_button_click("=")
            elif char.lower() == "c":
                self.on_button_click("C")
