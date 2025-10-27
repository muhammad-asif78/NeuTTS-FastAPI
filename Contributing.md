# Contributing to NeuTTS-FastAPI

Thank you for your interest in contributing to NeuTTS-FastAPI! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Provide detailed information including:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment details (OS, Python version, etc.)

### Code Contributions

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the coding standards
4. **Test your changes** thoroughly
5. **Commit your changes** with descriptive commit messages
6. **Push to your fork** and **create a Pull Request**

### Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/NeuTTS-FastAPI.git
   cd NeuTTS-FastAPI
   ```

2. **Install dependencies:**
   ```bash
   pip install uv
   uv sync
   ```

3. **Run tests:**
   ```bash
   uv run pytest
   ```

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where possible
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

### Code Formatting

We use the following tools for code formatting:

```bash
uv run black .          # Format Python code
uv run isort .          # Sort imports
uv run flake8 .         # Check for style issues
```

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Test both CPU and Docker environments

### Documentation

- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update API documentation if endpoints change

## Pull Request Process

1. Ensure your PR description clearly describes the changes
2. Reference any related issues
3. Ensure CI checks pass
4. Wait for review and address any feedback

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.
