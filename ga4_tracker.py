#!/usr/bin/env python3
"""
Google Analytics 4 click/event tracker for rankertoolai.com.

Pulls real numbers for the events already fired by assets/js/main.js and
/go/ redirect pages (affiliate_click, cta_click, outbound_click, form_submit,
internal_navigate, site_search, faq_expand, scroll_depth, engaged) and prints
a console report or dumps JSON for build_dashboard.py to embed.

Setup (one-time):
  1. pip install google-analytics-data google-analytics-admin google-auth-oauthlib
  2. Reuse the same Google Cloud project as gsc_tracker.py (or create one):
     https://console.cloud.google.com/ → APIs & Services → Library
     → enable "Google Analytics Data API" and "Google Analytics Admin API"
  3. Auth — service account (recommended, no browser/local-server needed,
     works unattended forever): IAM & Admin → Service Accounts → Create
     Service Account → Keys → Add key → Create new key → JSON → save as
     ga4_service_account.json in this folder. Then in GA4 Admin → Property
     Access Management, add the service account's email (ends in
     .iam.gserviceaccount.com) as a Viewer.
     (Viewer is enough to pull reports; use Editor if you also plan to run
     --register-dimensions, which needs write access to create dimensions.)
     OR — OAuth Desktop client (needs a one-time interactive browser login,
     and re-auth if the token ever expires/is revoked): APIs & Services →
     Credentials → Create Credentials → OAuth client ID → Desktop app →
     download as client_secret.json in this folder, then run with --auth.
  4. Find your GA4 Property ID: analytics.google.com → Admin (bottom left)
     → Property Settings → "PROPERTY ID" (a 9-10 digit number, NOT the
     "G-XXXXXXXXXX" measurement ID used in the site's <script> tag).
  5. Create ga4_config.json in this folder: {"property_id": "123456789"}
     (running the script once with no config file will create a template)
  6. If using OAuth (not service account): python ga4_tracker.py --auth
  7. Register custom dimensions once so tool/cta_context/etc. are queryable:
     python ga4_tracker.py --register-dimensions
     (GA4 only reports on event parameters — tool, cta_context, page_section,
     outbound_domain, destination, form_id — once they're registered as
     custom dimensions; events sent before registration won't backfill)

Usage:
  python ga4_tracker.py                        # 7-day summary report
  python ga4_tracker.py --days 28              # last 28 days
  python ga4_tracker.py --json ga4_report.json # dump for build_dashboard.py
  python ga4_tracker.py --csv ga4_events.csv   # export raw event counts
  python ga4_tracker.py --register-dimensions  # one-time GA4 setup
"""
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

TOKEN_FILE  = Path(__file__).parent / "ga4_token.json"
SECRET_FILE = Path(__file__).parent / "client_secret.json"
CONFIG_FILE = Path(__file__).parent / "ga4_config.json"
SERVICE_ACCOUNT_FILE = Path(__file__).parent / "ga4_service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/analytics.edit",
]

# event_name -> custom dimension (event parameter) worth breaking down by
EVENT_BREAKDOWNS = {
    "affiliate_click":   "tool",
    "cta_click":         "cta_context",
    "outbound_click":    "outbound_domain",
    "internal_navigate": "destination",
    "form_submit":       "form_id",
    "site_search":       "search_term",
    "engaged":           "page_section",
}
CUSTOM_DIMENSIONS = sorted(set(EVENT_BREAKDOWNS.values()))


def load_property_id(override: str = None) -> str:
    if override:
        return override
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"property_id": "REPLACE_ME"}, indent=2))
        print(f"ERROR: {CONFIG_FILE} not found — created a template.")
        print("Fill in your GA4 Property ID (Admin → Property Settings → PROPERTY ID)")
        print("then re-run. Or pass --property-id 123456789 directly.")
        sys.exit(1)
    data = json.loads(CONFIG_FILE.read_text())
    pid = data.get("property_id", "")
    if not pid or pid == "REPLACE_ME":
        print(f"ERROR: set a real property_id in {CONFIG_FILE}")
        sys.exit(1)
    return pid


def get_credentials(force_auth=False):
    from google_oauth import get_credentials as _get_credentials
    return _get_credentials(TOKEN_FILE, SECRET_FILE, SCOPES, force_auth=force_auth,
                             service_account_file=SERVICE_ACCOUNT_FILE)


def build_data_client(force_auth=False):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    return BetaAnalyticsDataClient(credentials=get_credentials(force_auth=force_auth))


def build_admin_client(force_auth=False):
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    return AnalyticsAdminServiceClient(credentials=get_credentials(force_auth=force_auth))


def run_report(client, property_id, dimensions, metrics, days,
                event_filter=None, order_metric=None, limit=25):
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, OrderBy,
        FilterExpression, Filter,
    )

    kwargs = dict(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        limit=limit,
    )
    if event_filter:
        kwargs["dimension_filter"] = FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value=event_filter),
            )
        )
    if order_metric:
        kwargs["order_bys"] = [OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True
        )]

    resp = client.run_report(RunReportRequest(**kwargs))
    rows = []
    for row in resp.rows:
        rows.append({
            "dims": [v.value for v in row.dimension_values],
            "metrics": [v.value for v in row.metric_values],
        })
    return rows


def fetch_totals(client, property_id, days) -> dict:
    rows = run_report(
        client, property_id, dimensions=[],
        metrics=["totalUsers", "sessions", "engagementRate",
                 "averageSessionDuration", "screenPageViews"],
        days=days, limit=1,
    )
    if not rows:
        return {}
    m = rows[0]["metrics"]
    return {
        "users": int(float(m[0])),
        "sessions": int(float(m[1])),
        "engagement_rate": round(float(m[2]) * 100, 1),
        "avg_session_sec": round(float(m[3]), 0),
        "pageviews": int(float(m[4])),
    }


