
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
