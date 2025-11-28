# jaxOS Architecture

## Overview
jaxOS is a simulated operating system designed to explore **AI-Native** computing. Instead of a traditional kernel that executes compiled code directly, jaxOS uses a **Neural Kernel** loop that interprets natural language intent.

## Core Components

### 1. The Neural Kernel (`kernel/main.py`)
The heart of the OS. It runs a continuous loop:
1.  **Input**: Captures user input (keyboard or UI).
2.  **Routing**: Checks if the input is a system command (`ls`, `launch`) or a natural language query.
3.  **Inference**: If natural language, it sends the query to a local LLM (Gemma 3 via Ollama).
4.  **Intent Parsing**: The LLM response is parsed into a structured JSON intent (e.g., `{"action": "write_file", "params": ...}`).
5.  **Execution**: The kernel executes the corresponding Python function (Syscall).

### 2. The Unified Grid UI (`ui/`)
A custom rendering engine built on Tkinter.
-   **`TkRenderer`**: Handles low-level drawing (lines, text, rectangles) on a canvas.
-   **`Widget` System**: A hierarchy of UI elements (`Label`, `Button`, `Panel`).
-   **`GridLayout`**: A layout manager that automatically arranges widgets in a grid, ensuring a consistent, retro-futurist aesthetic across all apps.

### 3. The Filesystem (`fs/db.py`)
A flat, SQLite-backed filesystem.
-   **Virtual Directories**: Directories are simulated using path prefixes (e.g., `/docs/readme.txt`).
-   **Persistence**: All files are stored in `system.db`.

### 4. Application Runtime (`apps/`)
Applications are Python classes inheriting from `App`.
-   **Lifecycle**: `on_start`, `on_stop`, `on_input`.
-   **Sandboxing**: Apps run within the kernel process but have limited access via the `kernel` object.
-   **Dynamic Loading**: Apps are discovered and loaded at runtime from the `apps/` directory.

## Data Flow
```mermaid
graph TD
    User[User Input] --> Kernel
    Kernel -->|Command?| Shell[Filesystem Shell]
    Kernel -->|NL Query?| LLM[Ollama (Gemma 3)]
    LLM -->|JSON Intent| Parser[Intent Parser]
    Parser -->|Syscall| Kernel
    Kernel -->|Draw| UI[TkRenderer]
    Kernel -->|Read/Write| DB[SQLite FS]
```
