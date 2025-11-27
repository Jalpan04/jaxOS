# jaxOS
> *A Python-First Unikernel with a Neural Inference Loop and Generative UI.*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-Research%20Prototype-orange.svg)

## 1. Abstract
**NEURO-CASIO OS** represents a paradigm shift from traditional interrupt-driven operating systems to an **AI-Native, Intent-Driven Architecture**. By replacing the traditional `while(1)` kernel loop with a continuous **Inference Loop**, the OS moves beyond rigid system calls to fluid, semantic intent execution.

This project implements the "Python Paradox" architecture: a minimal C/Assembly shim that immediately yields control to a high-performance Python runtime, proving that modern embedded Python is sufficient for kernel-space logic when augmented with Neural capabilities.

## 2. Architectural Pillars

### 2.1 The Neural Kernel (Cortex Layer)
Unlike Linux or Windows, the kernel does not wait for hardware interrupts in a vacuum. It actively polls a Large Language Model (LLM) to interpret the user's high-level intent.
- **Traditional:** `User Input -> Scancode -> Driver -> SysCall`
- **Neuro-Casio:** `User Input -> Tokenization -> LLM Inference -> Semantic Intent -> Python Function`

### 2.2 The Semantic File System (Vector Space)
We discard the hierarchical directory structure (inode/FAT) in favor of a **High-Dimensional Vector Space**.
- Files are addressed by their semantic content, not their path.
- Retrieval is performed via Cosine Similarity search.
- `fs.open("that budget report from last week")` works natively.

### 2.3 The "Casio" Visual Engine
A generative, code-only UI system inspired by retro-futurist digital watch aesthetics.
- No bitmaps or static assets.
- All UI elements are drawn procedurally using vector primitives.
- The UI state is hallucinated by the LLM based on the current context.

## 3. Simulation & Usage

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) running locally
- Model: `gemma3:12b` (`ollama pull gemma3:12b`)

### Running the Simulation
This codebase simulates the Unikernel environment on your host OS.

1. **Start Ollama:**
   Ensure Ollama is running and listening on port 11434.

2. **Boot the Kernel:**
   ```bash
   python kernel/main.py
   ```

3. **Interaction:**
   The "Natural Shell" will accept raw English commands.
   > "Create a file named notes.txt with a reminder to buy milk."
   > "Show me the system status."

## 4. Directory Structure
- `/boot`: Minimal bootloader stubs (Assembly/C).
- `/hal`: Hardware Abstraction Layer and C-FFI bindings.
- `/kernel`: The core Python runtime and Neural Loop.
- `/fs`: Vector-based file system implementation.
- `/ui`: Procedural graphics engine.
- `/tools`: Build and simulation scripts.

## 5. Research Goals
- Validate the latency/utility trade-off of an LLM-driven kernel loop.
- Demonstrate the viability of "Python-on-Bare-Metal" for complex OS logic.
- Explore non-hierarchical file organization paradigms.