def fetch_events_summary(client, property_id, days) -> list:
    rows = run_report(
        client, property_id, dimensions=["eventName"], metrics=["eventCount"],
        days=days, order_metric="eventCount", limit=50,
    )
    return [{"name": r["dims"][0], "count": int(r["metrics"][0])} for r in rows]


def fetch_breakdown(client, property_id, event_name, dimension_param, days, limit=15):
    from google.api_core.exceptions import InvalidArgument
    try:
        rows = run_report(
            client, property_id,
            dimensions=[f"customEvent:{dimension_param}"], metrics=["eventCount"],
            days=days, event_filter=event_name, order_metric="eventCount", limit=limit,
        )
    except InvalidArgument:
        print(f"  (skip breakdown '{dimension_param}' for {event_name}: dimension not "
              f"registered yet — run `python ga4_tracker.py --register-dimensions`)")
        return []
    except Exception as e:
        print(f"  ERROR fetching breakdown '{dimension_param}' for {event_name}: {e}")
        return []
    return [{"value": r["dims"][0] or "(not set)", "count": int(r["metrics"][0])} for r in rows]


def fetch_top_pages(client, property_id, days, limit=20) -> list:
    rows = run_report(
        client, property_id, dimensions=["pagePath"],
        metrics=["screenPageViews", "sessions"], days=days,
        order_metric="screenPageViews", limit=limit,
    )
    return [{"path": r["dims"][0], "views": int(r["metrics"][0]),
              "sessions": int(r["metrics"][1])} for r in rows]


def build_full_report(client, property_id, days) -> dict:
    print("Fetching totals...")
    totals = fetch_totals(client, property_id, days)
    print("Fetching event summary...")
    events = fetch_events_summary(client, property_id, days)
    print("Fetching top pages...")
    top_pages = fetch_top_pages(client, property_id, days)

    breakdowns = {}
    for event_name, dim in EVENT_BREAKDOWNS.items():
        if not any(e["name"] == event_name for e in events):
            continue
        print(f"Fetching breakdown: {event_name} by {dim}...")
        breakdowns[event_name] = fetch_breakdown(client, property_id, event_name, dim, days)

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "days": days,
        "totals": totals,
        "events": events,
        "breakdowns": breakdowns,
        "top_pages": top_pages,
    }


def print_report(report: dict):
    t = report["totals"]
    print(f"\n{'='*70}")
    print(f"  RankerToolAI — GA4 Summary — last {report['days']} days")
    print(f"{'='*70}")
    if t:
        print(f"  Users: {t['users']:,}   Sessions: {t['sessions']:,}   "
              f"Pageviews: {t['pageviews']:,}")
        print(f"  Engagement rate: {t['engagement_rate']}%   "
              f"Avg session: {t['avg_session_sec']:.0f}s")

    print(f"\n  {'Event':<22} {'Count':>10}")
    print(f"  {'-'*22} {'-'*10}")
    for e in report["events"]:
        print(f"  {e['name']:<22} {e['count']:>10,}")

    for event_name, rows in report["breakdowns"].items():
        if not rows:
            continue
        dim = EVENT_BREAKDOWNS[event_name]
        print(f"\n  {event_name} by {dim}:")
        for r in rows[:10]:
            print(f"    {r['value']:<30} {r['count']:>8,}")

    print(f"\n  Top pages by views:")
    for p in report["top_pages"][:15]:
        print(f"    {p['path']:<45} {p['views']:>8,}  ({p['sessions']:,} sessions)")


def register_dimensions(property_id, force_auth=False):
    from google.analytics.admin_v1beta.types import CustomDimension
    client = build_admin_client(force_auth=force_auth)
    parent = f"properties/{property_id}"
    existing = {cd.parameter_name for cd in client.list_custom_dimensions(parent=parent)}
    print(f"Existing custom dimensions: {sorted(existing) or '(none)'}")

    for name in CUSTOM_DIMENSIONS:
        if name in existing:
            print(f"  {name}: already registered, skip")
            continue
        client.create_custom_dimension(
            parent=parent,
            custom_dimension=CustomDimension(
                parameter_name=name,
                display_name=name,
                scope=CustomDimension.DimensionScope.EVENT,
            ),
        )
        print(f"  {name}: created")
    print("\nDone. New events from now on will populate these dimensions")
    print("(historical events sent before registration will NOT backfill).")


def main():
    parser = argparse.ArgumentParser(description="GA4 click/event tracker for rankertoolai.com")
    parser.add_argument("--auth", action="store_true", help="Force re-authentication")
    parser.add_argument("--days", type=int, default=7, help="Date range in days (default: 7)")
    parser.add_argument("--property-id", help="Override property_id from ga4_config.json")
    parser.add_argument("--json", metavar="FILE", help="Dump full report as JSON")
    parser.add_argument("--csv", metavar="FILE", help="Export raw event counts to CSV")
    parser.add_argument("--register-dimensions", action="store_true",
                        help="One-time: create GA4 custom dimensions for tool/cta_context/etc.")
    args = parser.parse_args()

    if args.auth and TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print("Cleared cached token. Re-authenticating...")

    property_id = load_property_id(args.property_id)

    if args.register_dimensions:
        register_dimensions(property_id, force_auth=args.auth)
        return

    print("Connecting to Google Analytics Data API...")
    client = build_data_client(force_auth=args.auth)

    report = build_full_report(client, property_id, args.days)
    print_report(report)

    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nJSON exported: {args.json}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["event_name", "count"])
            for e in report["events"]:
                writer.writerow([e["name"], e["count"]])
        print(f"CSV exported: {args.csv}")

    print(f"\nDone. Run with --help to see all options.")


if __name__ == "__main__":
    main()
