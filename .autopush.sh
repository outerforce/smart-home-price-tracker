#!/bin/bash
# 自动追加 commit 并推送到 GitHub
# 调用方式: bash /workspace/.autopush.sh "commit message"
set -e

REPO_DIR="/workspace"
MSG="${1:-$(date '+%Y-%m-%d %H:%M')} 更新"

cd "$REPO_DIR"

# 添加所有变更
git add -A

# 检查是否有变更
if git diff --cached --quiet; then
    echo "✅ 暂无新变更"
    exit 0
fi

# 设置分支（master 或 main）
BRANCH=$(git branch --show-current)
[ -z "$BRANCH" ] && BRANCH="master"

# Commit
git commit -m "$MSG"

# Push
git push origin "$BRANCH"

echo "✅ 已推送: $MSG"
