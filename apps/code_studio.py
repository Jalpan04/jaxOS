from apps.base import App
from ui.widgets import Button, Label
import io
import sys
import traceback

class CodeStudio(App):
    def build_ui(self):
        self.widgets.append(Label(20, 40, "CODE STUDIO v1.0", font_size=18))
        self.widgets.append(Label(20, 70, "Type python code below. Type 'RUN' to execute.", font_size=12))
        self.widgets.append(Label(20, 90, "Type 'EXIT' to close.", font_size=12))
        
        # Run Button
        self.widgets.append(Button(500, 40, 80, 30, "RUN", self.run_code))
        
        self.content_start_y = 130 # Start text below widgets
        self.code_buffer = []

    def on_input(self, user_input: str):
        if user_input.upper() == "RUN":
            self.run_code()
            return
        
        if user_input.upper() == "EXIT":
            self.kernel.close_app()
            return

        if user_input.upper() == "CLEAR":
            self.code_buffer = []
            self.kernel.log("Buffer cleared.")
            return

        # Add line to buffer
        self.code_buffer.append(user_input)
        self.kernel.log(f" {len(self.code_buffer)}: {user_input}")

    def run_code(self):
        code = "\n".join(self.code_buffer)
        self.kernel.log("--- EXECUTING ---")
        
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            # Restricted globals for safety (basic sandbox)
            safe_globals = {
                "print": print,
                "range": range,
                "len": len,
                "int": int,
                "str": str,
                "list": list,
                "dict": dict,
                "math": __import__("math")
            }
            exec(code, safe_globals)
            output = redirected_output.getvalue()
            if output:
                self.kernel.log(output)
            else:
                self.kernel.log("(No Output)")
        except Exception:
            self.kernel.log(traceback.format_exc())
        finally:
            sys.stdout = old_stdout
            self.kernel.log("-----------------")
