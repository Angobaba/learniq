# Contributing to LearnIQ

Thank you for your interest in contributing! Please follow the guidelines below to keep the project clean and maintainable.

---

## Branch Naming

Use the following prefixes:

| Prefix | Purpose |
|--------|---------|
| `feature/` | New features or enhancements |
| `fix/` | Bug fixes |
| `docs/` | Documentation-only changes |
| `refactor/` | Code refactoring without functional change |
| `test/` | Adding or improving tests |
| `chore/` | Maintenance tasks (dependencies, CI, etc.) |

Examples:
- `feature/adaptive-quiz`
- `fix/citation-dedup`
- `docs/architecture-update`

---

## Pull Requests

1. **Fork** the repository and create your branch from `main`.
2. Make your changes, keeping commits **small and focused**.
3. Write or update **tests** for any logic changes.
4. Run the test suite before opening the PR:
   ```bash
   pytest tests/ -v
   ```
5. Ensure your code follows the existing style (PEP 8, docstrings).
6. Open a PR with:
   - A clear title describing the change.
   - A description explaining **what** changed and **why**.
   - A reference to the related issue (e.g., `Closes #12`).
7. PRs must pass all CI checks before merging.
8. At least **one reviewer approval** is required before merge.

---

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use descriptive variable names.
- Add docstrings to all public functions and classes.
- Keep functions small and single-purpose.

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
- `feat(rag): add hybrid retrieval support`
- `fix(qa_chain): handle empty LLM response`
- `docs(readme): update setup instructions`

---

## Reporting Issues

Use GitHub Issues to report bugs or request features. Please include:
- A clear description of the problem.
- Steps to reproduce (for bugs).
- Expected vs. actual behaviour.
- Environment details (Python version, OS, etc.).

---

## Code of Conduct

Be respectful and constructive. This project is intended for educational use and collaboration.
