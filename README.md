# jaxOS v3.5 🧠
> *A Python-First Simulated Operating System with a Neural Kernel and Unified Grid UI.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-Stable-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![AI](https://img.shields.io/badge/AI-Neural%20Kernel-purple.svg)

**jaxOS** is an experimental operating system simulation that explores the intersection of traditional OS architecture and modern AI. It features a **Neural Kernel** that uses a Large Language Model (LLM) to interpret user intent, a **Unified Grid UI** for consistent application design, and a robust **Filesystem Shell**.

---

## 🚀 Features

### 🧠 Neural Kernel
-   **Intent-Driven Execution**: The kernel parses natural language commands (e.g., "What is the capital of France?") using a local LLM (`gemma3:12b`).
-   **Hybrid Shell**: Supports both traditional commands (`ls`, `cd`) and AI queries.

### 🖥️ Unified Grid UI
-   **Procedural Rendering**: A custom `TkRenderer` draws a retro-futurist, monochrome interface.
-   **Grid Layout Engine**: Applications use a responsive `Panel` and `GridLayout` system.
-   **Apps**:
    -   **Calculator**: A fully functional grid-based calculator.
    -   **SysMon**: Real-time system monitoring (CPU, RAM, Network).
    -   **Notes**: A text editor with toolbar and file I/O.
    -   **Code Studio**: A Python REPL environment.
    -   **Clock**: A digital timer.

### 📦 System Management
-   **Filesystem Shell**: Full support for `ls`, `cd`, `mkdir`, `rmdir`, `cat`, `pwd`.
-   **Package Manager (`map`)**: Install and remove apps dynamically (`map list`, `map install`).
-   **Authentication**: Secure login with password hashing and recovery keys.

---

## 🛠️ Quick Start

### Run from Source
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Jalpan04/jaxOS.git
    cd jaxOS
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Boot the OS**:
    ```bash
    python kernel/main.py
    ```

> **Note**: For AI features, ensure [Ollama](https://ollama.com/) is running with `gemma3:12b`.

---

## 🏗️ Architecture

-   **Kernel**: `kernel/main.py` - The central event loop and syscall handler.
-   **UI**: `ui/tk_renderer.py` - Tkinter-based rendering engine.
-   **Filesystem**: `fs/db.py` - SQLite-backed flat filesystem with virtual directories.
-   **AI Bridge**: `kernel/intent_parser.py` - Interfaces with Ollama for NLU.

See [ARCHITECTURE.md](ARCHITECTURE.md) for a deep dive.

---

## 🤝 Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
