#!/bin/bash
#
# SCOPE Installation Script
# Installs SCOPE commands, skills, and agents to user or project directory
#
# Usage:
#   ./install.sh              # Install to ./.claude (default)
#   ./install.sh --user       # Install to ~/.claude
#   ./install.sh /path/to/dir # Install to /path/to/dir/.claude
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

# Colors
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

INSTALL_TYPE="project"
INSTALL_DIR="."
CLAUDE_DIR="./.claude"

if [ "$1" == "--user" ]; then
    INSTALL_TYPE="user"
    CLAUDE_DIR="$HOME/.claude"
    INSTALL_DIR="$HOME"
    echo -e "${GREEN}Installing to user directory: ${CLAUDE_DIR}${NC}"
elif [ -n "$1" ]; then
    INSTALL_DIR="$1"
    CLAUDE_DIR="${INSTALL_DIR}/.claude"
    echo -e "${GREEN}Installing to custom directory: ${CLAUDE_DIR}${NC}"
else
    echo -e "${GREEN}Installing to project directory: ${CLAUDE_DIR}${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Discover Available Commands
# ─────────────────────────────────────────────────────────────────────────────

COMMANDS=()
for cmd_file in "${SCRIPT_DIR}/src/commands/"*.md; do
    if [ -f "$cmd_file" ]; then
        filename=$(basename "$cmd_file" .md)
        COMMANDS+=("$filename")
    fi
done

IFS=$'\n' COMMANDS=($(sort <<<"${COMMANDS[*]}")); unset IFS

# ─────────────────────────────────────────────────────────────────────────────
# Create Directory Structure
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}Creating Directory Structure${NC}"
echo ""

mkdir -p "${CLAUDE_DIR}/commands"
mkdir -p "${CLAUDE_DIR}/skills"
mkdir -p "${CLAUDE_DIR}/agents"

echo "  Created ${CLAUDE_DIR}/commands/"
echo "  Created ${CLAUDE_DIR}/skills/"
echo "  Created ${CLAUDE_DIR}/agents/"

# ─────────────────────────────────────────────────────────────────────────────
# Copy Files
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}Copying Files${NC}"
echo ""

# Copy config template
cp "${SCRIPT_DIR}/src/commands/config_example.yaml" "${CLAUDE_DIR}/commands/"
echo "  ✓ config_example.yaml (template)"

# Copy commands
for cmd in "${COMMANDS[@]}"; do
    if [ -f "${SCRIPT_DIR}/src/commands/${cmd}.md" ]; then
        cp "${SCRIPT_DIR}/src/commands/${cmd}.md" "${CLAUDE_DIR}/commands/"
        echo "  ✓ /$cmd"
    fi
done

# Copy command resource directories (e.g., prd_refine/, prd_breakdown/)
for cmd_dir in "${SCRIPT_DIR}/src/commands/"*/; do
    if [ -d "$cmd_dir" ]; then
        dir_name=$(basename "$cmd_dir")
        cp -r "$cmd_dir" "${CLAUDE_DIR}/commands/"
        echo "  ✓ /$dir_name/ (resources)"
    fi
done

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
while IFS= read -r agent_file; do
    agent_name=$(basename "$agent_file" .md)
    echo "    ✓ $agent_name"
done < <(find "${SCRIPT_DIR}/src/agents" -name "*.md" -type f 2>/dev/null)

# ─────────────────────────────────────────────────────────────────────────────
# Create Configuration Template (project-level only)
# ─────────────────────────────────────────────────────────────────────────────

if [[ "$INSTALL_TYPE" == "project" ]]; then
    echo ""
    echo -e "${YELLOW}Creating Configuration${NC}"
    echo ""

    mkdir -p "${INSTALL_DIR}/.scope"

    if [ -f "${INSTALL_DIR}/.scope/config.yaml" ]; then
        echo "  ○ .scope/config.yaml already exists (skipped)"
    else
        cp "${SCRIPT_DIR}/src/commands/config_example.yaml" "${INSTALL_DIR}/.scope/config.yaml"
        echo "  ✓ Created .scope/config.yaml from template"
        echo ""
        echo -e "  ${YELLOW}Next: Edit .scope/config.yaml to set:${NC}"
        echo "    - project.name"
        echo "    - tracking.skill and tracking.project_key"
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
        echo "2. Edit .scope/config.yaml with your project settings"
        echo ""
        echo "3. Start using SCOPE:"
    else
        echo "1. Edit .scope/config.yaml with your project settings"
        echo ""
        echo "2. Start using SCOPE:"
    fi
    echo "   /prd_refine"
    echo "   /prd_breakdown"
    echo "   /epic_refine {epic-id}"
    echo "   /implement {epic-id}"
    echo ""
else
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. In any project, start using SCOPE:"
    echo "   /prd_refine"
    echo "   /prd_breakdown"
    echo "   /epic_refine {epic-id}"
    echo "   /implement {epic-id}"
    echo ""
fi

echo -e "${BLUE}Documentation: ${SCRIPT_DIR}/docs/scope-architecture.md${NC}"
echo ""
