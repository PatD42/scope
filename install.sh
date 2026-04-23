#!/bin/bash
#
# SCOPE Installation Script
# Installs Claude and Codex variants from shared + platform-specific source roots.
#
# Usage:
#   ./install.sh              # Install to current project
#   ./install.sh --user       # Install to home directory
#   ./install.sh /path/to/dir # Install to a custom target directory
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.1.0"

SHARED_SRC="${SCRIPT_DIR}/src_shared"
CLAUDE_SRC="${SCRIPT_DIR}/src_claude"
CODEX_SRC="${SCRIPT_DIR}/src_codex"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║          SCOPE Installer v${VERSION}        ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

INSTALL_TYPE="project"
INSTALL_DIR="."
CLAUDE_DIR="./.claude"
CODEX_DIR="./plugins/scope"

if [[ "${1:-}" == "--user" ]]; then
    INSTALL_TYPE="user"
    INSTALL_DIR="$HOME"
    CLAUDE_DIR="$HOME/.claude"
    CODEX_DIR="$HOME/plugins/scope"
    echo -e "${GREEN}Installing to user directory:${NC}"
elif [[ -n "${1:-}" ]]; then
    INSTALL_DIR="$1"
    CLAUDE_DIR="${INSTALL_DIR}/.claude"
    CODEX_DIR="${INSTALL_DIR}/plugins/scope"
    echo -e "${GREEN}Installing to custom directory:${NC}"
else
    echo -e "${GREEN}Installing to project directory:${NC}"
fi

echo "  Claude: ${CLAUDE_DIR}"
echo "  Codex:  ${CODEX_DIR}"
echo ""

copy_overlay() {
    local src="$1"
    local dest="$2"

    if [[ -d "$src" ]]; then
        mkdir -p "$dest"
        cp -R "$src/." "$dest/"
    fi
}

copy_file_if_exists() {
    local src="$1"
    local dest="$2"

    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        cp "$src" "$dest"
    fi
}

list_markdown_commands() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        find "$dir" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort
    fi
}

echo -e "${YELLOW}Creating Directory Structure${NC}"
echo ""

mkdir -p "${CLAUDE_DIR}/commands" "${CLAUDE_DIR}/skills" "${CLAUDE_DIR}/agents" "${CLAUDE_DIR}/governance"
mkdir -p "${CODEX_DIR}/commands" "${CODEX_DIR}/skills" "${CODEX_DIR}/agents" "${CODEX_DIR}/governance" "${CODEX_DIR}/docs" "${CODEX_DIR}/scripts" "${CODEX_DIR}/.codex-plugin"
mkdir -p "${CLAUDE_DIR}/commands/scripts"

echo "  Created ${CLAUDE_DIR}/"
echo "  Created ${CODEX_DIR}/"

echo ""
echo -e "${YELLOW}Installing Claude Files${NC}"
echo ""

copy_overlay "${SHARED_SRC}/commands" "${CLAUDE_DIR}/commands"
copy_overlay "${CLAUDE_SRC}/commands" "${CLAUDE_DIR}/commands"
copy_overlay "${SHARED_SRC}/scripts" "${CLAUDE_DIR}/commands/scripts"
copy_overlay "${CLAUDE_SRC}/scripts" "${CLAUDE_DIR}/commands/scripts"
copy_overlay "${SHARED_SRC}/skills" "${CLAUDE_DIR}/skills"
copy_overlay "${CLAUDE_SRC}/skills" "${CLAUDE_DIR}/skills"
copy_overlay "${SHARED_SRC}/agents" "${CLAUDE_DIR}/agents"
copy_overlay "${CLAUDE_SRC}/agents" "${CLAUDE_DIR}/agents"
copy_overlay "${SHARED_SRC}/governance" "${CLAUDE_DIR}/governance"
copy_overlay "${CLAUDE_SRC}/governance" "${CLAUDE_DIR}/governance"

echo "  Commands:"
while IFS= read -r cmd; do
    [[ -n "$cmd" ]] && echo "    ✓ /$cmd"
done < <(list_markdown_commands "${CLAUDE_DIR}/commands")

echo "  Command resources:"
while IFS= read -r resource_dir; do
    [[ -n "$resource_dir" ]] && echo "    ✓ /$resource_dir/"
done < <(find "${CLAUDE_DIR}/commands" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)

echo "  Skills:"
while IFS= read -r skill_dir; do
    [[ -n "$skill_dir" ]] && echo "    ✓ $skill_dir"
