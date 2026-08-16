#!/bin/bash
# Se ejecuta EN el servidor (vía SSH desde el job de deploy de GitLab CI/CD).
# Espera las variables de entorno ya exportadas por el job: ver .gitlab-ci.yml
# y CI_CD_SETUP.md para la lista completa.
set -euo pipefail

: "${GIT_REPO_URL:?falta GIT_REPO_URL}"
: "${DEPLOY_PATH:=/opt/unravel}"
: "${GIT_BRANCH:=main}"

# Normaliza a ruta absoluta por si DEPLOY_PATH llegó sin la barra inicial
# (ej. "opt/unravel" en vez de "/opt/unravel") — si no, cd más abajo
# terminaría parado en un directorio relativo al $HOME del usuario SSH.
case "$DEPLOY_PATH" in
  /*) ;;
  *) DEPLOY_PATH="/$DEPLOY_PATH" ;;
esac
echo "== Deploy $(date) — destino: $DEPLOY_PATH =="

# /opt (o el padre que sea) suele ser de root — se crea el directorio de
# destino con sudo y se lo cede al usuario que corre el deploy, así el
# resto del script (clone/pull/docker) no necesita privilegios.
if [ ! -d "$DEPLOY_PATH" ]; then
  sudo mkdir -p "$DEPLOY_PATH"
  sudo chown "$(id -u):$(id -g)" "$DEPLOY_PATH"
fi

# --- Clonar o actualizar el repo ---
if [ -d "$DEPLOY_PATH/.git" ]; then
  cd "$DEPLOY_PATH"
  git fetch origin "$GIT_BRANCH"
  git reset --hard "origin/$GIT_BRANCH"
else
  git clone --branch "$GIT_BRANCH" "$GIT_REPO_URL" "$DEPLOY_PATH"
  cd "$DEPLOY_PATH"
fi

# A partir de acá SIEMPRE estamos parados dentro de $DEPLOY_PATH — se usan
# rutas relativas al cwd (no se vuelve a prefijar con $DEPLOY_PATH) para no
# depender de que la variable sea absoluta.

# --- Armar .env desde las variables del pipeline ---
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

# --- Levantar el stack ---
# --force-recreate porque "docker compose restart" (o un up sin cambios de
# imagen) puede no releer el .env — nos pasó durante el desarrollo: el
# backend seguía usando la API key vieja hasta forzar la recreación.
docker compose up -d --build --force-recreate

# --- Limpieza de imágenes viejas (evita llenar el disco con cada deploy) ---
docker image prune -f

echo "== Deploy listo: http://${PUBLIC_HOST}:3000 =="
