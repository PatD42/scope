Create epic, story, task, or bug interactively via product-owner agent.

**Syntax:** `/create {type} {description}`

**Types:** `epic` | `story` | `task` | `bug`

## Examples

```
/create epic User authentication with OAuth2 and MFA support
/create story Add password reset functionality
/create task Update dependencies to latest versions
/create bug There is a bug in story 14. The embeddings are not using the right model.
```

## Execution

1. Parse type and initial description
2. Load `.scope/config.yaml`:
   - `management_skill` = config.skills.management
   - `documentation_skill` = config.skills.documentation
   - `project_key` = config.project.key
3. Auto-detect project_key references in description:
   - "story 14" → SCOPE-14
   - "SCOPE-42" → SCOPE-42
   - "epic 3" → SCOPE-3
4. Spawn/resume product-owner with create context:
   ```
   Phase: Other

   Create a {type} for project {project_key}.

   Use skills: {management_skill}, {documentation_skill}

   Initial description: {description}
   Detected parent: {parent_key or "none"}

   Artifact creation rules:
   - Epic: management work item + documentation page with labels
   - Story: management work item + documentation page with labels
   - Task: management work item only (no documentation page)
   - Bug: management work item only (no documentation page)

   Ask clarifying questions based on issue type, then create.
   Return status: user_input until all questions answered.
   ```
5. Product-owner asks type-specific questions
6. User answers (multi-turn conversation)
7. Product-owner creates:
   - Work item via management skill (all types)
   - Documentation page via documentation skill (epic and story only)
8. Display output with created item details and next-step recommendation

## Question Templates

### Epic
- What is the business value?
- What are the success metrics?
- What is in scope? What is explicitly out of scope?
- Are there any known constraints or dependencies?

### Story
- What are the acceptance criteria?
- Are there dependencies on other stories?
- (Optional) Parent epic? Use auto-detected if present, otherwise skip or let user specify. Can be assigned later.

### Task
- What is the definition of done?
- (Optional) Parent story or epic? Use auto-detected if present, otherwise skip or let user specify. Can be assigned later.

### Bug
- Steps to reproduce?
- Expected behavior?
- Actual behavior?
- Severity? (critical/high/medium/low)
- (Optional) Affected component/story? Use auto-detected if present, otherwise skip. User may not know.

## Artifact Creation

| Type | Management | Documentation |
|------|------------|---------------|
| Epic | Create work item | Create page with labels |
| Story | Create work item | Create page with labels |
| Task | Create work item | No page |
| Bug | Create work item | No page |

## Output

On success, display:
- Work item key and URL
- Documentation page URL (if created)
- Parent link (if applicable)
- Labels applied (if documentation page created)

**Next step recommendation:**
- **For Epic:** `Next: /workplan {epic-id}`
- **For Story:** Suggest assigning to epic or starting implementation
- **For Task/Bug:** No specific recommendation (depends on workflow)

## Error Handling

**No config:**
```
Error: No .scope/config.yaml found.

Please create .scope/config.yaml for your project.
```

**Invalid type:**
```
Error: Invalid type '{type}'.

Valid types: epic, story, task, bug

Example: /create story Add user profile page
```

**Missing description:**
```
Error: Description is required.

Usage: /create {type} {description}

Example: /create epic User authentication system
```
