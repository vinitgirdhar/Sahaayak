# Sahaayak

Sahaayak is a Flask-based marketplace for street vendors and wholesalers. It includes vendor discovery, cart and checkout flows, wholesaler product management, order tracking, profile management, analytics, and a Gemini-powered market insight endpoint.

## Highlights

- Vendor registration, login, dashboard, cart, checkout, and order history
- Wholesaler registration, approval flow, login, dashboard, product management, and order handling
- SQLite-backed data model with seeded sample data for local development
- Server-rendered UI with responsive vendor and wholesaler dashboards
- AI-assisted market insights through `google-generativeai`
- Script-based pre-deployment verification suite

## Tech Stack

- Python 3.11+
- Flask 2.3
- SQLite
- Tailwind via CDN in templates
- `google-generativeai` for the AI endpoint

## Project Layout

```text
Sahaayak/
|-- app.py
|-- config.py
|-- vendor_clubs.db
|-- my_app/
|   |-- __init__.py
|   |-- db.py
|   |-- routes.py
|   |-- templates/
|   `-- static/
|-- validate_mock_data.py
|-- data_integrity_check.py
|-- test_user_flow.py
|-- final_verification.py
|-- verification_helper.py
`-- MANUAL_VERIFICATION.md
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optionally create a `.env` file:

```env
SECRET_KEY=change-this-for-local-dev
GEMINI_API_KEY=your-gemini-key
```

4. Start the app:

```bash
python app.py
```

The app initializes `vendor_clubs.db` automatically on startup if the schema is missing.

## Seeded Local Credentials

These are development/demo credentials created by `init_db()` when the database is empty.

- Admin: `admin` / `admin123`
- Vendor: `9876543210` / `vendor123`
- Wholesaler: `9999999999` / `password123`

## Configuration

Important settings live in `config.py`.

- `SECRET_KEY`: Flask session secret
- `GEMINI_API_KEY`: API key used by `/api/ask-ai`
- `DATABASE`: defaults to `vendor_clubs.db`
- `UPLOAD_FOLDER`: defaults to `my_app/static/uploads`

The verification suite can override `DATABASE` and `UPLOAD_FOLDER` at runtime so checks run against disposable copies instead of the checked-in database and static files.

## Verification Scripts

Run these from the project root.

```bash
python validate_mock_data.py
python data_integrity_check.py
python test_user_flow.py
python final_verification.py
```

What they do:

- `validate_mock_data.py`: validates the disposable verification fixture and seeded test entities
- `data_integrity_check.py`: checks schema shape, foreign key declarations, orphan records, numeric sanity, file references, and whether app-style SQLite connections enable foreign keys
- `test_user_flow.py`: runs end-to-end route checks with Flask `test_client`, including vendor, wholesaler, API, cart, checkout, and mocked AI flows
- `final_verification.py`: runs deployment preflight checks for the current Vercel target

For the optional live AI smoke test:

```bash
set VERIFY_LIVE_GEMINI=1
python test_user_flow.py
```

If `VERIFY_LIVE_GEMINI` is not set, the AI flow is tested with mocks by default.

## Manual QA

Use the checklist in `MANUAL_VERIFICATION.md` for the browser pass. It covers:

- Desktop viewport: `1440x900`
- Mobile viewport: `390x844`
- Core vendor and wholesaler pages
- Responsive layout issues, clipped content, missing assets, and interaction checks

## Deployment Notes

The repository includes a `vercel.json`, but the current runtime defaults are still local-file based:

- database: `vendor_clubs.db`
- uploads: `my_app/static/uploads`

That works for local development, but it is not a production-safe storage strategy for a serverless deployment target like Vercel. The deployment preflight script is designed to fail until you replace those with persistent production storage and provide a real `SECRET_KEY`.

## Current Production Caveats

- SQLite foreign key enforcement is not yet enabled on app-style connections
- Local SQLite and local uploads are still treated as deployment blockers for Vercel
- `SECRET_KEY` must be set in the deployment environment

## License

This project is licensed under the MIT License. See `LICENSE` for details.
