# Version Control & Development Workflow

## Git Configuration

### Repository Information
- **Repository**: `automl`
- **Owner**: `kulbirminhas-aiinitiative`
- **Main Branch**: `main`
- **Remote**: `git@github.com:kulbirminhas-aiinitiative/automl.git`

### Current Version: v1.1.0 ✅

## Branching Strategy

### Main Branches
- **`main`**: Production-ready code
  - Protected branch
  - Requires pull request reviews
  - All tests must pass before merge

### Development Workflow
```
main
├── feature/sklearn-fixes (merged)
├── feature/testing-infrastructure (merged)
└── feature/dataset-management (merged)
```

### Branch Naming Convention
- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/issue-description`
- **Hot fixes**: `hotfix/critical-issue`
- **Release branches**: `release/v1.x.x`

## Version Tagging

### Semantic Versioning (SemVer)
Format: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Current Tags
- `v1.1.0`: scikit-learn fixes and testing infrastructure
- `v1.0.0`: Initial AutoML application

### Tagging Commands
```bash
# Create annotated tag
git tag -a v1.2.0 -m "Version 1.2.0: Description"

# Push tag to remote
git push origin v1.2.0

# List all tags
git tag -l
```

## Commit Message Convention

### Format
```
type(scope): description

body (optional)
footer (optional)
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```bash
feat(api): add model suggestion endpoint
fix(serialization): resolve numpy type JSON errors
docs(readme): update installation instructions
test(api): add comprehensive endpoint testing
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: implement new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
# Merge after review and tests pass
```

### 2. Bug Fixes
```bash
# Create fix branch
git checkout -b fix/bug-description

# Fix the issue
git add .
git commit -m "fix: resolve specific bug"

# Push and create PR
git push origin fix/bug-description
```

### 3. Release Process
```bash
# Create release branch
git checkout -b release/v1.2.0

# Update version numbers, changelog
git add .
git commit -m "chore: prepare v1.2.0 release"

# Merge to main
git checkout main
git merge release/v1.2.0

# Tag the release
git tag -a v1.2.0 -m "Version 1.2.0 release"

# Push everything
git push origin main
git push origin v1.2.0
```

## File Management

### .gitignore Configuration
```gitignore
# Python
venv/
__pycache__/
*.pyc

# Data files
data/*.csv
data/*.json
!data/sample_data.csv

# Models
*.pkl
*.joblib

# Logs
logs/
*.log

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
```

### What to Commit
✅ **Include**:
- Source code
- Configuration files
- Documentation
- Tests
- Requirements files
- Sample data (small files)

❌ **Exclude**:
- Virtual environments
- Large datasets
- Model files
- Logs
- IDE settings
- OS-specific files

## Continuous Integration

### GitHub Actions Workflow (Future)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/
```

## Code Review Process

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

## Rollback Strategy

### Quick Rollback
```bash
# Revert last commit
git revert HEAD

# Revert specific commit
git revert <commit-hash>

# Reset to previous tag
git reset --hard v1.0.0
```

### Emergency Hotfix
```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-issue

# Fix the issue
git add .
git commit -m "hotfix: resolve critical security issue"

# Merge directly to main
git checkout main
git merge hotfix/critical-issue

# Tag and deploy immediately
git tag -a v1.1.1 -m "Hotfix v1.1.1"
git push origin main v1.1.1
```

## Repository Health

### Current Status: ✅ HEALTHY
- All files properly tracked
- No sensitive data committed
- Documentation up to date
- Testing framework in place
- Version tags applied

### Maintenance Tasks
- [ ] Regular dependency updates
- [ ] Security vulnerability scans
- [ ] Performance monitoring
- [ ] Documentation reviews
- [ ] Test coverage analysis

## Commands Reference

### Daily Development
```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "type: description"

# Push to remote
git push origin branch-name

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# View commit history
git log --oneline
```

### Release Management
```bash
# List tags
git tag -l

# Create tag
git tag -a v1.2.0 -m "Version 1.2.0"

# Push tag
git push origin v1.2.0

# Delete tag (local)
git tag -d v1.2.0

# Delete tag (remote)
git push origin --delete v1.2.0
```
