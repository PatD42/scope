#!/bin/bash
#
# SCOPE Installation Script
# Installs SCOPE commands, skills, and agents to user or project directory
#
# Usage:
#   ./install.sh              # Install to ./.claude (default, no interaction)
#   ./install.sh --user       # Install to ~/.claude
#   ./install.sh /path/to/dir # Install to /path/to/dir/.claude
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║          SCOPE Installer v${VERSION}        ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# Parse Arguments and Determine Installation Target
# ─────────────────────────────────────────────────────────────────────────────

# Default: Install to project directory (./.claude)
INSTALL_TYPE="project"
INSTALL_DIR="."
CLAUDE_DIR="./.claude"

# Check for --user flag
if [ "$1" == "--user" ]; then
    INSTALL_TYPE="user"
    CLAUDE_DIR="$HOME/.claude"
    INSTALL_DIR="$HOME"
    echo -e "${GREEN}Installing to user directory: ${CLAUDE_DIR}${NC}"
elif [ -n "$1" ]; then
    # Custom directory provided
    INSTALL_DIR="$1"
    CLAUDE_DIR="${INSTALL_DIR}/.claude"
    INSTALL_TYPE="project"
    echo -e "${GREEN}Installing to custom directory: ${CLAUDE_DIR}${NC}"
else
    # Default: project installation
    echo -e "${GREEN}Installing to project directory: ${CLAUDE_DIR}${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Discover Available Commands (install all by default)
# ─────────────────────────────────────────────────────────────────────────────

# Dynamically discover commands from src/commands/*.md
# Excludes: scope.md (hub), config_example.yaml (template)
COMMANDS=()
for cmd_file in "${SCRIPT_DIR}/src/commands/"*.md; do
    if [ -f "$cmd_file" ]; then
        filename=$(basename "$cmd_file" .md)
        # Skip hub command
        if [[ "$filename" == "scope" ]]; then
            continue
        fi
        COMMANDS+=("$filename")
    fi
done

# Sort commands alphabetically
IFS=$'\n' COMMANDS=($(sort <<<"${COMMANDS[*]}")); unset IFS

# No commands to skip - install all
SKIP_COMMANDS=()

# ─────────────────────────────────────────────────────────────────────────────
# Create Directory Structure
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}Creating Directory Structure${NC}"
echo ""

mkdir -p "${CLAUDE_DIR}/commands"
mkdir -p "${CLAUDE_DIR}/commands/scripts"
mkdir -p "${CLAUDE_DIR}/skills"
mkdir -p "${CLAUDE_DIR}/agents/planners"
mkdir -p "${CLAUDE_DIR}/agents/scripts"

echo "  Created ${CLAUDE_DIR}/commands/"
echo "  Created ${CLAUDE_DIR}/skills/"
echo "  Created ${CLAUDE_DIR}/agents/"

# ─────────────────────────────────────────────────────────────────────────────
# Copy Files
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}Copying Files${NC}"
echo ""

# Function to check if command should be skipped
should_skip() {
    local cmd="$1"
    for skip in "${SKIP_COMMANDS[@]}"; do
        if [[ "$skip" == "$cmd" ]]; then
            return 0
        fi
    done
    return 1
}

# Copy config template (always)
cp "${SCRIPT_DIR}/src/commands/config_example.yaml" "${CLAUDE_DIR}/commands/"
echo "  ✓ config_example.yaml (template)"

# Copy shortcut commands (all by default)
for cmd in "${COMMANDS[@]}"; do
    if should_skip "$cmd"; then
        echo "  ○ /$cmd (skipped)"
    else
        if [ -f "${SCRIPT_DIR}/src/commands/${cmd}.md" ]; then
            cp "${SCRIPT_DIR}/src/commands/${cmd}.md" "${CLAUDE_DIR}/commands/"
            echo "  ✓ /$cmd"
        fi
    fi
done

# Copy command scripts (if they exist)
if [ -d "${SCRIPT_DIR}/src/commands/scripts" ]; then
    echo ""
    echo "  Copying command scripts..."
    cp -r "${SCRIPT_DIR}/src/commands/scripts/"* "${CLAUDE_DIR}/commands/scripts/" 2>/dev/null || true
    # Make scripts executable
    chmod +x "${CLAUDE_DIR}/commands/scripts/"*.sh 2>/dev/null || true
    while IFS= read -r script_file; do
        script_name=$(basename "$script_file")
        echo "    ✓ $script_name"
    done < <(find "${SCRIPT_DIR}/src/commands/scripts" -type f 2>/dev/null | grep -E '\.(sh|ps1)$')
