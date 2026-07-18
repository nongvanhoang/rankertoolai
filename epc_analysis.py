# -*- coding: utf-8 -*-
"""
Compute real EPC (earnings-per-click) from affiliate-network exports and rank
active programs so CTA placement/emphasis decisions are based on actual $
data instead of the commission-rate proxy used when no revenue data exists.

No affiliate network here (CJ, PartnerStack, Impact Radius, Rewardful) has an
API integration in this repo, and none should be built without the user's
own API key/credentials (never fabricate one) — so this tool is a CSV/manual
import, matching the existing workflow already used for Semrush's ad-picker
table (user pastes what their dashboard shows, we compute from that).

Usage:
  1. Export or copy a table from your network dashboard with AT LEAST a tool
     name/slug column, a clicks column, and a revenue OR commission column.
     Conversions/signups column is optional but recommended.
  2. Save as CSV, e.g. data/epc_imports/cj_2026-07-25.csv
  3. Run:
       python epc_analysis.py --csv data/epc_imports/cj_2026-07-25.csv --network CJ
  4. Repeat for other networks/exports — each import is appended to
     data/epc_history.json (not overwritten), so trends build up over time.
  5. Run with no --csv to just print the latest known EPC ranking across all
     networks imported so far, cross-referenced with build_dashboard.py's
     commission data for tools with no revenue data yet.

Column name matching is flexible (case-insensitive substring match) since
every network's export uses different headers:
  tool/slug   <- "tool", "slug", "campaign", "advertiser", "product", "offer"
  clicks      <- "clicks", "hits"
  conversions <- "conversions", "signups", "sales", "leads", "actions"
  revenue     <- "revenue", "commission", "earnings", "payout", "amount"
"""
import argparse, csv, json, re, sys
from pathlib import Path
from datetime import datetime, timezone

HISTORY_FILE = Path(__file__).parent / "data" / "epc_history.json"

COLUMN_ALIASES = {
    "tool": ["tool", "slug", "campaign", "advertiser", "product", "offer", "program", "merchant"],
    "clicks": ["clicks", "hits"],
    "conversions": ["conversions", "signups", "sales", "leads", "actions", "orders"],
    "revenue": ["revenue", "commission", "earnings", "payout", "amount", "earned"],
}


def _match_column(headers, aliases):
    headers_lower = {h.lower(): h for h in headers}
    for alias in aliases:
        for h_lower, h_orig in headers_lower.items():
            if alias in h_lower:
                return h_orig
    return None


def _parse_money(val):
    if val is None:
        return 0.0
    s = re.sub(r"[^\d.\-]", "", str(val))
    try:
        return float(s) if s not in ("", "-", ".") else 0.0
    except ValueError:
        return 0.0


def _parse_int(val):
    if val is None:
        return 0
    s = re.sub(r"[^\d\-]", "", str(val))
    try:
        return int(s) if s not in ("", "-") else 0
    except ValueError:
        return 0


def _slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def import_csv(path, network):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        col_tool = _match_column(headers, COLUMN_ALIASES["tool"])
        col_clicks = _match_column(headers, COLUMN_ALIASES["clicks"])
        col_conv = _match_column(headers, COLUMN_ALIASES["conversions"])
        col_rev = _match_column(headers, COLUMN_ALIASES["revenue"])

        if not col_tool or not col_clicks:
            raise SystemExit(
                f"Could not find tool/clicks columns in headers: {headers}\n"
                f"Rename columns to include one of {COLUMN_ALIASES['tool']} and {COLUMN_ALIASES['clicks']}."
            )

        rows = []
        for row in reader:
            name = (row.get(col_tool) or "").strip()
            if not name:
                continue
            clicks = _parse_int(row.get(col_clicks))
            conversions = _parse_int(row.get(col_conv)) if col_conv else None
            revenue = _parse_money(row.get(col_rev)) if col_rev else None
            rows.append({
                "tool": name, "slug": _slugify(name),
                "clicks": clicks, "conversions": conversions, "revenue": revenue,
            })
    return rows


def load_history():
    if not HISTORY_FILE.exists():
        return []
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))


def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def latest_snapshot_per_tool(history):
    """Collapse history to the most recent entry per (network, slug)."""
    latest = {}
    for entry in history:
        key = (entry["network"], entry["slug"])
        if key not in latest or entry["imported_at"] > latest[key]["imported_at"]:
            latest[key] = entry
    return list(latest.values())


def print_ranking(rows):
    if not rows:
        print("No EPC data imported yet. Run with --csv <file> --network <name> first.")
        return
    ranked = sorted(rows, key=lambda r: (r["revenue"] or 0) / max(r["clicks"], 1), reverse=True)
    print(f"\n{'Tool':<20}{'Network':<14}{'Clicks':>8}{'Conv':>7}{'Revenue':>10}{'EPC':>9}{'CVR':>8}")
    print("-" * 76)
    for r in ranked:
        epc = (r["revenue"] or 0) / max(r["clicks"], 1)
        cvr = f"{(r['conversions'] or 0) / r['clicks'] * 100:.1f}%" if r["clicks"] and r["conversions"] is not None else "n/a"
        rev = f"${r['revenue']:.2f}" if r["revenue"] is not None else "n/a"
        conv = str(r["conversions"]) if r["conversions"] is not None else "n/a"
        print(f"{r['tool']:<20}{r['network']:<14}{r['clicks']:>8}{conv:>7}{rev:>10}{epc:>9.3f}{cvr:>8}")
    print(
        "\nEPC = revenue / clicks (real earnings-per-click). Programs with revenue:0 and "
        "meaningful click volume (roughly 10+) are the clearest 'cut candidates' if the pattern "
        "holds across 2+ imports — a single low-click snapshot isn't enough signal to cut a program."
    )


def main():
    ap = argparse.ArgumentParser(description="Compute real EPC from affiliate network exports")
    ap.add_argument("--csv", help="Path to a network export CSV to import")
    ap.add_argument("--network", help="Network label for this import, e.g. CJ, PartnerStack, Impact")
    args = ap.parse_args()

    history = load_history()

    if args.csv:
        if not args.network:
            ap.error("--network is required when importing --csv")
        rows = import_csv(args.csv, args.network)
        now = datetime.now(timezone.utc).isoformat()
        for r in rows:
            r["network"] = args.network
            r["imported_at"] = now
            history.append(r)
        save_history(history)
        print(f"Imported {len(rows)} rows from {args.csv} (network: {args.network})")

    print_ranking(latest_snapshot_per_tool(history))


if __name__ == "__main__":
    main()
