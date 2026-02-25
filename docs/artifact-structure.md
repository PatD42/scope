# Project File Structure

Default guideline to agents on project files location. Adapt based on language and project needs.

**Folders are created only when needed.**

```
project_root/
├── src/
│   ├── shared/
│   │   └── tests/              # Colocated unit tests (TDD)
│   ├── {module}/
│   │   └── tests/              # Colocated unit tests
│   └── tests/                  # Unit tests (if not colocated)
├── config/                     # Application configuration
├── tests/
│   ├── integration/
│   └── e2e/
├── docker/
├── scripts/
├── fixtures/                   # Test data
├── vendor/                     # Vendored dependencies
├── bin/                        # Executables
├── migrations/                 # Database migrations
└── assets/                     # Static files (images, fonts, etc.)
```

## Guidelines

**Source Code (`src/`)**
- Group by module/domain
- Colocate unit tests with source for TDD

**Tests**
- Unit tests: colocated in `src/{module}/tests/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`

**Documentation**
- docs/ is not defined on purpose. Agents must use the `project-documentation` skill to read/write/modify documentation in the local `docs/` directory. The skill defines the folder structure and templates.
