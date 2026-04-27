#!/usr/bin/env bash
# deploy.sh - 部署 hf_space 到 HuggingFace Space
# 用法：bash deploy.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HF_SPACE_DIR="$SCRIPT_DIR/hf_space"
HF_REPO="https://huggingface.co/spaces/centerseed/health123_poc"
ENV_FILE="$SCRIPT_DIR/poc/.env"

# ── 1. 讀取 .env ────────────────────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
  echo "錯誤：找不到 $ENV_FILE" >&2
  exit 1
fi
source "$ENV_FILE"

if [ -z "$HF_TOKEN" ]; then
  echo "錯誤：.env 缺少 HF_TOKEN" >&2
  exit 1
fi
if [ -z "$GOOGLE_API_KEY" ]; then
  echo "錯誤：.env 缺少 GOOGLE_API_KEY" >&2
  exit 1
fi

# ── 2. 同步最新 app.py ──────────────────────────────────────
echo "▶ 同步 app.py ..."
cp "$SCRIPT_DIR/poc/app.py" "$HF_SPACE_DIR/app.py"
# 修正 sys.path：poc 版用 parent.parent，hf_space 版用 parent
sed -i '' 's|parent.parent / "naru_agent"|parent / "naru_agent"|g' "$HF_SPACE_DIR/app.py"

# ── 3. 同步 naru_agent（不含 .git）──────────────────────────
echo "▶ 同步 naru_agent ..."
rsync -a --delete --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  "$SCRIPT_DIR/naru_agent/" "$HF_SPACE_DIR/naru_agent/"

# ── 4. 同步 chroma_db ───────────────────────────────────────
echo "▶ 同步 chroma_db ..."
rsync -a --delete "$SCRIPT_DIR/poc/chroma_db/" "$HF_SPACE_DIR/chroma_db/"

# ── 5. Git commit & push ────────────────────────────────────
cd "$HF_SPACE_DIR"

if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "▶ 初始化 git repo ..."
  git init
  git lfs install
fi

# 確保 remote 存在
if ! git remote get-url hf > /dev/null 2>&1; then
  git remote add hf "$HF_REPO"
fi

git add -A
if git diff --cached --quiet; then
  echo "✅ 沒有變更，跳過 push"
else
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
  git commit -m "deploy: $TIMESTAMP"
  echo "▶ 推送到 HuggingFace ..."
  git push --force "https://centerseed:${HF_TOKEN}@huggingface.co/spaces/centerseed/health123_poc" main
  echo "✅ 推送完成"
fi

# ── 6. 更新 HF Secrets ──────────────────────────────────────
echo "▶ 更新 GOOGLE_API_KEY Secret ..."
curl -s -X POST \
  "https://huggingface.co/api/spaces/centerseed/health123_poc/secrets" \
  -H "Authorization: Bearer ${HF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"key\": \"GOOGLE_API_KEY\", \"value\": \"${GOOGLE_API_KEY}\"}" > /dev/null

echo "▶ 更新 NEON_DATABASE_URL Secret ..."
curl -s -X POST \
  "https://huggingface.co/api/spaces/centerseed/health123_poc/secrets" \
  -H "Authorization: Bearer ${HF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"key\": \"NEON_DATABASE_URL\", \"value\": \"${NEON_DATABASE_URL}\"}" > /dev/null

echo ""
echo "✅ 部署完成：https://huggingface.co/spaces/centerseed/health123_poc"
