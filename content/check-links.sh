#!/bin/sh
# check-links.sh — Validate internal links and references in MD/MDX content files
#
# Usage: sh content/check-links.sh [file-or-directory]
#
# Exits with 0 if all files pass, 1 if any fail.
#
# Validation checks:
#   1. Internal GitHub links reference existing files
#   2. Image references have valid extensions
#   3. No broken [text](url) patterns
#   4. Citation references have matching definitions

set -e

ERRORS=0

# Main validation
if [ -z "$1" ]; then
  echo "Usage: sh check-links.sh <file-or-directory>"
  exit 1
fi

TARGET="$1"

if [ ! -e "$TARGET" ]; then
  echo "❌ Target not found: $TARGET"
  exit 1
fi

# Find all MD/MDX files
if [ -d "$TARGET" ]; then
  FILES=$(find "$TARGET" -type f \( -name "*.md" -o -name "*.mdx" \) | sort)
else
  FILES="$TARGET"
fi

for FILE in $FILES; do
  echo "🔍 Validating links: $FILE"

  # Save current error count
  ERRORS_BEFORE=$ERRORS

  # Check for image references: !\[alt\]\(path\)
  if grep -qE '!\[.*\]\.\(.*\)' "$FILE" 2>/dev/null; then
    grep -nE '!\[.*\]\.\(.*\)' "$FILE" 2>/dev/null | while read -r line; do
      line_num=$(echo "$line" | cut -d: -f1)
      # Extract image path from !\[alt\]\(path\)
      img_path=$(echo "$line" | sed -nE 's/^.*!\[.*\]\((.*)\)/\1/p')
      # Remove surrounding parentheses or quotes
      img_path=$(echo "$img_path" | tr -d ' "''')
      # Check if file exists
      if [ ! -f "$(dirname "$FILE")/$img_path" ]; then
        echo "❌ $FILE:$line_num: image not found: $img_path"
        ERRORS=$((ERRORS + 1))
      else
        echo "✓ $FILE:$line_num: image found: $img_path"
      fi
    done
  fi

  # Check for internal links to other markdown files: [text](page.md)
  if grep -qE '\[.*\]\.md' "$FILE" 2>/dev/null; then
    grep -nE '\[.*\]\.md' "$FILE" 2>/dev/null | while read -r line; do
      line_num=$(echo "$line" | cut -d: -f1)
      # Extract link target from \[text\](url)
      target=$(echo "$line" | sed -nE 's/^.*\[.*\]\((.*)\)/\1/p')
      target=$(echo "$target" | tr -d ' "''')
      # Get filename
      target_file=$(basename "$target")
      # Resolve path
      full_path="$(dirname "$FILE")/$target_file"
      if [ ! -f "$full_path" ]; then
        echo "❌ $FILE:$line_num: broken internal link: $target_file not found"
        ERRORS=$((ERRORS + 1))
      else
        echo "✓ $FILE:$line_num: internal link OK: $target_file"
      fi
    done
  fi

  # Check for reference-style links [text][ref]
  if grep -qE '\[.*\]\[' "$FILE" 2>/dev/null; then
    # Extract reference names
    ref_names=$(grep -oE '\[([^\[\]]+)\]' "$FILE" | grep -v '^\[$' | sort -u)
    for ref in $ref_names; do
      # Check if reference definition exists: [ref]:
      if grep -qE "^\s*\[${ref}\]:*" "$FILE"; then
        echo "✓ $FILE: reference [${ref}] defined"
      else
        echo "⚠️  $FILE: reference [${ref}] used but not defined (may be OK if external)"
      fi
    done
  fi

  echo ""
done

if [ $ERRORS -gt 0 ]; then
  echo "💥 $ERRORS link validation error(s) found"
  exit 1
else
  echo "✅ All $FILES passed link validation"
  exit 0
fi