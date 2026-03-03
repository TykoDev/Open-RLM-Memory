# Contributing to Open RLM Memory

Thank you for your interest in contributing to Open RLM Memory! This document provides guidelines for contributing to the project.

## How to Contribute

We welcome contributions in many forms:

- **Reporting Bugs**: Help us fix issues by reporting bugs
- **Suggesting Features**: Request new features or enhancements
- **Writing Code**: Submit pull requests with bug fixes or features
- **Improving Documentation**: Fix typos, improve clarity, add examples
- **Answering Questions**: Help other users in discussions

## Development Setup

Follow these steps to set up your development environment:

### Clone Repository

```bash
git clone https://github.com/TykoDev/open-rlm-memory.git
cd open-rlm-memory
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Configuration

```bash
cp .env.example .env
# Edit .env with your local configuration
```

### Run Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## Submission Guidelines

### Branching Strategy

Use descriptive branch names:

```bash
feature/add-user-authentication
bugfix/memory-delete-error
docs/update-api-documentation
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user authentication
fix: resolve search performance issue
docs: update API documentation
style: format code with ruff
refactor: simplify cache service
test: add unit tests for RLM service
chore: update dependencies
```

### Pull Request Process

1. Update your branch with latest main
2. Ensure all tests pass locally
3. Create pull request to main branch
4. Fill out the PR template completely
5. Link any related issues
6. Request review from maintainers

### Code Review

- Be open to constructive feedback
- Review others' PRs when possible
- Keep feedback constructive and actionable

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8 and use `ruff` for linting
- **Type Hints**: Include type hints on all functions
- **Documentation**: Add docstrings to public classes and methods
- **Testing**: Write tests for new functionality
- **Async**: Use async/await for I/O operations

### TypeScript (Frontend)

- **Style**: Use ESLint with Prettier
- **Type Safety**: No `any` types, enable strict mode
- **Components**: Use functional components with proper typing
- **Testing**: Write tests with Vitest and @testing-library/react

### Testing Requirements

- **Backend**: All PRs must pass `pytest`
- **Frontend**: All PRs must pass `npm run test` and `npm run typecheck`
- **Coverage**: Aim for 80%+ coverage on new code
- **Bug Fixes**: Include regression tests

## Documentation Updates

- Update relevant documentation for user-facing changes
- Update CHANGELOG.md for notable changes
- Ensure code examples are accurate

## Questions?

- Check [Documentation](https://github.com/TykoDev/open-rlm-memory/docs) first
- Search [Issues](https://github.com/TykoDev/open-rlm-memory/issues) for similar questions
- Join [Discussions](https://github.com/TykoDev/open-rlm-memory/discussions) for general conversation

## License

By contributing, you agree that your contributions will be licensed under the [AGPLv3](LICENSE). See also [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md) for commercial licensing.

Thank you for contributing to Open RLM Memory!
