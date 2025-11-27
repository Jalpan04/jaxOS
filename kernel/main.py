"""
neuro-casio-os/kernel/main.py

The Neural Kernel Entry Point.
------------------------------
This is the "PID 1" of NEURO-CASIO OS.
Instead of a traditional init system, it boots directly into a
Natural Language REPL powered by a local Large Language Model.

Architecture:
1. Boot Sequence: Initialize HAL, FS, UI.
2. Kernel Loop:
   - Read Input (Natural Language)
   - Inference (Ollama / gemma3:12b)
   - Intent Parsing (JSON -> SysCall)
   - Execution (Python Function)
   - Render (Generative UI)
"""

import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any

import threading
import queue

# Import internal modules
try:
    from intent_parser import IntentParser
    # Import UI modules
    sys.path.append('ui')
    from tk_renderer import TkRenderer
    from segment_font import SegmentFont
except ImportError:
    # Handle running from root directory
    sys.path.append('kernel')
    sys.path.append('ui')
    from tk_renderer import TkRenderer
    from segment_font import SegmentFont

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"
SYSTEM_PROMPT = """
You are the kernel of jaxOS, an AI-native operating system.
Your goal is to interpret user intent and translate it into system calls.
Output ONLY valid JSON matching this schema:
{
  "action": "create_file" | "read_file" | "delete_file" | "list_files" | "system_status",
  "params": { ...arguments... }
}
Example:
{
  "action": "create_file",
  "params": { "path": "test.txt", "content": "hello" }
}
"""

class NeuralKernel:
    def __init__(self):
        self.parser = IntentParser()
        self.running = True
        self.fs_state = {} 
        
        # Initialize UI
        self.renderer = TkRenderer()
        self.font = SegmentFont()
        self.renderer.font_renderer = self.font
        
        # Terminal Log (for display)
        self.log_lines = []
        
        # Input Queue (if we wanted to pass input from GUI, but we use console for now)

    def log(self, message: str):
        """Logs to console and adds to UI buffer"""
        print(message)
        self.log_lines.append(message)
        if len(self.log_lines) > 10:
            self.log_lines.pop(0)
            
    def render_ui(self):
        """Draws the UI frame. Thread-safe."""
        self.renderer.clear()
        
        # We need to schedule the text rendering
        # Since render_text makes many draw_line calls, we wrap it
        def _draw():
            # Draw Header
            self.renderer.render_text("jaxOS v1.0", 20, 20, self.font)
            self.renderer.render_text("--------------", 20, 50, self.font)
            
            # Draw Log
            y = 80
            for line in self.log_lines:
                display_text = line[:25]
                self.renderer.render_text(display_text, 20, y, self.font)
                y += 45
        
        # Execute drawing on main thread
        self.renderer.root.after(0, _draw)

    def boot(self):
        self.log("jaxOS v1.0 Booting...")
        self.render_ui()
        
        self.log("[*] Init Neural Shim...")
        self.render_ui()
        
        if self._check_ollama():
            self.log("[+] Cortex Online.")
        else:
            self.log("[-] Cortex Offline.")
            
        self.log("[*] Mounting VFS...")
        self.render_ui()
        time.sleep(1)
        self.log("System Ready.")
        self.render_ui()

    # ... (_check_ollama, _llm_inference, execute_syscall remain same) ...
    def _check_ollama(self) -> bool:
        try:
            url = "http://127.0.0.1:11434/api/tags"
            with urllib.request.urlopen(url) as response:
                return response.status == 200
        except Exception as e:
            self.log(f"[!] Cortex Connection Error: {e}")
            return False

    def _llm_inference(self, user_input: str) -> str:
        payload = {
            "model": MODEL_NAME,
            "prompt": user_input,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": "json"
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                raw_response = result.get("response", "{}")
                self.log(f"[DEBUG] Raw LLM: {raw_response}")
                return raw_response
        except Exception as e:
            self.log(f"[!] Inference Error: {e}")
            return "{}"

    def execute_syscall(self, intent: Dict[str, Any]):
        action = intent.get("action")
        params = intent.get("params", {})
        
        self.log(f"Exec: {action}")
        self.render_ui()
        
        if action == "create_file":
            path = params.get("path")
            content = params.get("content", "")
            self.fs_state[path] = content
            self.log(f"Created {path}")
            
        elif action == "read_file":
            path = params.get("path")
            if path in self.fs_state:
                self.log(f"Read {path}")
            else:
                self.log(f"Error: {path} 404")
                
        elif action == "delete_file":
            path = params.get("path")
            if path in self.fs_state:
                del self.fs_state[path]
                self.log(f"Deleted {path}")
            else:
                self.log(f"Error: {path} 404")
                
        elif action == "list_files":
            files = list(self.fs_state.keys())
            self.log(f"Files: {len(files)}")
            for f in files[:3]:
                self.log(f"- {f}")
            
        elif action == "system_status":
            self.log("RAM: 16KB Used")
            self.log(f"Cortex: {MODEL_NAME}")
            
        elif action == "unknown":
            self.log("Unknown Intent")
            
        self.render_ui()

    def kernel_loop(self):
        """The Input Loop running in a background thread."""
        self.boot()
        
        while self.running:
            try:
                # Console input blocks this thread, but GUI thread keeps running
                user_input = input("\nUSER@NEURO> ")
                if user_input.lower() in ["exit", "quit", "shutdown"]:
                    self.log("Shutting down...")
                    self.render_ui()
                    self.running = False
                    self.renderer.stop() # Kill GUI
                    break
                
                if not user_input.strip():
                    continue

                self.log("Thinking...")
                self.render_ui()
                
                llm_response = self._llm_inference(user_input)
                
                intent = self.parser.parse(llm_response)
                self.execute_syscall(intent)
                
            except EOFError:
                break
            except Exception as e:
                self.log(f"Panic: {e}")
                self.render_ui()

    def run(self):
        # Start Kernel Loop in background thread
        t = threading.Thread(target=self.kernel_loop, daemon=True)
        t.start()
        
        # Start GUI in main thread (Blocking)
        self.renderer.start()

if __name__ == "__main__":
    kernel = NeuralKernel()
    kernel.run()
