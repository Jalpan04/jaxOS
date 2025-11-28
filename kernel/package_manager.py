import os
from typing import List, Dict, Tuple

class PackageManager:
    def __init__(self, apps_dir: str):
        self.apps_dir = apps_dir
        self.repo = self._init_repo()

    def _init_repo(self) -> Dict[str, str]:
        """Simulates a remote repository with available apps."""
        return {
            "snake": self._get_snake_code(),
            "clock": self._get_clock_code(),
            "todo": self._get_todo_code()
        }

    def list_apps(self) -> List[Tuple[str, str]]:
        """Returns a list of (app_name, status)."""
        result = []
        
        # System Apps
        result.append(("code_studio", "System"))
        result.append(("calculator", "System"))
        
        for app_name in self.repo:
            if self.is_installed(app_name):
                result.append((app_name, "Installed"))
            else:
                result.append((app_name, "Available"))
        return result

    def is_installed(self, app_name: str) -> bool:
        return os.path.exists(os.path.join(self.apps_dir, f"{app_name}.py"))

    def install(self, app_name: str) -> bool:
        """Installs an app from the repo."""
        if app_name not in self.repo:
            return False
        
        code = self.repo[app_name]
        path = os.path.join(self.apps_dir, f"{app_name}.py")
        
        try:
            with open(path, "w") as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Install Error: {e}")
            return False

    def remove(self, app_name: str) -> bool:
        """Removes an installed app."""
        path = os.path.join(self.apps_dir, f"{app_name}.py")
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception:
                return False
        return False

    # --- APP SOURCE CODES ---

    def _get_snake_code(self) -> str:
        return """
from apps.base import App
import random
import time

class Snake(App):
    def on_start(self):
        self.log("SNAKE GAME")
        self.log("Controls: W/A/S/D to move. Q to quit.")
        self.width = 20
        self.height = 10
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = (0, 1) # Down
        self.food = self._spawn_food()
        self.score = 0
        self.game_over = False
        self.last_tick = time.time()
        
    def _spawn_food(self):
        while True:
            food = (random.randint(0, self.height-1), random.randint(0, self.width-1))
            if food not in self.snake:
                return food

    def on_input(self, user_input):
        key = user_input.lower().strip()
        if key == 'w': self.direction = (-1, 0)
        elif key == 's': self.direction = (1, 0)
        elif key == 'a': self.direction = (0, -1)
        elif key == 'd': self.direction = (0, 1)
        elif key == 'q': self.kernel.close_app()
        
        # Manual tick for now since we don't have a game loop
        self._tick()

    def _tick(self):
        if self.game_over:
            return

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Bounds check
        if (new_head[0] < 0 or new_head[0] >= self.height or
            new_head[1] < 0 or new_head[1] >= self.width or
            new_head in self.snake):
            self.game_over = True
            self.log(f"GAME OVER! Score: {self.score}")
            return

        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()
            
        self._render()

    def _render(self):
        # Clear log buffer manually-ish
        self.kernel.app_log_lines = []
        self.log(f"Score: {self.score}")
        
        board = [['.' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw Food
        board[self.food[0]][self.food[1]] = '*'
        
        # Draw Snake
        for r, c in self.snake:
            board[r][c] = '#'
            
        for row in board:
            self.log("".join(row))
        
        self.kernel.render_ui()
"""

    def _get_clock_code(self) -> str:
        return """
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
"""

    def _get_todo_code(self) -> str:
        return """
from apps.base import App

class Todo(App):
    def on_start(self):
        self.log("TODO LIST")
        self.log("Commands: add <item>, del <index>, list, quit")
        self.tasks = []

    def on_input(self, user_input):
        parts = user_input.split(" ", 1)
        cmd = parts[0].lower()
        
        if cmd == "quit":
            self.kernel.close_app()
        elif cmd == "add" and len(parts) > 1:
            self.tasks.append(parts[1])
            self.log(f"Added: {parts[1]}")
        elif cmd == "list":
            self.log("--- TASKS ---")
            for i, task in enumerate(self.tasks):
                self.log(f"{i}. {task}")
        elif cmd == "del" and len(parts) > 1:
            try:
                idx = int(parts[1])
                removed = self.tasks.pop(idx)
                self.log(f"Removed: {removed}")
            except:
                self.log("Invalid index")
        else:
            self.log("Unknown command")
"""
