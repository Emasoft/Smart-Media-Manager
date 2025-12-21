#!/usr/bin/env bash
set -euo pipefail

HOOK_NAME=${2:-manual}
REPO_ROOT="$(git rev-parse --show-toplevel)"
BACKUP_DIR="$REPO_ROOT/.git/local_backups"
PROTECTED_DIRS=("docs_dev" "scripts_dev")

mkdir -p "$BACKUP_DIR"

archive_path() {
    local dir="$1"
    printf '%s/%s.tar.gz' "$BACKUP_DIR" "$dir"
}

has_contents() {
    local dir="$1"
    local target="$REPO_ROOT/$dir"
    [ -d "$target" ] && [ -n "$(ls -A "$target" 2>/dev/null || true)" ]
}

backup_dir() {
    local dir="$1"
    local target="$REPO_ROOT/$dir"
    local archive
    archive="$(archive_path "$dir")"

    if has_contents "$dir"; then
        local tmp_archive="${archive}.tmp"
        tar -czf "$tmp_archive" -C "$target" .
        mv "$tmp_archive" "$archive"
    fi
}

restore_dir() {
    local dir="$1"
    local target="$REPO_ROOT/$dir"
    local archive
    archive="$(archive_path "$dir")"

    if has_contents "$dir"; then
        return 0
    fi

    if [ -f "$archive" ]; then
        mkdir -p "$target"
        tar -xzf "$archive" -C "$target"
        printf '[protect-dev] Restored %s from backup (%s)\n' "$dir" "$HOOK_NAME" >&2
        return 0
    fi

    printf '[protect-dev] WARNING: %s missing and no backup archive found (%s).\n' "$dir" "$HOOK_NAME" >&2
    return 1
}

backup_all() {
    for dir in "${PROTECTED_DIRS[@]}"; do
        backup_dir "$dir"
    done
}

restore_all() {
    local rc=0
    for dir in "${PROTECTED_DIRS[@]}"; do
        restore_dir "$dir" || rc=1
    done
    return $rc
}

safeguard() {
    backup_all
    restore_all || true
}

ensure_before_operation() {
    local missing=()

    for dir in "${PROTECTED_DIRS[@]}"; do
        if has_contents "$dir"; then
            backup_dir "$dir"
            continue
        fi

        local archive
        archive="$(archive_path "$dir")"
        if [ -f "$archive" ]; then
            restore_dir "$dir" || missing+=("$dir")
        else
            missing+=("$dir")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        local list
        list=$(printf '%s, ' "${missing[@]}")
        list=${list%%, }
        printf '[protect-dev] Aborting %s: %s not found and no backup exists.\n' "$HOOK_NAME" "$list" >&2
        printf 'Create the missing directories or run scripts/protect_docs_dev.sh backup before retrying.\n' >&2
        exit 1
    fi
}

command=${1:-safeguard}
case "$command" in
    backup)
        backup_all
        ;;
    restore)
        restore_all
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
