#!/usr/bin/env python3
"""
Run deployment preflight checks for the current Vercel target.
"""

import json
import os
from pathlib import Path

from config import Config
from verification_helper import LIVE_GEMINI_ENV_VAR


PROJECT_ROOT = Path(__file__).resolve().parent
VERCEL_CONFIG_PATH = PROJECT_ROOT / 'vercel.json'
DEFAULT_SECRET_KEY = 'a-very-secret-key-that-you-should-change'


def report(ok, message, failures, warnings):
    if ok:
        print(f"[PASS] {message}")
        return

    print(f"[FAIL] {message}")
    failures.append(message)


def warn(message, warnings):
    print(f"[WARN] {message}")
    warnings.append(message)


def main():
    failures = []
    warnings = []

    print("SAHAAYAK DEPLOYMENT PREFLIGHT")
    print("=============================")

    report(VERCEL_CONFIG_PATH.exists(), 'vercel.json is present', failures, warnings)
    if VERCEL_CONFIG_PATH.exists():
        with VERCEL_CONFIG_PATH.open('r', encoding='utf-8') as handle:
            vercel_config = json.load(handle)

        builds = vercel_config.get('builds', [])
        routes = vercel_config.get('routes', [])
        build_ok = any(
            build.get('src') == 'app.py' and build.get('use') == '@vercel/python'
            for build in builds
        )
        route_ok = any(route.get('dest') == 'app.py' for route in routes)

        report(build_ok, 'Vercel build points to app.py via @vercel/python', failures, warnings)
        report(route_ok, 'Vercel routes dispatch traffic to app.py', failures, warnings)

    secret_key = os.getenv('SECRET_KEY')
    report(
        bool(secret_key) and secret_key != DEFAULT_SECRET_KEY,
        'SECRET_KEY is supplied via the environment and is not the default value',
        failures,
        warnings,
    )

    live_gemini_requested = os.getenv(LIVE_GEMINI_ENV_VAR) == '1'
    gemini_key = os.getenv('GEMINI_API_KEY')
    if live_gemini_requested:
        report(
            bool(gemini_key),
            f'GEMINI_API_KEY is set when {LIVE_GEMINI_ENV_VAR}=1',
            failures,
            warnings,
        )
    elif not gemini_key:
        warn('GEMINI_API_KEY is not set; live Gemini smoke checks will be skipped.', warnings)

    database_path = str(Config.DATABASE)
    upload_folder = str(Config.UPLOAD_FOLDER)
    uses_local_sqlite = database_path.endswith('.db') and not Path(database_path).is_absolute()
    uses_local_uploads = upload_folder.replace('\\', '/').startswith('my_app/static/uploads')

    report(
        not uses_local_sqlite,
        'runtime database is not a repo-local SQLite file',
        failures,
        warnings,
    )
    if uses_local_sqlite:
        print(f"       Config.DATABASE={database_path}")

    report(
        not uses_local_uploads,
        'runtime uploads are not stored in repo-local my_app/static/uploads',
        failures,
        warnings,
    )
    if uses_local_uploads:
        print(f"       Config.UPLOAD_FOLDER={upload_folder}")

    if failures:
        print("")
        print("Deployment preflight failed.")
        return 1

    if warnings:
        print("")
        print(f"Deployment preflight passed with {len(warnings)} warning(s).")
        return 0

    print("")
    print("Deployment preflight passed.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
