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

linked=0
for skill in "$CONNECTOR_DIR"/skills/*.md; do
    name="$(basename "$skill")"
    ln -sf "$skill" "$COMMANDS_DIR/$name"
    echo "  linked: $name"
    linked=$((linked + 1))
done

echo ""
echo "Done. $linked connector skills linked into $COMMANDS_DIR"
echo "Connector at: $CONNECTOR_DIR"
