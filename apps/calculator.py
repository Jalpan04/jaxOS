from apps.base import App
from ui.widgets import Button, Label

class Calculator(App):
    def build_ui(self):
        self.expression = ""
        
        # Display
        self.display_label = Label(20, 40, "0", font_size=24, color="#00FF32")
        self.widgets.append(self.display_label)
        
        # Grid Config
        start_x = 20
        start_y = 90
        btn_w = 60
        btn_h = 40
        gap = 10
        
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]
        
        for r, row in enumerate(buttons):
            for c, text in enumerate(row):
                x = start_x + c * (btn_w + gap)
                y = start_y + r * (btn_h + gap)
                
                # Capture text in closure
                cmd = lambda t=text: self.on_button_click(t)
                self.widgets.append(Button(x, y, btn_w, btn_h, text, cmd))

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
