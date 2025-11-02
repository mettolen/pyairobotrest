# Contributing to pyairobotrest

Thank you for your interest in contributing to pyairobotrest! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- An Airobot TE1 thermostat for testing (optional but recommended)

### Development Setup

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/yourusername/pyairobotrest.git
   cd pyairobotrest
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (optional but recommended):

   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Verify the setup**:

   ```bash
   pytest
   mypy src/pyairobotrest
   ruff check src/pyairobotrest
   ```

## 🔧 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style and patterns
- Add docstrings to all public methods and classes
- Update type hints as needed

### 3. Add Tests

All new features and bug fixes must include tests:

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=pyairobotrest --cov-report=term-missing

# Run specific test
pytest tests/test_client.py::test_your_new_test -v
```

**Coverage requirement**: Maintain >95% code coverage.

### 4. Type Checking

Ensure all code passes strict type checking:

```bash
mypy src/pyairobotrest
```

Fix any type errors before submitting your PR.

### 5. Linting

Run ruff to check code style:

```bash
# Check for issues
ruff check src/pyairobotrest tests/

# Auto-fix issues
ruff check --fix src/pyairobotrest tests/
```

### 6. Format Code

Code is automatically formatted with ruff:

```bash
ruff format src/pyairobotrest tests/
```

### 7. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add support for device name setting

- Implement set_device_name method
- Add device name validation (1-20 characters)
- Update tests and documentation"
```

**Commit message guidelines**:

- Use present tense ("Add feature" not "Added feature")
- First line is a brief summary (50 chars or less)
- Add detailed description after a blank line if needed
- Reference issue numbers when applicable

### 8. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## 📋 Code Style Guidelines

### Python Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 88 characters (ruff default)
- Use docstrings for all public classes, methods, and functions

### Docstring Format

Use Google-style docstrings:

```python
async def set_home_temperature(self, temperature: float) -> None:
    """Set HOME mode setpoint temperature.

    Args:
        temperature: Temperature in °C (range: 5.0°C - 35.0°C).

    Raises:
        AirobotConnectionError: If connection fails.
        AirobotAuthError: If authentication fails.
        AirobotError: If the request fails or temperature is out of range.

    Example:
        >>> await client.set_home_temperature(22.5)
    """
```

### Type Hints

All functions must have complete type hints:

```python
async def get_statuses(self) -> ThermostatStatus:
    """Get all thermostat read-only parameters."""

def _validate_temperature(self, temperature: float, temp_type: str) -> None:
    """Validate temperature value."""
```

### Error Handling

- Use specific exception types from `pyairobotrest.exceptions`
- Always include error context in exception messages
- Chain exceptions using `raise ... from err`

```python
try:
    response_data = await response.json()
except aiohttp.ClientError as err:
    raise AirobotConnectionError(
        f"Failed to connect to {url}: {err}"
    ) from err
```

## 🧪 Testing Guidelines

### Test Structure

Tests are located in `tests/` directory:

```
tests/
├── __init__.py
├── test_client.py
├── test_exceptions.py
└── conftest.py  # Shared fixtures
```

### Writing Tests

- Use descriptive test names: `test_set_temperature_raises_error_when_out_of_range`
- Test both success and failure cases
- Mock external dependencies (HTTP communication)
- Use pytest fixtures for common setup

```python
async def test_set_temperature_success(mock_client):
    """Test successful temperature setting."""
    async with AirobotClient("192.168.1.100", "T01XXXXXX", "password") as client:
        await client.set_home_temperature(22.5)
        # Assertions...

async def test_set_temperature_out_of_range(mock_client):
    """Test temperature validation."""
    client = AirobotClient("192.168.1.100", "T01XXXXXX", "password")

    with pytest.raises(AirobotError, match="out of range"):
        await client.set_home_temperature(50.0)
```

### Test Coverage

Check coverage after adding tests:

```bash
pytest --cov=pyairobotrest --cov-report=html
open htmlcov/index.html  # View detailed coverage report
```

## 📖 Documentation

### Update Documentation

When adding features, update:

1. **README.md** - User-facing features
2. **Docstrings** - All public APIs
3. **example.py** - Add usage examples if applicable
4. **CHANGELOG.md** - Document changes (if file exists)

### API Documentation

Public APIs must have comprehensive docstrings:

- Description of what the method does
- All parameters with types and descriptions
- Return value type and description
- All possible exceptions
- Usage examples for complex APIs

## 🐛 Bug Reports

### Before Submitting

- Check existing issues to avoid duplicates
- Test with the latest version
- Gather relevant information:
  - Python version
  - pyairobotrest version
  - Thermostat model and firmware version
  - Error messages and stack traces

### Bug Report Template

```markdown
## Description

Brief description of the bug

## Steps to Reproduce

1. Step one
2. Step two
3. ...

## Expected Behavior

What should happen

## Actual Behavior

What actually happens

## Environment

- Python version: 3.13.9
- pyairobotrest version: 0.1.0
- Thermostat: Airobot TE1
- OS: Linux/Windows/macOS

## Error Messages
```

Paste error messages and stack traces here

```

## Additional Context

Any other relevant information
```

## 💡 Feature Requests

### Proposing New Features

1. **Check existing issues** to see if already proposed
2. **Open a discussion** before implementing large features
3. **Describe the use case** - why is this feature needed?
4. **Propose an API** - how should it work?

### Feature Request Template

```markdown
## Feature Description

What feature would you like to see?

## Use Case

Why is this feature needed? What problem does it solve?

## Proposed API

How should the feature work?

# Example usage

`await client.async_some_new_feature(param=value)`

## Alternatives Considered

What other approaches did you consider?
```

## 🔄 Pull Request Process

### Before Submitting

- [ ] All tests pass: `pytest`
- [ ] Type checking passes: `mypy src/pyairobotrest`
- [ ] Linting passes: `ruff check src/pyairobotrest`
- [ ] Code coverage is maintained (>95%)
- [ ] Documentation is updated
- [ ] Commit messages are clear

### PR Description

Include in your PR:

- **Summary** of changes
- **Motivation** - why is this change needed?
- **Testing** - how was it tested?
- **Breaking changes** - if any
- **Related issues** - link to issues

### Review Process

1. Automated checks will run (tests, linting, type checking)
2. Maintainer will review the code
3. Address any feedback or requested changes
4. Once approved, PR will be merged

### After Your PR is Merged

- Delete your feature branch
- Pull the latest changes from main
- Update your fork

## 🎯 Development Best Practices

### Async/Await

- All I/O operations must be async
- Don't block the event loop
- Use `asyncio.sleep()` not `time.sleep()`

### Error Handling

- Be specific with exception types
- Include helpful error messages
- Don't use bare `except:` clauses

### Performance

- Minimize HTTP requests
- Use session reuse for multiple requests
- Use appropriate timeouts

### Security

- Never log sensitive data (passwords, tokens)
- Validate all user inputs
- Use secure defaults

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Report security issues privately to the maintainers

## 📄 License

By contributing to pyairobotrest, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## 🙏 Thank You!

Your contributions make pyairobotrest better for everyone. We appreciate your time and effort!