done < <(find "${CLAUDE_DIR}/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)

echo "  Agents:"
while IFS= read -r agent_name; do
    [[ -n "$agent_name" ]] && echo "    ✓ $agent_name"
done < <(find "${CLAUDE_DIR}/agents" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort)

echo "  Governance:"
while IFS= read -r governance_name; do
    [[ -n "$governance_name" ]] && echo "    ✓ $governance_name"
done < <(find "${CLAUDE_DIR}/governance" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort)

echo ""
echo -e "${YELLOW}Installing Codex Plugin${NC}"
echo ""

copy_overlay "${SHARED_SRC}/commands" "${CODEX_DIR}/commands"
copy_overlay "${CODEX_SRC}/commands" "${CODEX_DIR}/commands"
copy_overlay "${SHARED_SRC}/skills" "${CODEX_DIR}/skills"
copy_overlay "${CODEX_SRC}/skills" "${CODEX_DIR}/skills"
copy_overlay "${SHARED_SRC}/agents" "${CODEX_DIR}/agents"
copy_overlay "${CODEX_SRC}/agents" "${CODEX_DIR}/agents"
copy_overlay "${SHARED_SRC}/governance" "${CODEX_DIR}/governance"
copy_overlay "${CODEX_SRC}/governance" "${CODEX_DIR}/governance"
copy_overlay "${SHARED_SRC}/docs" "${CODEX_DIR}/docs"
copy_overlay "${CODEX_SRC}/docs" "${CODEX_DIR}/docs"
copy_overlay "${SHARED_SRC}/scripts" "${CODEX_DIR}/scripts"
copy_overlay "${CODEX_SRC}/scripts" "${CODEX_DIR}/scripts"
copy_overlay "${CODEX_SRC}/.codex-plugin" "${CODEX_DIR}/.codex-plugin"
copy_file_if_exists "${CODEX_SRC}/README.md" "${CODEX_DIR}/README.md"
copy_file_if_exists "${CODEX_SRC}/.mcp.json" "${CODEX_DIR}/.mcp.json"

echo "  Plugin root:"
[[ -f "${CODEX_DIR}/README.md" ]] && echo "    ✓ README.md"
[[ -f "${CODEX_DIR}/.mcp.json" ]] && echo "    ✓ .mcp.json"
[[ -f "${CODEX_DIR}/.codex-plugin/plugin.json" ]] && echo "    ✓ .codex-plugin/plugin.json"

echo "  Commands:"
while IFS= read -r cmd; do
    [[ -n "$cmd" ]] && echo "    ✓ scope:$cmd"
done < <(list_markdown_commands "${CODEX_DIR}/commands")

echo "  Skills:"
while IFS= read -r skill_dir; do
    [[ -n "$skill_dir" ]] && echo "    ✓ $skill_dir"
done < <(find "${CODEX_DIR}/skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)

echo "  Agents:"
while IFS= read -r agent_name; do
    [[ -n "$agent_name" ]] && echo "    ✓ $agent_name"
done < <(find "${CODEX_DIR}/agents" -maxdepth 1 -type f -name "*.md" -exec basename {} .md \; | sort)

echo "  Docs:"
while IFS= read -r doc_name; do
    [[ -n "$doc_name" ]] && echo "    ✓ $doc_name"
done < <(find "${CODEX_DIR}/docs" -maxdepth 1 -type f -name "*.md" -exec basename {} \; | sort)

echo "  Scripts:"
while IFS= read -r script_name; do
    [[ -n "$script_name" ]] && echo "    ✓ $script_name"
done < <(find "${CODEX_DIR}/scripts" -maxdepth 1 -type f -exec basename {} \; | sort)

if [[ "$INSTALL_TYPE" == "project" ]]; then
    echo ""
    echo -e "${YELLOW}Creating Configuration${NC}"
    echo ""

    mkdir -p "${INSTALL_DIR}/.scope"

    if [[ -f "${INSTALL_DIR}/.scope/config.yaml" ]]; then
        echo "  ○ .scope/config.yaml already exists (skipped)"
    else
        cp "${SHARED_SRC}/commands/config_example.yaml" "${INSTALL_DIR}/.scope/config.yaml"
        echo "  ✓ Created .scope/config.yaml from template"
        echo ""
        echo -e "  ${YELLOW}Next: Edit .scope/config.yaml to set:${NC}"
        echo "    - project.name"
        echo "    - tracking.skill and tracking.project_key"
        echo ""
    fi
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""

if [[ "$INSTALL_TYPE" == "project" ]]; then
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    if [[ "$INSTALL_DIR" != "." ]]; then
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
    echo "   Claude: /prd_refine, /prd_breakdown, /epic_refine {epic-id}, /implement {epic-id}"
    echo "   Codex:  scope:prd_refine, scope:prd_breakdown, scope:epic_refine E1, scope:implement E1"
    echo ""
else
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. In any project, use the installed directories:"
    echo "   Claude: ${CLAUDE_DIR}"
    echo "   Codex:  ${CODEX_DIR}"
    echo ""
fi

echo -e "${BLUE}Documentation: ${SCRIPT_DIR}/docs/scope-architecture.md${NC}"
echo ""
