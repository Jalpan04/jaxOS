# Contributing to jaxOS

Thank you for your interest in contributing to jaxOS! We welcome pull requests from developers of all skill levels.

## 🚀 Getting Started

1.  **Fork the Repository**: Click the "Fork" button on GitHub.
2.  **Clone your Fork**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/jaxOS.git
    cd jaxOS
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up AI**: Ensure you have [Ollama](https://ollama.com/) installed and run `ollama pull gemma3:12b`.

## 🛠️ Development Workflow

1.  **Create a Branch**: `git checkout -b feature/my-cool-feature`
2.  **Code**:
    -   **Apps**: Create new apps in `apps/`. Use `apps/template.py` as a guide.
    -   **Kernel**: Core logic goes in `kernel/`. Be careful with the event loop!
    -   **UI**: Add new widgets in `ui/widgets.py`.
3.  **Test**: Run `python kernel/main.py` and verify your changes.
4.  **Commit**: Use clear commit messages (e.g., "feat: Added Weather app").
5.  **Push**: `git push origin feature/my-cool-feature`
6.  **Pull Request**: Open a PR on the main repository.

## 🎨 Design Guidelines

-   **Aesthetic**: Stick to the "Cyberpunk/Retro" terminal look. Green text, black background.
-   **Code Style**: Follow PEP 8. Keep functions small and readable.
-   **No Assets**: Do not add images or binary assets. Use procedural drawing.

## 🐛 Reporting Bugs

Please open an issue on GitHub with:
-   Steps to reproduce.
-   Expected behavior vs. actual behavior.
-   Screenshots (if applicable).

