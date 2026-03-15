#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
BRANCH="main"
REMOTE="origin"
LOG_DIR="$SCRIPT_DIR/logs"
RUN_LOG="$LOG_DIR/run.log"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

mkdir -p "$LOG_DIR"

{
  echo "[$STAMP] start"
} >> "$RUN_LOG"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

cd "$REPO_DIR"

if [ ! -d .git ]; then
  echo "[$STAMP] missing git repository" >> "$RUN_LOG"
  exit 1
fi

if [ -z "$(git status --porcelain)" ]; then
  echo "[$STAMP] no changes" >> "$RUN_LOG"
  exit 0
fi

git add -A

if ! git diff --cached --quiet; then
  git commit -m "auto: $STAMP" >> "$RUN_LOG" 2>&1 || true
fi

git fetch "$REMOTE" >> "$RUN_LOG" 2>&1

if git rev-parse --verify "$REMOTE/$BRANCH" >/dev/null 2>&1; then
  if ! git merge-base --is-ancestor "$REMOTE/$BRANCH" "$BRANCH"; then
    echo "[$STAMP] remote is ahead, skip push" >> "$RUN_LOG"
    exit 0
  fi
fi

git push "$REMOTE" "$BRANCH" >> "$RUN_LOG" 2>&1
echo "[$STAMP] push complete" >> "$RUN_LOG"
