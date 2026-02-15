---
name: agent-catalog
description: Build catalogs of agents and skills for planners and skill-loader. Agents catalog for planner selection (agent-summary required). Skills catalog for dynamic skill loading (all available skills).
---

# Agent Catalog

Build catalogs of agents and skills:
- **Agents catalog**: Planner-selectable agents (agent-summary skill required)
- **Skills catalog**: All available Claude skills for dynamic loading

## build_catalog()

```bash
mkdir -p .scope

# Initialize JSON array
echo '{"agents":[]}' > .scope/agents_catalog.json

# Search in installed locations (prefer project-local, fallback to user)
# Use $HOME instead of ~ for reliable expansion in all contexts
find ./.claude/agents "$HOME/.claude/agents" -name "*.md" 2>/dev/null | sort -u | while read f; do
  # Extract YAML frontmatter (between first two --- markers only)
  frontmatter=$(awk '/^---$/{if(++n==2) exit; if(n==1) next} n==1' "$f")

  if [ -n "$frontmatter" ]; then
    name=$(echo "$frontmatter" | yq -r '.name // ""')
    desc=$(echo "$frontmatter" | yq -r '.description // ""')
    skills=$(echo "$frontmatter" | yq -r '.skills // ""')

    if [ -n "$name" ]; then
      # Filter: only include agents with agent-summary skill (required for planner selection)
      if [[ ! "$skills" =~ "agent-summary" ]]; then
        continue
      fi

      # Build JSON object for this agent
      agent_json=$(cat <<EOF
{
  "name": "$name",
  "description": "$desc",
  "skills": "$skills"
}
EOF
)

      # Handle phases
      phases_type=$(echo "$frontmatter" | yq -r '.phases | type')
      if [ "$phases_type" = "!!seq" ]; then
        first_phase_type=$(echo "$frontmatter" | yq -r '.phases[0] | type')
        if [ "$first_phase_type" = "!!map" ]; then
          # Phases with descriptions (array of objects)
          phases_json=$(echo "$frontmatter" | yq -o=json '.phases')
          agent_json=$(echo "$agent_json" | jq --argjson phases "$phases_json" '. + {phases: $phases}')
        else
          # Simple string list - convert to comma-separated string
          phases=$(echo "$frontmatter" | yq -r '.phases | join(", ")')
          agent_json=$(echo "$agent_json" | jq --arg phases "$phases" '. + {phases: $phases}')
        fi
      elif [ "$phases_type" = "!!str" ]; then
        # String format (comma-separated)
        phases=$(echo "$frontmatter" | yq -r '.phases')
        agent_json=$(echo "$agent_json" | jq --arg phases "$phases" '. + {phases: $phases}')
      fi

      # Append agent to catalog
      tmp=$(mktemp)
      jq --argjson agent "$agent_json" '.agents += [$agent]' .scope/agents_catalog.json > "$tmp" && mv "$tmp" .scope/agents_catalog.json
    fi
  fi
done
```

## get_catalog()

Read `.scope/agents_catalog.json`.

**Output format:**
```json
{
  "agents": [
    {
      "name": "product-owner",
      "description": "Validate epic business requirements...",
      "skills": "agent-summary, project-documentation, project-tracking",
      "phases": [
        {
          "name": "epic_validation",
          "description": "Validate business requirements, ask clarifying questions, gate architecture work"
        },
        {
          "name": "epic_definition",
          "description": "Write acceptance criteria and end-to-end test scenarios"
        },
        {
          "name": "story_review",
          "description": "Review story breakdown for business alignment and completeness"
        }
      ]
    },
    {
      "name": "architect",
      "description": "Design technical architecture...",
      "skills": "agent-summary, project-documentation, project-tracking",
      "phases": [
        {
          "name": "system_context",
          "description": "Analyze how epic fits in existing system, identify patterns and constraints"
        },
        {
          "name": "architecture_design",
          "description": "Design components, APIs, data models, and create ADRs"
        },
        {
          "name": "architecture_review",
          "description": "Self-check architecture completeness before human approval"
        },
        {
          "name": "spec_generation",
          "description": "Generate technical specifications in docs/architecture/13-specs/"
        }
      ]
    }
  ]
}
```

**Phase descriptions provide context for planner:**
- **When** to use each phase (based on workflow stage)
- **What** the agent does in that phase (outcome expected)
- **Why** this phase exists (business purpose)

## build_skills_catalog()

```bash
mkdir -p .scope

# Initialize JSON array
echo '{"skills":[]}' > .scope/skills_catalog.json

# Search both user skills and project skills
# Use $HOME instead of ~ for reliable expansion in all contexts
for skill_dir in "$HOME/.claude/skills" ./.claude/skills; do
  if [ -d "$skill_dir" ]; then
    find "$skill_dir" -name "SKILL.md" 2>/dev/null | while read f; do
      # Extract YAML frontmatter (between first two --- markers only)
      frontmatter=$(awk '/^---$/{if(++n==2) exit; if(n==1) next} n==1' "$f")

      if [ -n "$frontmatter" ]; then
        name=$(echo "$frontmatter" | yq -r '.name // ""')
        desc=$(echo "$frontmatter" | yq -r '.description // ""')

        if [ -n "$name" ]; then
          # Extract location (user vs project skill)
          location="project"
          if [[ "$f" =~ ".claude/skills" ]]; then
            location="user"
          fi

          # Build JSON object for this skill
          skill_json=$(jq -n \
            --arg name "$name" \
            --arg desc "$desc" \
            --arg path "$f" \
            --arg location "$location" \
            '{name: $name, description: $desc, path: $path, location: $location}')

          # Append skill to catalog
          tmp=$(mktemp)
          jq --argjson skill "$skill_json" '.skills += [$skill]' .scope/skills_catalog.json > "$tmp" && mv "$tmp" .scope/skills_catalog.json
        fi
      fi
    done
  fi
done
```

## get_skills_catalog()

Read `.scope/skills_catalog.json`.

**Output format:**
```json
{
  "skills": [
    {
      "name": "frontend-react",
      "description": "React component patterns and best practices",
      "path": "/Users/bob/.claude/skills/technology/frontend-react/SKILL.md",
      "location": "project"
    },
    {
      "name": "algorithmic-art",
      "description": "Creating algorithmic art using p5.js",
      "path": "/Users/bob/.claude/skills/algorithmic-art/SKILL.md",
      "location": "user"
    },
    {
      "name": "subagent-skill-loader",
      "description": "Dynamically load technology skills based on story requirements",
      "path": "/Users/bob/.claude/skills/subagent-skill-loader/SKILL.md",
      "location": "project"
    }
  ]
}
```

**Note**: Skills catalog includes ALL available skills. Skill-loader uses description to determine when to load each skill based on story requirements.
