# Spec Validator Skill

Validates technical specifications in `docs/architecture/13-specs/` directory for correctness and completeness.

## Purpose

Ensures specs are valid and ready for Claude Flow consumption:
1. Validate YAML/JSON syntax
2. Validate format compliance (OpenAPI, JSON Schema)
3. Check cross-references between specs
4. Verify error taxonomy completeness

## Functions

### validate_api(service_name)

Validate an API contract file.

```python
def validate_api(service_name: str) -> dict:
    """
    Validate OpenAPI 3.0.3 contract.

    Args:
        service_name: Service name (e.g., "auth" for auth.yaml)

    Returns:
        {
            "valid": true/false,
            "file": "docs/architecture/13-specs/api/auth.yaml",
            "errors": [],
            "warnings": []
        }
    """
```

**Checks:**
- Valid OpenAPI 3.0.3 structure
- All `$ref` references resolve
- All error responses reference valid error codes
- Request/response schemas are valid
- Security schemes defined if used
- Changelog present

### validate_schema(entity_name)

Validate a domain schema file.

```python
def validate_schema(entity_name: str) -> dict:
    """
    Validate JSON Schema Draft 2020-12.

    Args:
        entity_name: Entity name (e.g., "user" for user.yaml)

    Returns:
        {
            "valid": true/false,
            "file": "docs/architecture/13-specs/schemas/domain/user.yaml",
            "errors": [],
            "warnings": []
        }
    """
```

**Checks:**
- Valid JSON Schema Draft 2020-12
- `$id` matches filename
- Required properties list is accurate
- Type constraints are valid
- Changelog present

### validate_database(type, name)

Validate a database spec file.

```python
def validate_database(db_type: str, name: str) -> dict:
    """
    Validate database schema spec.

    Args:
        db_type: Database type (sql, nosql, graph, vector)
        name: Table/collection name

    Returns:
        {
            "valid": true/false,
            "file": "docs/architecture/13-specs/database/sql/users.sql",
            "errors": [],
            "warnings": []
        }
    """
```

**Checks by type:**

**SQL:**
- Valid SQL DDL syntax
- Primary key defined
- Foreign key references valid
- Indexes documented

**NoSQL:**
- Valid YAML structure
- Indexes defined
- Validation rules present

**Graph:**
- Node/relationship definitions valid
- Cypher/Gremlin examples syntactically correct

**Vector:**
- Embedding dimensions match model
- Index configuration valid

### validate_errors(domain)

Validate error codes for a domain.

```python
def validate_errors(domain: str) -> dict:
    """
    Validate domain error codes.

    Args:
        domain: Domain name (e.g., "auth")

    Returns:
        {
            "valid": true/false,
            "file": "docs/architecture/13-specs/errors/by-domain/auth.yaml",
            "errors": [],
            "warnings": [],
            "taxonomy_sync": true/false  # All codes in taxonomy?
        }
    """
```

**Checks:**
- Valid YAML structure
- Code format matches `{PREFIX}_{NNN}`
- HTTP status codes are valid
- All codes exist in taxonomy.yaml
- No duplicate codes

### validate_all()

Validate all specs in the directory.

```python
def validate_all() -> dict:
    """
    Validate all specs in docs/architecture/13-specs/ directory.

    Returns:
        {
            "valid": true/false,
            "summary": {
                "api": {"total": 3, "valid": 3, "invalid": 0},
                "schemas": {"total": 5, "valid": 4, "invalid": 1},
                "database": {"total": 2, "valid": 2, "invalid": 0},
                "errors": {"total": 4, "valid": 4, "invalid": 0}
            },
            "errors": [...],
            "warnings": [...]
        }
    """
```

## Usage

### From Architect-Reviewer Agent

```python
# Validate all specs during epic review
result = Skill(skill="spec-validator", args="validate_all")

if not result["valid"]:
    # Report validation errors as concerns
    concerns = []
    for error in result["errors"]:
        concerns.append({
            "severity": "critical",
            "category": "spec_validation",
            "description": error["message"],
            "location": error["file"]
        })
```

### From Update Spec Command

```python
# After modifying a spec
result = Skill(skill="spec-validator", args=f"validate_api {service_name}")

if result["valid"]:
    Output: f"Spec validation: PASSED"
else:
    Output: f"Spec validation: FAILED\n{result['errors']}"
```

## Validation Rules

### OpenAPI 3.0.3 Requirements

- `openapi: "3.0.3"` version string
- `info.title` and `info.version` required
- At least one path defined
- All `$ref` paths valid
- Response schemas defined

### JSON Schema Requirements

- `$schema` points to Draft 2020-12
- `$id` matches entity name
- `type: object` for entities
- `properties` defined
- `required` array present

### Error Code Requirements

- Format: `{PREFIX}_{NNN}` (3-5 letter prefix, 3 digit number)
- `http_status` is valid HTTP status code (400-599)
- `message` is present and non-empty
- `retry` boolean is defined
- `added_by` tracks origin

## Error Messages

```yaml
# Missing taxonomy entry
error: "Error code AUTH_005 not found in taxonomy.yaml"
fix: "Add AUTH_005 to docs/architecture/13-specs/errors/taxonomy.yaml all_codes section"

# Invalid reference
error: "API ref '../schemas/domain/user.yaml' does not exist"
fix: "Create user.yaml schema or fix the reference path"

# Duplicate code
error: "Duplicate error code VAL_001 in validation.yaml and input.yaml"
fix: "Rename one of the codes or consolidate into single domain"
```

## Integration Points

This skill is used by:
- `architect-reviewer` agent during epic_review phase
- `/update_spec` command after modifications
- `spec-merger` skill before consolidation
