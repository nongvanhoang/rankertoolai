"""Shared OAuth2 credential helper for gsc_tracker.py and ga4_tracker.py.

Fails fast instead of hanging/crashing when run unattended (e.g. from a
scheduled task): a broken/expired refresh token or a missing token with no
interactive session both print an actionable error and exit(1) rather than
raising or blocking forever on a browser that will never open.

If a service_account.json (see get_credentials' service_account_file param)
is present, it's used instead of the interactive OAuth flow — no browser, no
local server, no token expiry to babysit. Preferred for unattended/scheduled
scripts; set it up once in Google Cloud Console (IAM → Service Accounts →
Create → Keys → Create new key → JSON) and grant the service account's email
Viewer access on the relevant property/site.
"""
import sys
from pathlib import Path


def get_credentials(token_file: Path, secret_file: Path, scopes: list,
                     force_auth: bool = False, service_account_file: Path = None):
    if service_account_file and service_account_file.exists():
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            str(service_account_file), scopes=scopes
        )
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: pip install google-auth google-auth-oauthlib google-auth-httplib2")
        sys.exit(1)

    creds = None
    if token_file.exists() and not force_auth:
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and not force_auth:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"ERROR: {token_file.name} refresh failed ({e}).")
                print(f"Refresh token likely expired or was revoked. Delete {token_file.name}")
                print("and re-run this script with --auth to re-authenticate interactively.")
                sys.exit(1)
        else:
            # --auth means the user explicitly asked to authenticate now, so always
            # launch the browser flow even if stdin isn't a TTY (e.g. run as a background
            # job) — run_local_server needs a browser, not terminal input, to complete.
            # Without --auth, refuse to guess: an unattended/scheduled run with no
            # cached credentials should fail fast instead of hanging on a browser
            # that will never open.
            if not force_auth and not sys.stdin.isatty():
                print(f"ERROR: no valid credentials in {token_file.name} and no interactive")
                print("session available to authenticate (this looks like an unattended/")
                print("scheduled run). Run this script once interactively with --auth first.")
                sys.exit(1)
            if not secret_file.exists():
                print(f"ERROR: {secret_file} not found.")
                print("Google Cloud Console → APIs & Services → Credentials")
                print("→ Create OAuth client ID → Desktop app → download JSON")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), scopes)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json())

    return creds
