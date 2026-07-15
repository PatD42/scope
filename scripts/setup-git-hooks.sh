#!/usr/bin/env bash

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

test -x .githooks/pre-push
git config --local core.hooksPath .githooks

printf 'Configured Scope Git hooks from %s/.githooks\n' "$repo_root"
