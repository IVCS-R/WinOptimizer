# AGENTS.md

## Conventions

### Versioning
- Every time significant changes are made, bump the version number
- Update `VERSION` in `optimizer.py` AND the docstring header
- Follow semver: `MAJOR.MINOR.PATCH`
  - MAJOR: breaking changes
  - MINOR: new features, fixes
  - PATCH: small fixes
- Git commit message must include version: `"release vX.Y.Z: description"`

### Git
- Always include version in commit message for releases
- Never commit secrets, keys, or personal data
- Always run `git status` before committing

### Code
- No bare `except:` — always `except Exception:`
- No `shell=True` in subprocess unless necessary
- Handle missing dependencies gracefully (try/except import)
