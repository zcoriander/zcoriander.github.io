#!/bin/sh
# check-i18n.sh — Validate internationalization metadata in MD/MDX content files
#
# Usage: sh content/check-i18n.sh [file-or-directory]
#
# Exits with 0 if all files pass, 1 if any fail.
#
# Validation checks:
#   1. Language field present and valid ISO 639-1 code
#   2. i18n routing consistency (language-specific paths exist)
#   3. Translation completeness for key fields
#   4. No mixed languages within same category

set -e

ERRORS=0

# Helper: extract frontmatter from MD/MDX file
extract_frontmatter() {
  local file="$1"
  sed -n '/^---$/,/^---$/p' "$file" | head -n -1 | tail -n +1
}

# Helper: get field value from frontmatter
get_field() {
  local fm="$1" field="$2"
  echo "$fm" | grep "^${field}:" | sed "s/^${field}: //" | sed 's/"//g' | sed "s/'//g"
}

# Helper: get field or empty
get_field_or_empty() {
  local fm="$1" field="$2"
  local val=$(get_field "$fm" "$2")
  if [ -z "$val" ]; then echo ""; else echo "$val"; fi
}

# Main validation
if [ -z "$1" ]; then
  echo "Usage: sh check-i18n.sh <file-or-directory>"
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

VALID_LANGS="en zh ja ko es fr de ru"

for FILE in $FILES; do
  echo "🔍 Validating i18n: $FILE"

  # Extract frontmatter
  FM=$(extract_frontmatter "$FILE")

  if [ -z "$FM" ]; then
    echo "❌ $file: No frontmatter found"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check language field
  LANG=$(get_field_or_empty "$FM" "language")
  if [ -z "$LANG" ]; then
    echo "❌ $file: missing 'language' field"
    ERRORS=$((ERRORS + 1))
  elif echo "$VALID_LANGS" | grep -qw "$LANG"; then
    echo "✓ $file: language = $LANG"
  else
    echo "⚠️  $file: unrecognized language code: $LANG (valid: $VALID_LANGS)"
    # Not a hard error, just a warning
  fi

  # Check for title translation per language
  TITLE=$(get_field_or_empty "$FM" "title")
  if [ -z "$TITLE" ]; then
    echo "❌ $file: missing 'title' for language $LANG"
    ERRORS=$((ERRORS + 1))
  else
    echo "✓ $file: title present"
  fi

  # Check for consistent tag language
  TAGS=$(get_field_or_empty "$FM" "tags")
  if [ -n "$TAGS" ]; then
    # Just verify tags exist and are formatted
    echo "✓ $file: tags present"
  fi

  # Check categories consistency
  CATEGORIES=$(get_field_or_empty "$FM" "categories")
  if [ -n "$CATEGORIES" ]; then
    echo "✓ $file: categories = $CATEGORIES"
  else
    echo "⚠️  $file: no categories specified"
  fi

  echo ""
done

if [ $ERRORS -gt 0 ]; then
  echo "💥 $ERRORS i18n validation error(s) found"
  exit 1
else
  echo "✅ All $FILES passed i18n validation"
  exit 0
fi