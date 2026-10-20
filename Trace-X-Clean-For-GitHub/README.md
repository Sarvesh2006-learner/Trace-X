# TRACE-X Full-Stack Forensic Evidence Analyzer

TRACE-X is a final-year project implementation combining a Flask backend and browser frontend.

## Features
- Investigator registration/login with password hashing
- Admin seed account
- Evidence upload and safe generated storage names
- SHA-256 hash for every evidence file
- Exact binary duplicate detection
- Text extraction from TXT/CSV/JSON/XML/LOG/PDF/DOCX
- Normalized content SHA-256 for cross-format identical text
- Sentence Transformer semantic similarity (optional heavy dependency/model download)
- Image pHash similarity
- ELA-style recompression difference indicator
- SQLite evidence register
- Admin activity log for sign-ins, sign-outs, registrations, and evidence actions
- Automatic PDF forensic report
- REST API + dashboard UI

## Important forensic limitation
TRACE-X reports indicators. It does not certify that a file is genuine/fake, nor that an image is definitely morphed. Hashes prove byte-level identity; similarity and ELA require investigator review.

## Windows setup
1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run `install_windows.bat`.
4. Run `run_windows.bat`.
5. Open http://127.0.0.1:5000

The setup creates a `.venv` virtual environment. If PowerShell blocks activation, do not activate it; the batch files call `.venv\Scripts\python.exe` directly.

## Default admin
username: admin
password: admin123

Change this before real deployment.

## API
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
GET  /api/admin/activity (admin only; supports limit and offset)
POST /api/evidence/upload
GET  /api/evidence
GET  /api/evidence/<id>
GET  /api/evidence/<id>/download
GET  /api/evidence/<id>/report

The SQLite file is `database/tracex.db`; activity events are stored in its `activity_logs` table. After startup, sign in with an admin account and open **Activity Log** from the dashboard to review recorded activity. Events created before activity logging was added cannot be reconstructed from the existing database.

## Project structure
backend/
frontend/
database/
storage/
tests/

All Python packages contain __init__.py files so imports such as `backend.forensic.hash_engine` work when running from the project root.
