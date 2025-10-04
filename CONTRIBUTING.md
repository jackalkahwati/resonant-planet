# Contributing to Resonant Worlds Explorer

Thank you for your interest in contributing to Resonant Worlds Explorer! We welcome contributions from the community to help us in the search for exoplanets and biosignatures.

## 🌟 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue describing:
- The problem your feature would solve
- Proposed solution or implementation
- Any relevant examples or references

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write or update tests**
5. **Run the test suite**
   ```bash
   cd backend
   pytest
   ```
6. **Commit with clear messages**
   ```bash
   git commit -m "Add: Description of your changes"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request**

## 🔬 Development Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and modular
- Write unit tests for new features

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable
- Add proper error handling

### Git Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Keep first line under 72 characters
- Add detailed description if needed

Examples:
```
Add: Support for TESS short cadence data
Fix: Phase folding error for long-period planets
Update: Improve biosignature confidence calculation
```

## 🧪 Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Add integration tests for new features
- Test with real NASA data when possible

## 📝 Documentation

- Update relevant documentation files
- Add docstrings to new functions
- Update README if adding major features
- Include examples in docstrings

## 💡 Areas for Contribution

### High Priority
- [ ] GPU acceleration for BLS search
- [ ] WebSocket support for real-time updates
- [ ] Multi-planet search with TTVs
- [ ] Additional biosignature molecules

### Medium Priority
- [ ] Radial velocity follow-up tools
- [ ] Atmospheric retrieval models
- [ ] Batch processing optimization
- [ ] Mobile-responsive UI improvements

### Documentation
- [ ] Video tutorials
- [ ] Jupyter notebook examples
- [ ] API usage examples
- [ ] Translation to other languages

## 🤔 Questions?

Feel free to:
- Open an issue for discussion
- Join our community discussions
- Reach out via GitHub

Thank you for helping advance exoplanet science! 🌌

