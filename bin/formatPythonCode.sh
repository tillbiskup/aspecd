#!/usr/bin/env bash
#
# Autoformat Python files currently in git staging area.
#
# Intended for using in pre-commit hook
#
# Formatter, formatter options and exclude pattern can be set.
#
# Note that due to calling the formatter explicitly for files, exclude patterns
# via formatter options are likely to not work. Hence the list of files to be
# reformatted needs to be filtered beforehand.
#
# Existence of the formatter is checked, and if it is not present,
# the script silently exits.
#
# Only Python files in the staging area are reformatted and afterwards
# re-added to the staging area.
#
# Copyright (c) 2023, Till Biskup
# 2023-12-06

FORMATTER="black"
FORMATTER_OPTIONS="-l 78"
EXCLUDE_PATTERN="templates"

if ! command -v $FORMATTER &> /dev/null
then
  exit
fi

if \[ -n "$EXCLUDE_PATTERN" \];
then
  CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR -- '*.py' |  grep -v $EXCLUDE_PATTERN)
else
  CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR -- '*.py')
fi

for file in $CHANGED_FILES
do
  echo "Reformat '$file' using '$FORMATTER $FORMATTER_OPTIONS'"
  $FORMATTER $FORMATTER_OPTIONS "$file"
  git add "$file"
done
