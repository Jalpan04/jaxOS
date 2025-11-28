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
import os

# Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

sys.path.append(root_dir) # For 'apps', 'ui', etc packages
sys.path.append(os.path.join(root_dir, 'ui')) # For 'tk_renderer'
sys.path.append(os.path.join(root_dir, 'net')) # For 'browser'
sys.path.append(os.path.join(root_dir, 'fs')) # For 'db'
sys.path.append(os.path.join(root_dir, 'kernel')) # For 'intent_parser'

# Import internal modules
from intent_parser import IntentParser
from tk_renderer import TkRenderer
from segment_font import SegmentFont
import browser
from db import Database
from apps.code_studio import CodeStudio
from apps.calculator import Calculator

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma3:12b"
SYSTEM_PROMPT = """
You are the kernel of jaxOS, an AI-native operating system.
Your goal is to interpret user intent and translate it into system calls.
Output ONLY valid JSON matching this schema:
{
  "action": "create_file" | "read_file" | "delete_file" | "list_files" | "system_status" | "browse" | "launch_app",
  "params": { ...arguments... }
}
Example:
{
  "action": "launch_app",
  "params": { "name": "code_studio" }
}
"""

class NeuralKernel:
    def __init__(self):
        self.parser = IntentParser()
        self.running = True
        
        # Initialize Persistence
        self.db = Database()
        
        # Initialize UI
        self.renderer = TkRenderer()
        self.font = SegmentFont()
        self.renderer.font_renderer = self.font
        
        # Terminal Log (for display)
        self.system_log_lines = []
        self.app_log_lines = []
        
        # App State
        self.active_app = None
        self.apps = {
            "code_studio": CodeStudio(self),
            "python": CodeStudio(self), # Alias
            "calculator": Calculator(self),
            "calc": Calculator(self) # Alias
        }

    def log(self, message: str):
        """Logs to console and adds to UI buffer"""
        print(message)
        
        # Determine target buffer
        target_buffer = self.app_log_lines if self.active_app else self.system_log_lines
        
        # Split message by newlines to prevent UI overlapping
        for line in message.split('\n'):
            target_buffer.append(line)
        
        # Keep buffer size reasonable (e.g., 15 lines)
        while len(target_buffer) > 15:
            target_buffer.pop(0)

    def render_ui(self, show_prompt=True):
        """Draws the UI frame using atomic rendering."""
        start_y = 30
        if self.active_app:
            # App Mode
            header = [f"--- {self.active_app.__class__.__name__.upper()} ---"]
            formatted_logs = list(self.app_log_lines)
            prompt = "CODE> " if show_prompt else ""
            start_y = getattr(self.active_app, 'content_start_y', 30)
        else:
            # System Mode
            header = ["jaxOS v1.0", "--------------"]
            formatted_logs = list(self.system_log_lines)
            prompt = "USER@NEURO> " if show_prompt else ""
        
        self.renderer.render_screen(
            header, 
            formatted_logs, 
            prompt, 
            self.renderer.current_input,
            start_y=start_y
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

    def launch_app(self, app_name: str):
        if app_name in self.apps:
            # Clear app logs for a fresh start
            self.app_log_lines = []
            
            self.active_app = self.apps[app_name]
            self.active_app.on_start()
            self.renderer.widgets = self.active_app.widgets
            
            # Don't log "Launched..." to the app buffer to keep it clean
            # self.log(f"Launched {app_name}") 
            self.render_ui(show_prompt=True)
        else:
            self.log(f"App '{app_name}' not found.")

    def close_app(self):
        if self.active_app:
            self.active_app.on_stop()
            self.active_app = None
            self.renderer.widgets = [] # Clear widgets
            self.log("App closed.")
            self.render_ui(show_prompt=True)

    def execute_syscall(self, intent: Dict[str, Any]):
        action = intent.get("action")
        params = intent.get("params", {})
        
        self.log(f"Exec: {action}")
        self.render_ui(show_prompt=False)
        
        if action == "launch_app":
            self.launch_app(params.get("name", "").lower().replace(" ", "_"))
            return # Don't re-render here, launch_app handles it

        elif action == "create_file":
            path = params.get("path")
            content = params.get("content", "")
            if self.db.write_file(path, content):
                self.log(f"Created {path}")
            else:
                self.log(f"Error creating {path}")
            
        elif action == "read_file":
            path = params.get("path")
            content = self.db.read_file(path)
            if content is not None:
                self.log(f"Read {path}")
                self.log(content)
            else:
                self.log(f"Error: {path} 404")
                
        elif action == "delete_file":
            path = params.get("path")
            if self.db.delete_file(path):
                self.log(f"Deleted {path}")
            else:
                self.log(f"Error: {path} 404")
                
        elif action == "list_files":
            files = self.db.list_files()
            self.log(f"Files: {len(files)}")
            for f in files[:5]: # Show top 5
                self.log(f"- {f}")
            
        elif action == "system_status":
            self.log("RAM: 16KB Used")
            self.log(f"Cortex: {MODEL_NAME}")
            self.log("Storage: SQLite Persistent")

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

                if not user_input.strip():
                    continue

                # APP ROUTING (Priority 1)
                if self.active_app:
                    self.active_app.on_input(user_input)
                    self.render_ui(show_prompt=True)
                    continue

                self.log(f"USER@NEURO> {user_input}")
                
                # Global System Commands (Priority 2)
                if user_input.lower() in ["exit", "quit", "shutdown"]:
                    self.log("Shutting down...")
                    self.render_ui(show_prompt=False)
                    self.running = False
                    self.renderer.stop() # Kill GUI
                    break

                # KERNEL ROUTING (LLM)
                self.log("Thinking...")
                self.render_ui(show_prompt=False) # Hide prompt while thinking
                
                llm_response = self._llm_inference(user_input)
                
                # Remove "Thinking..." from log
                # We need to check the active buffer
                target_buffer = self.app_log_lines if self.active_app else self.system_log_lines
                if target_buffer and target_buffer[-1] == "Thinking...":
                    target_buffer.pop()
                
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
    try:
        kernel.run()
    except KeyboardInterrupt:
        print("\n[!] Force Shutdown.")
        sys.exit(0)
