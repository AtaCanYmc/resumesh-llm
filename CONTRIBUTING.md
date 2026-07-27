# Contributing to resumesh-llm

First off, thank you for considering contributing to `resumesh-llm`! Contributions make the open-source community an amazing place to learn, inspire, and create.

---

## 🛠️ Development Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/AtaCanYmc/resumesh-llm.git
    cd resumesh-llm
    ```

2.  **Create a Virtual Environment & Install Dependencies**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    pip install -e .
    ```

3.  **Setup Pre-Commit Hooks**:
    ```bash
    pre-commit install
    ```

---

## 🎨 Styling & Linting Standards

We enforce strict style boundaries using **Ruff**.
Before pushing code, format your changes:
```bash
pre-commit run --all-files
```

---

## 🧪 Testing Guidelines

Make sure to write unit tests for any new features or bug fixes.
Run pytest to verify all tests pass:
```bash
PYTHONPATH=src pytest
```

---

## 💬 Commit Guidelines (Conventional Commits)

We use Google's **release-please** to manage version updates and write changelogs automatically. This requires commit messages to follow the Conventional Commits specification:

-   `feat:` A new capability for the library (triggers a minor version bump: `v0.1.0` -> `v0.2.0`).
-   `fix:` A bug fix (triggers a patch version bump: `v0.1.0` -> `v0.1.1`).
-   `docs:` Changes to documentation only.
-   `style:` Formatting, missing semi-colons, etc. (no production code changes).
-   `refactor:` A code change that neither fixes a bug nor adds a feature.
-   `test:` Adding missing tests or correcting existing tests.

For breaking changes, append a `!` to the type:
```text
feat!: breaking change description here

BREAKING CHANGE: Description of what changed and how to migrate.
```
