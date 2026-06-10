#!/usr/bin/env bash
# Compiles the Tailwind stylesheet used by all templates.
#
# Usage:
#   ./build_css.sh           # minified production build
#   ./build_css.sh --watch   # rebuild on change during development
#
# Requires the Tailwind standalone CLI (no Node needed):
#   https://github.com/tailwindlabs/tailwindcss/releases (v3.x)
# Either put `tailwindcss` on your PATH or set TAILWIND_BIN.
set -euo pipefail
cd "$(dirname "$0")"

BIN="${TAILWIND_BIN:-tailwindcss}"
if ! command -v "$BIN" >/dev/null 2>&1; then
  echo "tailwindcss CLI not found. Install the standalone binary from" >&2
  echo "https://github.com/tailwindlabs/tailwindcss/releases or set TAILWIND_BIN." >&2
  exit 1
fi

ARGS=(-c tailwind.config.js -i my_app/static/css/input.css -o my_app/static/css/app.css)
if [[ "${1:-}" == "--watch" ]]; then
  exec "$BIN" "${ARGS[@]}" --watch
else
  exec "$BIN" "${ARGS[@]}" --minify
fi
