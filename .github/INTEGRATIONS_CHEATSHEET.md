# CI/CD Integrations Cheatsheet

## 1. Docker Hub Integration
**Purpose**: Build and push Docker images
**Workflow File**: `.github/workflows/auto-deploy.yml`
**Trigger**: Push to main branch or manual dispatch
**Secrets Required**:
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token

**Manual Test**:
```bash
# Build locally
docker build -t adhd-calendar-backend .

# Test locally
docker run -p 8000:8000 adhd-calendar-backend

# Push to Docker Hub
docker tag adhd-calendar-backend $DOCKERHUB_USERNAME/adhd-calendar-backend:latest
docker push $DOCKERHUB_USERNAME/adhd-calendar-backend:latest
```

## 2. PyPI Package Publishing
**Purpose**: Publish Python package to PyPI
**Workflow File**: `.github/workflows/release.yml`
**Trigger**: Push of version tag (e.g., v1.0.0)
**Secrets Required**:
- `PYPI_TOKEN`: PyPI API token

**Manual Test**:
```bash
# Build package
python -m build

# Test package locally
pip install dist/*.whl

# Publish to PyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD=$PYPI_TOKEN twine upload dist/*
```

## 3. Snyk Security Scanning
**Purpose**: Security vulnerability scanning
**Workflow File**: `.github/workflows/security.yml`
**Trigger**: Push to main/develop, PRs, weekly schedule
**Secrets Required**:
- `SNYK_TOKEN`: Snyk API token

**Manual Test**:
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth $SNYK_TOKEN

# Test locally
snyk test
snyk monitor
```

## 4. SonarCloud Analysis
**Purpose**: Code quality and coverage analysis
**Workflow File**: `.github/workflows/sonarcloud.yml`
**Trigger**: Push to main/develop, PRs
**Secrets Required**:
- `SONAR_TOKEN`: SonarCloud token

**Manual Test**:
```bash
# Install SonarScanner
brew install sonar-scanner

# Run analysis locally
sonar-scanner \
  -Dsonar.projectKey=adhd-calendar-backend \
  -Dsonar.sources=. \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.login=$SONAR_TOKEN
```

## 5. Dependabot Auto-merge
**Purpose**: Automatically merge dependency updates
**Workflow File**: `.github/workflows/dependabot.yml`
**Trigger**: Dependabot PRs
**Secrets Required**: None

**Manual Test**:
```bash
# Check Dependabot status
gh api /repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/dependabot/alerts

# List open Dependabot PRs
gh pr list --author app/dependabot
```

## Common Issues & Solutions

### Docker Hub
- **Issue**: Permission denied
  - **Solution**: Verify Docker Hub credentials and token permissions
- **Issue**: Build fails
  - **Solution**: Check Dockerfile syntax and dependencies

### PyPI
- **Issue**: Package already exists
  - **Solution**: Increment version number
- **Issue**: Invalid token
  - **Solution**: Generate new PyPI token with correct permissions

### Snyk
- **Issue**: No vulnerabilities found
  - **Solution**: Ensure dependencies are properly installed
- **Issue**: False positives
  - **Solution**: Review and adjust severity thresholds

### SonarCloud
- **Issue**: Coverage not reported
  - **Solution**: Ensure pytest-cov is installed and configured
- **Issue**: Analysis fails
  - **Solution**: Check SonarCloud project settings

## Quick Reference

### Trigger Workflows Manually
1. Go to GitHub repository
2. Click "Actions"
3. Select workflow
4. Click "Run workflow"

### Check Workflow Status
```bash
# List recent workflow runs
gh run list

# View specific workflow
gh run view <run-id>
```

### Update Secrets
1. Go to repository Settings
2. Navigate to Secrets and Variables > Actions
3. Click "Update" on existing secret or "New repository secret"

## Best Practices
1. Always test locally before pushing
2. Keep dependencies up to date
3. Monitor security alerts regularly
4. Review code quality reports weekly
5. Maintain proper versioning
