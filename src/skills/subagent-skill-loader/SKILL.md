---
name: subagent-skill-loader
description: Load technology skill files into context based on story requirements. Conservative approach - only loads skills when clearly needed. Flags missing critical expertise.
---

# Subagent Skill Loader

## Purpose

Load skill files into context when story requires specialized expertise.

**Conservative approach**: Only load skills when clearly needed. It's OK if no skills are loaded.

## API

```python
analyze_and_load(story_id)
```

## How It Works

1. Read story (description, acceptance criteria, files)
2. Match against skills catalog descriptions
3. Read matching skill files: `Read(skill.path)`
4. Flag if critical expertise missing

## Loading Mechanism

**Read files, don't invoke**:

```python
catalog = read_json(".scope/skills_catalog.json")
story = get_story(story_id)

# Match story technologies against catalog
matches = []
for skill in catalog["skills"]:
    if technology_mentioned_in_story(story, skill["description"]):
        matches.append(skill)

# Load matched skills by reading files
for skill in matches:
    Read(skill["path"])  # Path includes /SKILL.md

return [skill["name"] for skill in matches]
```

**Don't use** `Skill(skill="name")` - that invokes the skill. Read the file instead.

## Conservative Loading

**Only load if**:
- Technology explicitly mentioned in story (e.g., "React", "PostgreSQL")
- File reference clearly indicates technology (e.g., `*.tsx`, `migrations/`)

**Don't load if**:
- Technology unclear or ambiguous
- General story without specific tech mentions
- Agent's general knowledge sufficient

**It's OK to return empty list** if no specialized skills needed.

## Critical Expertise Warnings

**Flag when**:
- Story mentions technology but no skill available
- Example: Story says "Vue.js form" but no `frontend-vue` skill exists

**Warning format**:
```json
{
  "warnings": [
    "Story mentions 'Vue.js' but no Vue skill available",
    "Story mentions 'GraphQL' but no GraphQL skill available"
  ]
}
```

## Output

```json
{
  "skills_loaded": ["frontend-react", "backend-nodejs"],
  "technologies_detected": ["React", "Node.js"],
  "warnings": ["Story mentions 'Vue.js' but no Vue skill available"]
}
```

## Example Scenarios

**Scenario 1: Clear technology**
- Story: "Add React form with validation"
- Load: `frontend-react` (if available)
- Warnings: None

**Scenario 2: No specialized skills needed**
- Story: "Fix bug in login function"
- Load: None (general knowledge sufficient)
- Warnings: None

**Scenario 3: Missing expertise**
- Story: "Add GraphQL query endpoint"
- Load: None (no `backend-graphql` skill)
- Warnings: "Story mentions 'GraphQL' but no GraphQL skill available"

**Scenario 4: Ambiguous**
- Story: "Add user settings feature"
- Load: None (could be frontend, backend, or both - unclear)
- Warnings: None
