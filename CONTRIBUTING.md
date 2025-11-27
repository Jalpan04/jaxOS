# Contributing to NEURO-CASIO OS

Thank you for your interest in this research project. We are exploring the frontiers of AI-Native Operating Systems.

## Code Style & Standards

### 1. The "Python-First" Philosophy
- **Python is the Kernel:** All logic that *can* be written in Python *must* be written in Python.
- **C is for Plumbing:** Use C only for low-level hardware access or performance-critical FFI bridges.

### 2. Formatting
- We follow **PEP 8**.
- Use **Black** for code formatting.
- **Type Hints** are mandatory for all function signatures.
  ```python
  def calculate_vector(input_str: str) -> list[float]:
      ...
  ```

### 3. Documentation
- Every module and class must have a Docstring explaining its role in the "Neural Architecture".
- Comments should explain the *why*, not just the *how*.

## Development Workflow

1. **Fork & Clone** the repository.
2. **Install Dependencies:** `pip install -r requirements.txt` (if applicable).
3. **Run the Kernel:** Test your changes by running `kernel/main.py`.
4. **Submit a Pull Request** with a detailed description of your architectural changes.

## Training the Kernel
If you are modifying the `_llm_runtime` or the system prompts:
- Ensure you are using `gemma3:12b` as the baseline model.
- Document any prompt engineering changes in `kernel/intent_parser.py`.
