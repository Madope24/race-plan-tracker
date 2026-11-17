#!/usr/bin/env sh
# Runs ON the server (called by the deploy and rollback workflows). Starts API_IMAGE, waits for /health,
# runs the smoke tests, and rolls back to the previous image automatically if anything fails.
#   Needed env: API_IMAGE POSTGRES_PASSWORD JWT_SECRET APP_PORT REGISTRATION_MODE STACK (salum-tracker | salum-tracker-staging)
set -eu
cd "$(dirname "$0")"
: "${STACK:?}" "${API_IMAGE:?}" "${POSTGRES_PASSWORD:?}" "${JWT_SECRET:?}" "${APP_PORT:?}"
umask 077
[ -f .env ] && grep '^API_IMAGE=' .env | cut -d= -f2- > .previous_image || true
write_env() {
  printf 'API_IMAGE=%s\nPOSTGRES_PASSWORD=%s\nJWT_SECRET=%s\nAPP_PORT=%s\nREGISTRATION_MODE=%s\n' \
    "$1" "$POSTGRES_PASSWORD" "$JWT_SECRET" "$APP_PORT" "${REGISTRATION_MODE:-first-only}" > .env
}
smoke() {
  docker compose -p "$STACK" exec -T api python - <<'PY'
import json, urllib.request, urllib.error
base = 'http://127.0.0.1:8000'
h = json.load(urllib.request.urlopen(base + '/health', timeout=5))
assert h['ok'], h
p = json.load(urllib.request.urlopen(base + '/api/v1/plan', timeout=30))
assert len(p['days']) > 100 and p['sessions'], 'plan is empty'
try:
    urllib.request.urlopen(base + '/api/v1/sync', timeout=5)
    raise SystemExit('sync must require sign-in')
except urllib.error.HTTPError as e:
    assert e.code == 401, e.code
print('smoke tests passed: health, plan (%d days), auth' % len(p['days']))
PY
}
start() {
  write_env "$1"
  docker compose -p "$STACK" pull api
  docker compose -p "$STACK" up -d --remove-orphans
  for i in $(seq 1 40); do
    if docker compose -p "$STACK" exec -T api python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" >/dev/null 2>&1; then
      smoke && return 0
      return 1
    fi
    sleep 3
  done
  return 1
}
chmod +x backup.sh 2>/dev/null || true
if start "$API_IMAGE"; then
  echo "$API_IMAGE" >> deployed_images.log
  docker image prune -f >/dev/null
  echo "Deployed $API_IMAGE to $STACK on port $APP_PORT"
  exit 0
fi
echo "Deploy of $API_IMAGE failed. Last logs:"
docker compose -p "$STACK" logs --tail 80 api || true
if [ -s .previous_image ]; then
  PREV=$(cat .previous_image)
  echo "Rolling back to $PREV"
  start "$PREV" && echo "Rolled back to $PREV" || echo "Rollback failed: check the server"
fi
exit 1
