# Spec Merger Skill

Validates and proposes merges for technical specifications in `docs/architecture/13-specs/` directory. **All changes require explicit human approval.**

## Critical: Human Approval Required

**Technical specifications are system-critical documents.** This skill:
- **NEVER** auto-updates specs
- **ALWAYS** shows proposed changes to user
- **ALWAYS** waits for explicit approval before any modification
- **EXPLAINS** why each change is needed

## Purpose

When epics generate specs, this skill helps:
1. Validate spec cross-references
2. Detect conflicts between specs
3. **Propose** error code merges into taxonomy (requires approval)
4. **Suggest** schema consolidation opportunities (requires approval)

## Functions

### merge_errors(epic_id)

Proposes error code merges from an epic's work into the main taxonomy.

```python
def merge_errors(epic_id: str) -> dict:
    """
    Analyze epic-specific error codes and propose taxonomy updates.
    DOES NOT MODIFY FILES - only proposes changes for user approval.

    Args:
        epic_id: Epic identifier (e.g., "SCOPE-42")

    Returns:
        {
            "proposed_changes": [
                {
                    "file": "docs/architecture/13-specs/errors/taxonomy.yaml",
                    "action": "add",
                    "section": "all_codes",
                    "content": {...},
                    "reason": "New error code AUTH_004 defined in auth.yaml"
                }
            ],
            "conflicts": [],
            "approval_required": true
        }
    """
```

**Implementation:**
1. Read all `docs/architecture/13-specs/errors/by-domain/*.yaml` files
2. Find codes with `added_by: {epic_id}`
3. Check if they exist in `taxonomy.yaml`
4. **Present proposed changes to user:**

```
## Proposed Spec Updates for {epic_id}

### Error Taxonomy Updates

The following error codes need to be added to `docs/architecture/13-specs/errors/taxonomy.yaml`:

| Code | Domain | HTTP Status | Message | Reason |
|------|--------|-------------|---------|--------|
| AUTH_004 | auth | 401 | Session expired | Defined in auth.yaml during epic refinement |
| AUTH_005 | auth | 403 | Account locked | Defined in auth.yaml during epic refinement |

### Files to Modify

1. `docs/architecture/13-specs/errors/taxonomy.yaml`
   - Add AUTH_004 to all_codes section
   - Add AUTH_005 to all_codes section

**Approve these changes?**
```

5. **Wait for user approval via AskUserQuestion**
6. Only proceed if user explicitly approves

### validate_specs()

Validate all specs for consistency (read-only, no changes).

```python
def validate_specs() -> dict:
    """
    Validate all specs in docs/architecture/13-specs/ directory.
    Read-only operation - does not modify any files.

    Returns:
        {
            "valid": true/false,
            "errors": [],
            "warnings": []
        }
    """
```

### detect_conflicts()

Detect conflicting definitions across specs (read-only).

```python
def detect_conflicts() -> dict:
    """
    Find conflicts between spec files.
    Read-only operation - does not modify any files.

    Returns:
        {
            "conflicts": [
                {
                    "type": "duplicate_error_code",
                    "code": "AUTH_005",
                    "locations": ["auth.yaml:15", "session.yaml:23"],
                    "recommendation": "Rename one code or consolidate domains"
                }
            ]
        }
    """
```

### propose_consolidation()

Suggest schema consolidation opportunities (proposals only).

```python
def propose_consolidation() -> dict:
    """
    Find opportunities to consolidate schemas.
    Does NOT modify files - only suggests changes.

    Returns:
        {
            "suggestions": [
                {
                    "type": "extract_common",
                    "schemas": ["user.yaml", "admin.yaml"],
                    "common_properties": ["id", "email", "created_at"],
                    "suggestion": "Extract to base-user.yaml",
                    "impact": "Reduces duplication, improves consistency"
                }
            ],
            "requires_manual_review": true
        }
    """
```

## Approval Workflow

### Step 1: Analyze and Propose

```python
# Analyze what needs to change
result = Skill(skill="spec-merger", args="merge_errors SCOPE-42")

# Display proposed changes to user
Output: """
## Proposed Spec Updates

{detailed_changes}

These changes are needed because:
- {reason_1}
- {reason_2}
"""
```

### Step 2: Ask for Approval

```python
response = AskUserQuestion(
    questions=[{
        "question": "Approve the proposed spec updates?",
        "header": "Spec Update",
        "options": [
            {"label": "Approve", "description": "Apply the proposed changes to docs/architecture/13-specs/"},
            {"label": "Modify", "description": "I want to adjust the changes first"},
            {"label": "Reject", "description": "Do not make any changes"}
        ],
        "multiSelect": False
    }]
)
```

### Step 3: Apply Only If Approved

```python
if response == "Approve":
    # Now apply the changes
    Skill(skill="spec-merger", args="apply_approved_changes SCOPE-42")
    Output: "Spec updates applied successfully."
elif response == "Modify":
    Output: "Please describe what changes you'd like to make."
    # Wait for user input, then re-propose
else:
    Output: "Spec updates cancelled. No changes made."
```

## Usage

### From Architect Agent (spec_generation phase)

```python
# After generating specs, propose taxonomy updates
result = Skill(skill="spec-merger", args="merge_errors {epic_id}")

if result["proposed_changes"]:
    # Display changes and ask for approval
    Output: format_proposed_changes(result)

    approval = AskUserQuestion(...)

    if approval == "Approve":
        Skill(skill="spec-merger", args="apply_approved_changes {epic_id}")
```

### From /update_spec Command

```python
# After manual spec edits, validate and propose sync
result = Skill(skill="spec-merger", args="validate_specs")

if not result["valid"]:
    Output: f"Validation errors found:\n{result['errors']}"
    Output: "Please fix these issues before proceeding."
```

## What This Skill Does NOT Do

- **Does NOT** auto-merge error codes
- **Does NOT** auto-update taxonomy.yaml
- **Does NOT** modify specs without explicit approval
- **Does NOT** consolidate schemas automatically
- **Does NOT** resolve conflicts automatically

## Error Handling

If user rejects changes:

```yaml
status: pending_approval
message: "Spec updates pending user approval"
proposed_changes: [...]
action_required: "User must approve changes via AskUserQuestion"
```

If conflicts detected:

```yaml
status: conflict
message: "Cannot merge - conflicts detected"
conflicts: [...]
action_required: "User must manually resolve conflicts"
```

## Integration

This skill is typically invoked:
1. After architect completes spec_generation phase
2. Before epic transitions to ready-for-implementation
3. When /update_spec command modifies specs

**All invocations that modify files require user approval.**
