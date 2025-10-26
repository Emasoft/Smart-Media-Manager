#!/usr/bin/env bash
set -euo pipefail

HOOK_NAME=${2:-manual}
REPO_ROOT="$(git rev-parse --show-toplevel)"
DOCS_DIR="$REPO_ROOT/docs_dev"
BACKUP_DIR="$REPO_ROOT/.git/local_backups"
BACKUP_ARCHIVE="$BACKUP_DIR/docs_dev.tar.gz"

mkdir -p "$BACKUP_DIR"

has_docs() {
    [ -d "$DOCS_DIR" ] && [ -n "$(ls -A "$DOCS_DIR" 2>/dev/null || true)" ]
}

backup_docs() {
    if has_docs; then
        local tmp_archive="${BACKUP_ARCHIVE}.tmp"
        tar -czf "$tmp_archive" -C "$DOCS_DIR" .
        mv "$tmp_archive" "$BACKUP_ARCHIVE"
    fi
}

restore_docs() {
    if ! has_docs; then
        if [ -f "$BACKUP_ARCHIVE" ]; then
            mkdir -p "$DOCS_DIR"
            tar -xzf "$BACKUP_ARCHIVE" -C "$DOCS_DIR"
            printf '[protect-docs] Restored docs_dev from backup (%s)\n' "$HOOK_NAME" >&2
        else
            printf '[protect-docs] WARNING: docs_dev missing and no backup archive found (%s).\n' "$HOOK_NAME" >&2
            return 1
        fi
    fi
}

safeguard() {
    backup_docs || return 1
    restore_docs || true
}

ensure_before_operation() {
    if has_docs; then
        backup_docs
    elif [ -f "$BACKUP_ARCHIVE" ]; then
        restore_docs
    else
        printf '[protect-docs] Aborting %s: docs_dev not found and no backup exists.\n' "$HOOK_NAME" >&2
        printf 'Create docs_dev or run scripts/protect_docs_dev.sh backup before retrying.\n' >&2
        exit 1
    fi
}

command=${1:-safeguard}
case "$command" in
    backup)
        backup_docs
        ;;
    restore)
        restore_docs
        ;;
    safeguard)
        safeguard
        ;;
    ensure)
        ensure_before_operation
        ;;
    *)
        printf 'Usage: %s [backup|restore|safeguard|ensure] [hook-name]\n' "$0" >&2
        exit 1
        ;;
 esac
