#!/bin/bash
# Runs ON the server (over SSH from the GitLab CI/CD deploy job).
# It expects the environment variables already exported by the job: see
# .gitlab-ci.yml and CI_CD_SETUP.md for the full list.
set -euo pipefail

: "${GIT_REPO_URL:?GIT_REPO_URL is missing}"
: "${DEPLOY_PATH:=/opt/unravel}"
: "${GIT_BRANCH:=main}"

# Normalise to an absolute path in case DEPLOY_PATH arrived without the
# leading slash (e.g. "opt/unravel" instead of "/opt/unravel") — otherwise
# the cd below would land in a directory relative to the SSH user's $HOME.
case "$DEPLOY_PATH" in
  /*) ;;
  *) DEPLOY_PATH="/$DEPLOY_PATH" ;;
esac
echo "== Deploy $(date) — target: $DEPLOY_PATH =="

# /opt (or whatever the parent is) is usually owned by root — the target
# directory is created with sudo and handed over to the user running the
# deploy, so the rest of the script (clone/pull/docker) needs no privileges.
if [ ! -d "$DEPLOY_PATH" ]; then
  sudo mkdir -p "$DEPLOY_PATH"
  sudo chown "$(id -u):$(id -g)" "$DEPLOY_PATH"
fi

# --- Clone or update the repository ---
if [ -d "$DEPLOY_PATH/.git" ]; then
  cd "$DEPLOY_PATH"
  git fetch origin "$GIT_BRANCH"
  git reset --hard "origin/$GIT_BRANCH"
else
  git clone --branch "$GIT_BRANCH" "$GIT_REPO_URL" "$DEPLOY_PATH"
  cd "$DEPLOY_PATH"
fi

# From here on we are ALWAYS inside $DEPLOY_PATH — paths are relative to
# the cwd (never prefixed with $DEPLOY_PATH again) so nothing depends on
# that variable being absolute.

# --- Build .env from the pipeline variables ---
cat > .env <<EOF
POSTGRES_USER=${POSTGRES_USER:-unravel}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-unravel}
POSTGRES_DB=${POSTGRES_DB:-unravel}
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://${POSTGRES_USER:-unravel}:${POSTGRES_PASSWORD:-unravel}@db:5432/${POSTGRES_DB:-unravel}

REDIS_URL=redis://redis:6379/0

OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
OPENROUTER_MODEL=${OPENROUTER_MODEL:-meta/llama-3.1-8b-instruct}
OPENROUTER_BASE_URL=${OPENROUTER_BASE_URL:-https://integrate.api.nvidia.com/v1}
OPENROUTER_SITE_URL=http://${PUBLIC_HOST}:3000
OPENROUTER_APP_NAME=Unravel

GDELT_DOC_API_URL=https://api.gdeltproject.org/api/v2/doc/doc
SEARCH_MAX_RESULTS=20
DISCOVERY_MAX_DEPTH=2
DISCOVERY_MAX_SOURCES=30

BACKEND_CORS_ORIGINS=http://${PUBLIC_HOST}:3000
ENV=production

NEXT_PUBLIC_API_BASE_URL=http://${PUBLIC_HOST}:8000
EOF

# --- Bring the stack up ---
# --force-recreate because "docker compose restart" (or an up with no image
# changes) may not re-read .env — it bit us during development: the backend
# kept using the old API key until the containers were forcibly recreated.
docker compose up -d --build --force-recreate

# --- Clean up old images (keeps each deploy from filling the disk) ---
docker image prune -f

echo "== Deploy finished: http://${PUBLIC_HOST}:3000 =="
