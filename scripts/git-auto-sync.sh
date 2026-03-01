#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "[git-auto-sync][ERROR] $*" >&2
  exit 1
}

log() {
  echo "[git-auto-sync] $*"
}

commit_created="no"
remote_created="no"
push_done="no"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "检测到当前目录不是 Git 仓库，开始初始化..."
  git init >/dev/null 2>&1 || fail "git init 失败"
  git branch -M main >/dev/null 2>&1 || fail "设置 main 分支失败"
fi

branch="$(git symbolic-ref --short -q HEAD || true)"
if [[ -z "$branch" ]]; then
  branch="main"
  git branch -M "$branch" >/dev/null 2>&1 || fail "无法设置默认分支为 $branch"
fi

log "当前分支: $branch"

git add -A || fail "git add -A 失败"

if ! git diff --cached --quiet --ignore-submodules --; then
  msg="chore(auto): sync $(date '+%Y-%m-%d %H:%M')"
  git commit -m "$msg" || fail "自动提交失败"
  commit_created="yes"
  log "已创建提交: $msg"
else
  log "无暂存变更，跳过 commit"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  if gh auth status --hostname github.com >/dev/null 2>&1; then
    repo_name="$(basename "$PWD")"
    log "未检测到 origin，尝试创建 GitHub 私有仓库: $repo_name"

    if gh repo create "$repo_name" --private --source=. --remote=origin >/dev/null 2>&1; then
      remote_created="yes"
      log "已创建远程仓库并设置 origin"
    else
      owner="$(gh api user --jq .login 2>/dev/null || true)"
      if [[ -n "$owner" ]] && gh repo view "$owner/$repo_name" >/dev/null 2>&1; then
        git remote add origin "https://github.com/$owner/$repo_name.git" || fail "远程仓库存在但添加 origin 失败"
        remote_created="yes"
        log "远程仓库已存在，已补充 origin"
      else
        fail "创建远程仓库失败（无 origin）。请检查 gh 权限或仓库命名冲突。"
      fi
    fi
  else
    fail "未检测到 origin 且 gh 未登录，无法自动创建远程仓库。请先执行 gh auth login。"
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin "$branch" || fail "git push 失败（origin/$branch）"
  push_done="yes"
  log "推送成功: origin/$branch"
else
  fail "未找到 origin，无法推送"
fi

log "RESULT commit_created=$commit_created remote_created=$remote_created push_done=$push_done branch=$branch"