fi

# Copy skills
echo ""
echo "  Copying skills..."
cp -r "${SCRIPT_DIR}/src/skills/"* "${CLAUDE_DIR}/skills/" 2>/dev/null || true
for skill_dir in "${SCRIPT_DIR}/src/skills/"*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        echo "    ✓ $skill_name"
    fi
done

# Copy agents
echo ""
echo "  Copying agents..."
cp -r "${SCRIPT_DIR}/src/agents/"* "${CLAUDE_DIR}/agents/" 2>/dev/null || true
# Use find to list all .md files in src/agents
while IFS= read -r agent_file; do
    agent_name=$(basename "$agent_file" .md)
    # Get relative path for better organization display
    rel_path=$(dirname "${agent_file#${SCRIPT_DIR}/src/agents/}")
    if [ "$rel_path" = "." ]; then
        echo "    ✓ $agent_name"
    else
        echo "    ✓ $rel_path/$agent_name"
    fi
done < <(find "${SCRIPT_DIR}/src/agents" -name "*.md" -type f 2>/dev/null)

# Copy agent scripts (if they exist)
if [ -d "${SCRIPT_DIR}/src/agents/scripts" ]; then
    echo ""
    echo "  Copying agent scripts..."
    cp -r "${SCRIPT_DIR}/src/agents/scripts/"* "${CLAUDE_DIR}/agents/scripts/" 2>/dev/null || true
    while IFS= read -r script_file; do
        script_name=$(basename "$script_file")
        echo "    ✓ $script_name"
    done < <(find "${SCRIPT_DIR}/src/agents/scripts" -type f 2>/dev/null | grep -E '\.(sh|ps1)$')
fi

# ─────────────────────────────────────────────────────────────────────────────
# Create Configuration Template (project-level only)
# ─────────────────────────────────────────────────────────────────────────────

if [[ "$INSTALL_TYPE" == "project" ]]; then
    echo ""
    echo -e "${YELLOW}Creating Configuration${NC}"
    echo ""

    # Create .scope directory
    mkdir -p "${INSTALL_DIR}/.scope"

    # Copy config template if it doesn't exist
    if [ -f "${INSTALL_DIR}/.scope/config.yaml" ]; then
        echo "  ○ .scope/config.yaml already exists (skipped)"
    else
        cp "${SCRIPT_DIR}/src/commands/config_example.yaml" "${INSTALL_DIR}/.scope/config.yaml"
        echo "  ✓ Created .scope/config.yaml from template"
        echo ""
        echo "  ${YELLOW}Next: Edit .scope/config.yaml to set:${NC}"
        echo "    - project.name"
        echo "    - tracking.project_key"
        echo "    - tracking.atlassian_url"
        echo "    - documentation.space_key"
        echo "    - documentation.atlassian_url"
        echo ""
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary and Next Steps
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""

if [[ "$INSTALL_TYPE" == "project" ]]; then
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    if [ "$INSTALL_DIR" != "." ]; then
        echo "1. Navigate to the project:"
        echo "   cd ${INSTALL_DIR}"
        echo ""
        echo "2. Edit .scope/config.yaml:"
    else
        echo "1. Edit .scope/config.yaml:"
    fi
    echo "   # Set project name, Jira project key, Atlassian URL, etc."
    echo "   # Or switch to file-based tracking/documentation"
    echo ""
    if [ "$INSTALL_DIR" != "." ]; then
        echo "3. For Atlassian (Jira/Confluence), validate authentication:"
    else
        echo "2. For Atlassian (Jira/Confluence), validate authentication:"
    fi
    echo ""
    if [ "$INSTALL_DIR" != "." ]; then
        echo "4. Start using SCOPE:"
    else
        echo "3. Start using SCOPE:"
    fi
    echo "   /create epic My first epic"
    echo "   /workplan MYPROJ-1"
    echo ""
else
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. In each project, initialize SCOPE configuration:"
    echo "   cd /path/to/your/project"
    echo ""
    echo "2. Start using SCOPE:"
    echo "   /prd_refine"
    echo "   /prd_breakdown"
    echo "   /create epic My first epic"
    echo "   /workplanplan ABC-1"
    echo ""
fi

echo -e "${BLUE}Documentation: ${SCRIPT_DIR}/design/scope-architecture.md${NC}"
echo ""
