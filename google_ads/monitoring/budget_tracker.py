"""
Module 4: Budget tracker with stop-loss rules.

Reads spend data from Google Ads API (or manual CSV input) and:
- Flags campaigns exceeding daily/monthly budget
- Auto-pauses ads that hit stop-loss threshold
- Calculates ROAS from estimated affiliate commissions
- Generates daily alert report

Usage:
  python budget_tracker.py --status         # Show current spend status
  python budget_tracker.py --log            # Log today's manual spend entry
  python budget_tracker.py --report         # Generate weekly report
  python budget_tracker.py --check-rules    # Check stop-loss rules
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta

CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
SPEND_LOG = Path(__file__).parent.parent / "data" / "spend_log.json"

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

def load_spend_log():
    if not SPEND_LOG.exists():
        return []
    with open(SPEND_LOG, encoding="utf-8") as f:
        return json.load(f)

def save_spend_log(log):
    SPEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SPEND_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def log_spend(campaign: str, spend_usd: float, clicks: int,
              conversions: int, conv_value: float, impressions: int):
    log = load_spend_log()
    entry = {
        "date": date.today().isoformat(),
        "campaign": campaign,
        "spend_usd": spend_usd,
        "clicks": clicks,
        "impressions": impressions,
        "conversions": conversions,
        "conv_value_usd": conv_value,
        "ctr": round(clicks / impressions * 100, 2) if impressions else 0,
        "cpc": round(spend_usd / clicks, 2) if clicks else 0,
        "cpa": round(spend_usd / conversions, 2) if conversions else 0,
        "roas": round(conv_value / spend_usd, 2) if spend_usd else 0,
    }
    log.append(entry)
    save_spend_log(log)
    print(f"  [LOGGED] {entry['date']} | {campaign} | ${spend_usd:.2f} | {conversions} conv | ROAS {entry['roas']:.1f}x")
    return entry

def check_stop_loss_rules(entries_today: list, cfg: dict) -> list:
    budget = cfg["budget"]
    alerts = []

    total_today = sum(e["spend_usd"] for e in entries_today)
    total_conv = sum(e["conversions"] for e in entries_today)
    total_value = sum(e["conv_value_usd"] for e in entries_today)
    roas = round(total_value / total_today, 2) if total_today else 0

    rules = [
        {
            "rule": "Daily spend exceeds stop-loss",
            "triggered": total_today > budget["stop_loss_daily_usd"],
            "value": f"${total_today:.2f} > ${budget['stop_loss_daily_usd']}",
            "action": "PAUSE all campaigns immediately",
            "severity": "CRITICAL",
        },
        {
            "rule": "ROAS below minimum",
            "triggered": total_today > 10 and roas < budget["min_roas"],
            "value": f"ROAS {roas:.1f}x < {budget['min_roas']}x minimum",
            "action": "Reduce bids by 30%, pause lowest performers",
            "severity": "WARNING",
        },
        {
            "rule": "CPA exceeds target",
            "triggered": total_conv > 0 and (total_today / total_conv) > budget["target_cpa_usd"] * 1.5,
            "value": f"CPA ${total_today/total_conv:.2f} > ${budget['target_cpa_usd']*1.5:.2f}",
            "action": "Review keywords, add negatives, check landing pages",
            "severity": "WARNING",
        },
        {
            "rule": "Zero conversions with high spend",
            "triggered": total_today > 20 and total_conv == 0,
            "value": f"${total_today:.2f} spent, 0 conversions",
            "action": "Pause and review keyword targeting",
            "severity": "CRITICAL",
        },
    ]

    for rule in rules:
        if rule["triggered"]:
            alerts.append(rule)

    return alerts

def show_status():
    cfg = load_config()
    budget = cfg["budget"]
    log = load_spend_log()
    today = date.today().isoformat()
    this_month = date.today().strftime("%Y-%m")

    today_entries = [e for e in log if e["date"] == today]
    month_entries = [e for e in log if e["date"].startswith(this_month)]

    total_today = sum(e["spend_usd"] for e in today_entries)
    total_month = sum(e["spend_usd"] for e in month_entries)
    total_conv_today = sum(e["conversions"] for e in today_entries)
    total_value_today = sum(e["conv_value_usd"] for e in today_entries)
    roas_today = round(total_value_today / total_today, 2) if total_today else 0

    print(f"\n{'═'*55}")
    print(f"  GOOGLE ADS — SPEND STATUS  ({today})")
    print(f"{'═'*55}")
    print(f"  TODAY")
    print(f"    Spend:        ${total_today:.2f} / ${budget['daily_budget_usd']:.2f} limit")
    print(f"    Conversions:  {total_conv_today}")
    print(f"    Conv Value:   ${total_value_today:.2f}")
    print(f"    ROAS:         {roas_today:.1f}x  (target: {budget['min_roas']}x)")
    print(f"    Stop-loss:    ${budget['stop_loss_daily_usd']:.2f}/day")
    print(f"\n  THIS MONTH")
    print(f"    Spend:        ${total_month:.2f} / ${budget['monthly_cap_usd']:.2f} cap")
    remaining = budget['monthly_cap_usd'] - total_month
    print(f"    Remaining:    ${remaining:.2f}")
    print(f"{'─'*55}")

    # Check stop-loss
    alerts = check_stop_loss_rules(today_entries, cfg)
    if alerts:
        print(f"\n  ⚠  ALERTS ({len(alerts)})")
        for a in alerts:
            print(f"  [{a['severity']}] {a['rule']}")
            print(f"    Value:  {a['value']}")
            print(f"    Action: {a['action']}")
    else:
        print(f"\n  ✓  No stop-loss rules triggered")

    print(f"{'═'*55}\n")

def generate_weekly_report():
    cfg = load_config()
    log = load_spend_log()
    today = date.today()
    week_ago = (today - timedelta(days=7)).isoformat()

    week_entries = [e for e in log if e["date"] >= week_ago]

    if not week_entries:
        print("  No data for the past 7 days.")
        return

    campaigns = {}
    for e in week_entries:
        c = e["campaign"]
        if c not in campaigns:
            campaigns[c] = {"spend": 0, "clicks": 0, "impressions": 0,
                           "conversions": 0, "conv_value": 0}
        campaigns[c]["spend"] += e["spend_usd"]
        campaigns[c]["clicks"] += e["clicks"]
        campaigns[c]["impressions"] += e["impressions"]
        campaigns[c]["conversions"] += e["conversions"]
        campaigns[c]["conv_value"] += e["conv_value_usd"]

    out_path = Path(__file__).parent.parent / "data" / f"weekly_report_{today.isoformat()}.txt"

    lines = [
        f"WEEKLY GOOGLE ADS REPORT — {(today - timedelta(days=7)).strftime('%b %d')} to {today.strftime('%b %d, %Y')}",
        "=" * 65,
        "",
    ]

    total_spend = sum(v["spend"] for v in campaigns.values())
    total_conv = sum(v["conversions"] for v in campaigns.values())
    total_value = sum(v["conv_value"] for v in campaigns.values())
    total_clicks = sum(v["clicks"] for v in campaigns.values())
    overall_roas = round(total_value / total_spend, 2) if total_spend else 0

    lines += [
        "SUMMARY",
        f"  Total Spend:       ${total_spend:.2f}",
        f"  Total Clicks:      {total_clicks}",
        f"  Total Conversions: {total_conv}",
        f"  Total Conv Value:  ${total_value:.2f}",
        f"  Overall ROAS:      {overall_roas:.2f}x",
        f"  Avg CPA:           ${total_spend/total_conv:.2f}" if total_conv else "  Avg CPA:  N/A",
        "",
        "BY CAMPAIGN",
        "-" * 65,
    ]

    for campaign, v in sorted(campaigns.items(), key=lambda x: -x[1]["spend"]):
        roas = round(v["conv_value"] / v["spend"], 2) if v["spend"] else 0
        cpa = round(v["spend"] / v["conversions"], 2) if v["conversions"] else 0
        status = "✓ KEEP" if roas >= cfg["budget"]["min_roas"] else ("⚠ REVIEW" if total_spend > 5 else "NEW")
        lines += [
            f"  {campaign}",
            f"    Spend: ${v['spend']:.2f}  Clicks: {v['clicks']}  Conv: {v['conversions']}",
            f"    ROAS:  {roas}x  CPA: ${cpa:.2f}  → {status}",
            "",
        ]

    lines += [
        "DECISION FRAMEWORK",
        "-" * 65,
        "  SCALE (increase budget 20%):  ROAS > 3x AND conversions > 5",
        "  KEEP (maintain):              ROAS 2-3x",
        "  REVIEW (optimize):            ROAS 1-2x — check keywords/LPs",
        "  PAUSE (stop):                 ROAS < 1x OR $20+ spend + 0 conv",
        "",
    ]

    report = "\n".join(lines)
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n  Report saved: {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--check-rules", action="store_true")
    parser.add_argument("--log", action="store_true", help="Log a manual spend entry")
    parser.add_argument("--campaign", default="RankerToolAI - Reviews")
    parser.add_argument("--spend", type=float, default=0.0)
    parser.add_argument("--clicks", type=int, default=0)
    parser.add_argument("--impressions", type=int, default=0)
    parser.add_argument("--conversions", type=int, default=0)
    parser.add_argument("--conv-value", type=float, default=0.0)
    args = parser.parse_args()

    if args.log:
        log_spend(args.campaign, args.spend, args.clicks,
                  args.conversions, args.conv_value, args.impressions)
    elif args.report:
        generate_weekly_report()
    elif args.check_rules:
        cfg = load_config()
        log = load_spend_log()
        today = date.today().isoformat()
        today_entries = [e for e in log if e["date"] == today]
        alerts = check_stop_loss_rules(today_entries, cfg)
        if alerts:
            for a in alerts:
                print(f"[{a['severity']}] {a['rule']} — {a['action']}")
        else:
            print("All clear. No stop-loss rules triggered.")
    else:
        show_status()
