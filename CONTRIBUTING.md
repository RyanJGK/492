# Contributing to 492-Energy-Defense

Thank you for your interest in contributing to this cybersecurity defense system!

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/492-energy-defense.git
   cd 492-energy-defense
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   make init
   ```

## Code Standards

### Python (Backend/AI Agent)

- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

```python
def process_data(input_data: Dict[str, Any]) -> ProcessedResult:
    """
    Process security data and return structured results.
    
    Args:
        input_data: Raw security event data
        
    Returns:
        ProcessedResult: Validated and processed data
        
    Raises:
        ValidationError: If input data is invalid
    """
    pass
```

### JavaScript/React (Frontend)

- Use ES6+ features
- Functional components with hooks
- PropTypes or TypeScript for type checking
- Component naming: PascalCase
- File naming: PascalCase for components, camelCase for utilities

```javascript
/**
 * Dashboard summary component
 * @param {Object} props - Component props
 * @param {Array} props.data - Summary data array
 */
export const DashboardSummary = ({ data }) => {
  // Component implementation
};
```

### SQL

- Use lowercase for SQL keywords
- Indent nested queries
- Add comments for complex queries
- Use meaningful table and column names

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests first (TDD)
   - Implement feature
   - Update documentation

3. **Commit with descriptive messages**
   ```bash
   git commit -m "feat: add vulnerability correlation analysis"
   ```

   Commit types:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes
   - `refactor`: Code refactoring
   - `test`: Test changes
   - `chore`: Build/tooling changes

4. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

1. **Ensure tests pass**
   - All unit tests pass
   - Code coverage maintained or improved
   - No linting errors

2. **Update documentation**
   - Update README if needed
   - Add/update API documentation
   - Include inline code comments

3. **Write clear PR description**
   - What problem does this solve?
   - How does it solve it?
   - Any breaking changes?
   - Screenshots (for UI changes)

4. **Request review**
   - Tag relevant maintainers
   - Address review comments
   - Update PR as needed

## Security Considerations

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP security best practices
- Report security issues privately

## Documentation

- Update README.md for new features
- Add API documentation for new endpoints
- Include architecture docs for major changes
- Provide examples for new functionality

## Code Review Guidelines

### As a Reviewer

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for security issues
- Verify tests are adequate
- Approve when satisfied

### As an Author

- Respond to all comments
- Don't take feedback personally
- Update code based on feedback
- Ask questions if unclear

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release tag
4. Build and test release
5. Deploy to staging
6. Deploy to production

## Questions?

- Check existing issues and discussions
- Join our community chat
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to energy sector cybersecurity! 🛡️**
