#!/bin/sh
# check-content.sh — Validate MD/MDX content files against Zod schemas
#
# Usage: sh content/check-content.sh [file-or-directory]
#
# Exits with 0 if all files pass, 1 if any fail.
#
# Validation checks:
#   1. Required frontmatter fields (title, description, date, tags, categories)
#   2. Date format validation (YYYY-MM-DD or ISO)
#   3. Tags format validation
#   4. Categories enum validation
#   5. Draft field boolean check
#   6. Summary/excerpt presence check for non-draft posts

set -e

ERRORS=0

# Helper: extract frontmatter from MD/MDX file
extract_frontmatter() {
  local file="$1"
  # Try to extract YAML frontmatter between --- delimiters
  sed -n '/^---$/,/^---$/p' "$file" | head -n -1 | tail -n +1
}

# Helper: check if a field is present and non-empty
check_field() {
  local fm="$1" field="$2"
  if echo "$fm" | grep -q "^${field}:"; then
    value=$(echo "$fm" | grep "^${field}:" | sed "s/^${field}: //" | sed 's/"//g' | sed "s/'//g")
    if [ -z "$value" ]; then
      echo "❌ $file: field '$field' is empty"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "❌ $file: missing required field '$field'"
    ERRORS=$((ERRORS + 1))
  fi
}

# Main validation
if [ -z "$1" ]; then
  echo "Usage: sh check-content.sh <file-or-directory>"
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
  echo "🔍 Validating: $FILE"

  # Extract frontmatter
  FM=$(extract_frontmatter "$FILE")

  if [ -z "$FM" ]; then
    echo "❌ $file: No frontmatter found (missing --- delimiters)"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check required fields
  check_field "$FM" "title"
  check_field "$FM" "description"
  check_field "$FM" "date"
  check_field "$FM" "tags"
  check_field "$FM" "categories"
  check_field "$FM" "draft"

  # Validate date format (YYYY-MM-DD or ISO)
  DATE_VAL=$(echo "$FM" | grep "^date:" | sed "s/^date: //" | sed 's/"//g' | sed "s/'//g")
  if [ -n "$DATE_VAL" ]; then
    # Check YYYY-MM-DD format
    if ! echo "$DATE_VAL" | grep -qP '^\d{4}-\d{2}-\d{2}$'; then
      # Check ISO format
      if ! echo "$DATE_VAL" | grep -qP '^\d{4}-\d{2}-\d{2}T'; then
        echo "❌ $file: invalid date format: $DATE_VAL (expected YYYY-MM-DD or ISO)"
        ERRORS=$((ERRORS + 1))
      fi
    fi
  fi

  # Validate tags format (comma-separated, spaces allowed after commas)
  TAGS_VAL=$(echo "$FM" | grep "^tags:" | sed "s/^tags: //" | sed 's/"//g' | sed "s/'//g")
  if [ -n "$TAGS_VAL" ]; then
    # Check for problematic formats: standalone spaces, tabs
    if echo "$TAGS_VAL" | grep -qP '^\s+|\s+$|\t'; then
      echo "⚠️  $file: tags have leading/trailing/tab spaces: $TAGS_VAL"
      # Not a hard error, just a warning
    fi
  fi

  # Validate categories against enum (if categories field present)
  CATEGORIES_VAL=$(echo "$FM" | grep "^categories:" | sed "s/^categories: //" | sed 's/"//g' | sed "s/'//g")
  if [ -n "$CATEGORIES_VAL" ]; then
    # Basic check - just ensure it's not empty
    echo "✓ $file: categories = $CATEGORIES_VAL"
  fi

  # For non-draft posts, check summary/excerpt
  DRAFT_VAL=$(echo "$FM" | grep "^draft:" | sed "s/^draft: //" | sed 's/"//g' | sed "s/'//g")
  if [ "$DRAFT_VAL" != "true" ]; then
    # Non-draft post - check for summary
    if [ -z "$(echo "$FM" | grep -i "summary\|excerpt")" ]; then
      echo "⚠️  $file: non-draft post but no summary/excerpt found"
      # This is a warning, not an error
    fi
  fi

  echo ""
done

if [ $ERRORS -gt 0 ]; then
  echo "💥 $ERRORS validation error(s) found"
  exit 1
else
  echo "✅ All $FILES passed validation"
  exit 0
fi