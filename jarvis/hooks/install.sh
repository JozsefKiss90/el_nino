#!/bin/sh
# Install the dev_graph projection hooks into this clone's .git/hooks.
# Git does not version .git/hooks, so each clone installs them once. Run from anywhere in the repo:
#   sh jarvis/hooks/install.sh
repo=$(git rev-parse --show-toplevel) || { echo "not a git repo"; exit 1; }
src="$repo/jarvis/hooks/pre-commit"
dst="$repo/.git/hooks/pre-commit"
cp "$src" "$dst"
chmod +x "$dst" 2>/dev/null || true
echo "Installed pre-commit hook -> $dst"
