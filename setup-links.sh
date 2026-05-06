#!/usr/bin/env bash
# setup-links.sh — symlink connector skills into a consumer project's .claude/commands/
#
# Run from the consumer project root:
#   bash connector/setup-links.sh
#
# This script is idempotent — re-running it updates existing symlinks.
set -e

CONNECTOR_DIR="$(cd "$(dirname "$0")" && pwd)"
CONSUMER_DIR="$(dirname "$CONNECTOR_DIR")"
COMMANDS_DIR="$CONSUMER_DIR/.claude/commands"

mkdir -p "$COMMANDS_DIR"

connector_name="$(basename "$CONNECTOR_DIR")"

linked=0
for cmd in "$CONNECTOR_DIR"/plugin/commands/*.md; do
    name="$(basename "$cmd")"
    # Use a relative path so the symlink works on any machine after cloning
    rel_path="../../$connector_name/plugin/commands/$name"
    ln -sf "$rel_path" "$COMMANDS_DIR/$name"
    echo "  linked: $name -> $rel_path"
    linked=$((linked + 1))
done

echo ""
echo "Done. $linked connector commands linked into $COMMANDS_DIR"
echo "Connector at: $CONNECTOR_DIR"
