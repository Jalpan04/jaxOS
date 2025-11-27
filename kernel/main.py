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

# Import internal modules
# Note: In a real Unikernel, these would be frozen modules.
try:
    from intent_parser import IntentParser
except ImportError:
    # Handle running from root directory
    sys.path.append('kernel')
    from intent_parser import IntentParser

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:12b"

SYSTEM_PROMPT = """
You are the Kernel of NEURO-CASIO OS, a retro-futurist AI operating system.
Your goal is to interpret user natural language commands and convert them into JSON system calls.

Capabilities:
- File System: create_file, read_file, delete_file, list_files
- System: system_status

Output Format:
You MUST output ONLY valid JSON. No markdown, no explanations.
Schema: {"action": "action_name", "params": {"param1": "value1"}}

Examples:
User: "Create a file named notes.txt saying hello world"
Output: {"action": "create_file", "params": {"path": "notes.txt", "content": "hello world"}}

User: "What files do I have?"
Output: {"action": "list_files", "params": {}}

User: "Delete the notes file"
Output: {"action": "delete_file", "params": {"path": "notes.txt"}}

User: "System status"
Output: {"action": "system_status", "params": {}}
"""

class NeuralKernel:
    def __init__(self):
        self.parser = IntentParser()
        self.running = True
        self.fs_state = {} # Mock in-memory FS for now

    def boot(self):
        print("\033[1;32m") # Green text
        print("========================================")
        print("           j a x O S   v1.0             ")
        print("========================================")
        print(f"[*] Initializing Neural Shim...")
        print(f"[*] Connecting to Cortex ({MODEL_NAME})...")
        
        if self._check_ollama():
            print("[+] Cortex Online.")
        else:
            print("[-] Cortex Offline. Please start Ollama.")
            sys.exit(1)
            
        print("[*] Mounting Vector FS...")
        print("[*] Starting Casio UI Engine...")
        print("========================================")
        print("System Ready. Waiting for intent...")
        print("\033[0m") # Reset

    def _check_ollama(self) -> bool:
        try:
            req = urllib.request.Request(OLLAMA_URL)
            # Just checking connectivity, not sending data yet
            # Actually api/generate expects POST, so a GET might fail 404 or 405, 
            # but connection refused means it's down.
            # Let's try a simple tags list or version check if possible, 
            # but for now just assuming if we can connect it's up.
            # We'll just try to open the base URL or tags endpoint.
            with urllib.request.urlopen("http://localhost:11434/api/tags") as response:
                return response.status == 200
        except urllib.error.URLError:
            return False
        except Exception:
            return False

    def _llm_inference(self, user_input: str) -> str:
        """
        Sends the user input to the local LLM and gets the JSON response.
        """
        payload = {
            "model": MODEL_NAME,
            "prompt": user_input,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": "json" # Force JSON mode if supported by model/ollama version
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", "{}")
        except Exception as e:
            print(f"[!] Inference Error: {e}")
            return "{}"

    def execute_syscall(self, intent: Dict[str, Any]):
        action = intent.get("action")
        params = intent.get("params", {})
        
        print(f"\n[KERNEL] Executing SysCall: {action}")
        
        if action == "create_file":
            path = params.get("path")
            content = params.get("content", "")
            self.fs_state[path] = content
            print(f"[FS] Created {path} ({len(content)} bytes)")
            
        elif action == "read_file":
            path = params.get("path")
            if path in self.fs_state:
                print(f"[FS] Content of {path}:\n{self.fs_state[path]}")
            else:
                print(f"[FS] Error: File {path} not found.")
                
        elif action == "delete_file":
            path = params.get("path")
            if path in self.fs_state:
                del self.fs_state[path]
                print(f"[FS] Deleted {path}")
            else:
                print(f"[FS] Error: File {path} not found.")
                
        elif action == "list_files":
            files = list(self.fs_state.keys())
            print(f"[FS] Files: {files}")
            
        elif action == "system_status":
            print("[SYS] RAM: 16KB / 64KB Used")
            print(f"[SYS] Cortex: {MODEL_NAME} (Active)")
            print("[SYS] Uptime: Forever")
            
        elif action == "unknown":
            print(f"[!] Unknown Intent: {intent.get('reason')}")

    def run(self):
        self.boot()
        
        while self.running:
            try:
                user_input = input("\nUSER@NEURO> ")
                if user_input.lower() in ["exit", "quit", "shutdown"]:
                    print("Shutting down...")
                    break
                
                if not user_input.strip():
                    continue

                print("Thinking...", end="", flush=True)
                llm_response = self._llm_inference(user_input)
                print("\r", end="") # Clear "Thinking..."
                
                intent = self.parser.parse(llm_response)
                self.execute_syscall(intent)
                
            except KeyboardInterrupt:
                print("\n[!] Interrupt detected. Shutting down.")
                break
            except Exception as e:
                print(f"\n[!] Kernel Panic: {e}")

if __name__ == "__main__":
    kernel = NeuralKernel()
    kernel.run()
