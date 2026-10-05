#!/usr/bin/env bash
# Per-invocation commit identity; authentication is deliberately separate.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
identity="${1:-}"
if [[ $# -gt 0 ]]; then shift; fi
case "$identity" in
  swagata) display_name='Swagata Bhowmik' ;;
  sumit) display_name='Sumit Kothari' ;;
  *) echo 'Choose swagata or sumit.' >&2; exit 2 ;;
esac
if [[ $# -eq 0 ]]; then
  echo "Usage: ./git-$identity <git-command> [arguments]" >&2; exit 2
fi
# Never discover and accidentally operate on an enclosing repository.
if [[ ! -d "$project_dir/.git" && ! -f "$project_dir/.git" ]]; then
  echo 'This project folder is not a Git repository yet. Initialize it or use the cloned project folder first.' >&2
  exit 2
fi
case "$1" in
  add|commit|status|diff|log|show|push|fetch|pull|switch|branch|merge|rebase|rev-parse|ls-files|var) ;;
  *) echo 'Unsupported wrapper command. For setup, use ordinary git with --local configuration.' >&2; exit 2 ;;
esac
identity_email="$(git -C "$project_dir" config --local --get "team.$identity.email" || true)"
if [[ -z "$identity_email" || "$identity_email" != *@* || "$identity_email" == *$'\n'* || "$identity_email" == *$'\r'* ]]; then
  echo "Set this member's verified GitHub email in this folder first:" >&2
  echo "git config --local team.$identity.email 'VERIFIED_EMAIL_OR_EXACT_GITHUB_NOREPLY_ADDRESS'" >&2
  exit 2
fi
export GIT_AUTHOR_NAME="$display_name" GIT_AUTHOR_EMAIL="$identity_email"
export GIT_COMMITTER_NAME="$display_name" GIT_COMMITTER_EMAIL="$identity_email"
exec git -C "$project_dir" -c user.name="$display_name" -c user.email="$identity_email" "$@"
