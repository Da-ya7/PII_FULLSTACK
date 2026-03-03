# Contributing to Secure PII Redaction System

Thank you for considering contributing to this project! Here's how you can help.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. Create a **feature branch** (`git checkout -b feature/your-feature`)
4. Make your changes
5. **Test** thoroughly (see [TESTING_GUIDE.md](TESTING_GUIDE.md))
6. **Commit** with clear messages (`git commit -m "feat: add X detection"`)
7. **Push** to your fork (`git push origin feature/your-feature`)
8. Open a **Pull Request**

## Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix     | Purpose                        |
|------------|--------------------------------|
| `feat:`    | New feature                    |
| `fix:`     | Bug fix                        |
| `docs:`    | Documentation changes          |
| `refactor:`| Code restructuring             |
| `test:`    | Adding or updating tests       |
| `chore:`   | Maintenance / tooling          |

## Code Style

- Follow **PEP 8** for Python code
- Add docstrings to all public functions and modules
- Keep functions focused and under 50 lines where possible

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce, expected vs. actual behavior, and environment details

## Adding New PII Detectors

1. Add regex patterns to `modules/regex_detector.py`
2. Add policy entries to `modules/rag_decision_engine.py`
3. Update `TESTING_GUIDE.md` with test cases
4. Add sample test images if applicable

---

All contributions are appreciated!
