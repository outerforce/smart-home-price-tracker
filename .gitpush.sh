#!/bin/bash
# Git 自动推送脚本
set -e

REPO_DIR="/workspace"
cd "$REPO_DIR"

echo "📦 检查 Git 状态..."

# 初始化（如果需要）
if [ ! -d ".git" ]; then
    echo "🔧 初始化 Git 仓库..."
    git init
    git config user.email "agent@openclaw.ai"
    git config user.name "OpenClaw Agent"
    echo "✅ Git 初始化完成"
else
    echo "✅ Git 仓库已存在"
fi

# 检查是否有 remote
if ! git remote -v | grep -q "origin"; then
    echo "⚠️ 未设置 remote origin，请先设置："
    echo "   git remote add origin https://github.com/你的用户名/你的仓库名.git"
    echo "   或直接编辑 .git/config 添加 remote"
    exit 1
fi

# 添加所有更改
echo "📝 暂存所有文件..."
git add -A

# 检查是否有变更
if git diff --cached --quiet; then
    echo "✅ 暂无新变更需要提交"
else
    # 获取当前分支名
    BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    if [ -z "$BRANCH" ]; then
        BRANCH="main"
        git branch -m "$BRANCH" 2>/dev/null || true
    fi

    # 自动 commit
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
    git commit -m "feat: $(date '+%Y-%m-%d') 更新"

    # 推送到 GitHub
    echo "🚀 推送到 GitHub (branch: $BRANCH)..."
    git push -u origin "$BRANCH" --force
    echo "✅ 推送完成！"
fi
