#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TARGET_ROOT=${1:-.}
TARGET_ROOT=$(CDPATH= cd -- "$TARGET_ROOT" && pwd)

if ! git -C "$TARGET_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: target is not a Git repository: $TARGET_ROOT" >&2
  exit 1
fi

mkdir -p \
  "$TARGET_ROOT/scripts" \
  "$TARGET_ROOT/docs" \
  "$TARGET_ROOT/.github/workflows"

copy_standard() {
  source_path=$1
  target_path=$2

  if [ "$source_path" = "$target_path" ]; then
    return
  fi

  cp "$source_path" "$target_path"
  echo "installed: ${target_path#"$TARGET_ROOT"/}"
}

copy_standard "$SOURCE_ROOT/.gitmessage" "$TARGET_ROOT/.gitmessage"
copy_standard \
  "$SOURCE_ROOT/scripts/check_commit_message.py" \
  "$TARGET_ROOT/scripts/check_commit_message.py"
copy_standard \
  "$SOURCE_ROOT/scripts/export_commit_context.py" \
  "$TARGET_ROOT/scripts/export_commit_context.py"
copy_standard \
  "$SOURCE_ROOT/docs/commit-convention.md" \
  "$TARGET_ROOT/docs/commit-convention.md"
copy_standard \
  "$SOURCE_ROOT/docs/commit-workflow.md" \
  "$TARGET_ROOT/docs/commit-workflow.md"
copy_standard \
  "$SOURCE_ROOT/.github/workflows/commit-lint.yml" \
  "$TARGET_ROOT/.github/workflows/commit-lint.yml"

if [ ! -f "$TARGET_ROOT/.commit-documentation-baseline" ] && \
  baseline=$(git -C "$TARGET_ROOT" rev-parse --verify HEAD 2>/dev/null); then
  printf '%s\n' "$baseline" > "$TARGET_ROOT/.commit-documentation-baseline"
  echo "created: .commit-documentation-baseline"
fi

chmod +x "$TARGET_ROOT/scripts/check_commit_message.py"
chmod +x "$TARGET_ROOT/scripts/export_commit_context.py"
git -C "$TARGET_ROOT" config --local commit.template .gitmessage

GIT_DIR=$(git -C "$TARGET_ROOT" rev-parse --absolute-git-dir)
HOOK_PATH="$GIT_DIR/hooks/commit-msg"
cat > "$HOOK_PATH" <<'HOOK'
#!/bin/sh
repo_root=$(git rev-parse --show-toplevel)
exec python3 "$repo_root/scripts/check_commit_message.py" "$1"
HOOK
chmod +x "$HOOK_PATH"

echo "configured: commit.template=.gitmessage"
echo "installed: .git/hooks/commit-msg"
echo "commit documentation standard is ready in $TARGET_ROOT"