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
    sys.path.append('net')
    from tk_renderer import TkRenderer
    from segment_font import SegmentFont
    import browser
except ImportError:
    # Handle running from root directory
    sys.path.append('kernel')
    sys.path.append('ui')
    sys.path.append('net')
    from intent_parser import IntentParser
    from tk_renderer import TkRenderer
    from segment_font import SegmentFont
    import browser

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"
SYSTEM_PROMPT = """
You are the kernel of jaxOS, an AI-native operating system.
Your goal is to interpret user intent and translate it into system calls.
Output ONLY valid JSON matching this schema:
{
  "action": "create_file" | "read_file" | "delete_file" | "list_files" | "system_status" | "browse",
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
        # Split message by newlines to prevent UI overlapping
        for line in message.split('\n'):
            self.log_lines.append(line)
        
        # Keep buffer size reasonable (e.g., 15 lines)
        while len(self.log_lines) > 15:
            self.log_lines.pop(0)

    def render_ui(self, show_prompt=True):
        """Draws the UI frame using atomic rendering."""
        # Prepare data for rendering
        header = ["jaxOS v1.0", "--------------"]
        
        # Format log lines
        formatted_logs = []
        for line in self.log_lines:
            formatted_logs.append(line)
            
        prompt = "USER@NEURO> " if show_prompt else ""
        
        self.renderer.render_screen(
            header, 
            formatted_logs, 
            prompt, 
            self.renderer.current_input
        )

    def boot(self):
        self.log("jaxOS v1.0 Booting...")
        self.render_ui(show_prompt=False)
        
        self.log("[*] Init Neural Shim...")
        self.render_ui(show_prompt=False)
        
        if self._check_ollama():
            self.log("[+] Cortex Online.")
        else:
            self.log("[-] Cortex Offline.")
            
        self.log("[*] Mounting VFS...")
        self.render_ui(show_prompt=False)
        time.sleep(1)
        self.log("System Ready.")
        self.render_ui(show_prompt=True)

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
                return raw_response
        except Exception as e:
            self.log(f"[!] Inference Error: {e}")
            return "{}"

    def execute_syscall(self, intent: Dict[str, Any]):
        action = intent.get("action")
        params = intent.get("params", {})
        
        self.log(f"Exec: {action}")
        self.render_ui(show_prompt=False)
        
        if action == "create_file":
            path = params.get("path")
            content = params.get("content", "")
            self.fs_state[path] = content
            self.log(f"Created {path}")
            
        elif action == "read_file":
            path = params.get("path")
            if path in self.fs_state:
                self.log(f"Read {path}")
                self.log(self.fs_state[path])
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

        elif action == "browse":
            url = params.get("url")
            self.log(f"Browsing: {url}...")
            self.render_ui(show_prompt=False)
            
            summary = browser.fetch_and_summarize(url, self._llm_inference)
            self.log("--- PAGE SUMMARY ---")
            for line in summary.split('\n'):
                if line.strip():
                    self.log(line.strip())
            self.log("--------------------")
            
        elif action == "unknown":
            self.log("Unknown Intent")
            
        self.render_ui(show_prompt=True)

    def kernel_loop(self):
        """The Input Loop running in a background thread."""
        self.boot()
        
        while self.running:
            try:
                # Update UI to show cursor blinking
                self.render_ui(show_prompt=True)
                
                # Poll for input from GUI
                try:
                    # Wait for input from GUI (100ms timeout to allow UI updates)
                    user_input = self.renderer.input_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                self.log(f"USER@NEURO> {user_input}")
                
                if user_input.lower() in ["exit", "quit", "shutdown"]:
                    self.log("Shutting down...")
                    self.render_ui(show_prompt=False)
                    self.running = False
                    self.renderer.stop() # Kill GUI
                    break
                
                if not user_input.strip():
                    continue

                # Show Thinking... but don't persist it forever
                self.log("Thinking...")
                self.render_ui(show_prompt=False) # Hide prompt while thinking
                
                llm_response = self._llm_inference(user_input)
                
                # Remove "Thinking..." from log
                if self.log_lines and self.log_lines[-1] == "Thinking...":
                    self.log_lines.pop()
                
                intent = self.parser.parse(llm_response)
                self.execute_syscall(intent)
                
            except EOFError:
                break
            except Exception as e:
                self.log(f"Panic: {e}")
                self.render_ui(show_prompt=True)

    def run(self):
        # Start Kernel Loop in background thread
        t = threading.Thread(target=self.kernel_loop, daemon=True)
        t.start()
        
        # Start GUI in main thread (Blocking)
        self.renderer.start()

if __name__ == "__main__":
    kernel = NeuralKernel()
    kernel.run()
