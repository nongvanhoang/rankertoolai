"""
RankerToolAI Weekly Operations Script
Chạy mỗi thứ 6 để có bức tranh toàn cảnh và lên kế hoạch tuần tới.

Usage:
  python weekly_ops.py          -- Weekly report đầy đủ
  python weekly_ops.py --quick  -- Chỉ stats nhanh
  python weekly_ops.py --plan   -- Kế hoạch content tuần tới
"""

import os
import sys
import sqlite3
import json
import glob
import datetime
import subprocess
import argparse

# Load .env nếu có
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "social_agent", ".env"))
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(ROOT, "html")
SOCIAL_DB = os.path.join(ROOT, "social_agent", "data", "posts.db")
TOOLS_FILE = os.path.join(ROOT, "social_agent", "data", "tools.json")
LOG_FILE = os.path.join(ROOT, "social_agent", "data", "run_log.txt")

# Commission rates cho mỗi tool (% recurring hoặc per-sale)
COMMISSION = {
    "semrush":     {"rate": 0.40, "avg_price": 129, "type": "recurring"},
    "jasper":      {"rate": 0.30, "avg_price": 59,  "type": "lifetime"},
    "writesonic":  {"rate": 0.30, "avg_price": 49,  "type": "recurring"},
    "surfer-seo":  {"rate": 0.25, "avg_price": 89,  "type": "recurring"},
    "elevenlabs":  {"rate": 0.22, "avg_price": 22,  "type": "12months"},
    "canva-ai":    {"rate": 0.15, "avg_price": 15,  "type": "per_sale"},
    "copy-ai":     {"rate": 0.20, "avg_price": 49,  "type": "recurring"},
    "pictory":     {"rate": 0.20, "avg_price": 39,  "type": "recurring"},
    "notion":      {"rate": None, "avg_price": 10,  "type": "per_referral"},
}

# Content gaps — trang chưa có nhưng nên tạo (theo revenue priority)
CONTENT_GAPS = [
    {"type": "compare", "a": "semrush", "b": "ahrefs",        "priority": 1, "reason": "Semrush 40%"},
    {"type": "compare", "a": "jasper",  "b": "writesonic",    "priority": 1, "reason": "30%+30%"},
    {"type": "compare", "a": "surfer-seo", "b": "clearscope", "priority": 1, "reason": "Surfer 25%"},
    {"type": "alts",    "slug": "semrush",                    "priority": 1, "reason": "40% recurring"},
    {"type": "best",    "slug": "ai-tools-for-marketers",     "priority": 2, "reason": "High volume"},
    {"type": "best",    "slug": "ai-tools-for-bloggers",      "priority": 2, "reason": "High volume"},
    {"type": "best",    "slug": "ai-tools-for-agencies",      "priority": 2, "reason": "B2B buyers"},
    {"type": "review",  "slug": "hubspot",                    "priority": 2, "reason": "High conversion"},
    {"type": "compare", "a": "chatgpt", "b": "claude",        "priority": 2, "reason": "High volume"},
    {"type": "review",  "slug": "frase",                      "priority": 3, "reason": "SEO niche"},
]

def sep(char="=", width=60):
    print(char * width)

def count_html_pages():
    counts = {}
    for section in ["review", "compare", "alternatives", "best", "blog", "category"]:
        path = os.path.join(HTML_DIR, section)
        if os.path.exists(path):
            # Count subdirectories with index.html
            pages = [d for d in os.listdir(path)
                     if os.path.isdir(os.path.join(path, d))
                     and os.path.exists(os.path.join(path, d, "index.html"))]
            counts[section] = len(pages)
        else:
            counts[section] = 0
    return counts

def get_social_stats():
    if not os.path.exists(SOCIAL_DB):
        return {}
    try:
        conn = sqlite3.connect(SOCIAL_DB)
        rows = conn.execute(
            "SELECT platform, COUNT(*) FROM posts WHERE success=1 GROUP BY platform"
        ).fetchall()
        conn.close()
        return dict(rows)
    except:
        try:
            conn = sqlite3.connect(SOCIAL_DB)
            rows = conn.execute(
                "SELECT platform, COUNT(*) FROM posts GROUP BY platform"
            ).fetchall()
            conn.close()
            return dict(rows)
        except:
            return {}

def get_recent_runs(days=7):
    if not os.path.exists(LOG_FILE):
        return []
    lines = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            for line in f:
                try:
                    ts_str = line[1:17]
                    ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
                    if ts >= cutoff:
                        lines.append(line.strip())
                except:
                    pass
    except:
        pass
    return lines

def check_credentials():
    env_keys = {
        "twitter":   ["TWITTER_API_KEY"],
        "reddit":    ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"],
        "pinterest": ["PINTEREST_ACCESS_TOKEN"],
        "linkedin":  ["LINKEDIN_ACCESS_TOKEN"],
        "instagram": ["INSTAGRAM_ACCESS_TOKEN"],
        "devto":     ["DEVTO_API_KEY"],
        "discord":   ["DISCORD_BOT_TOKEN"],
        "medium":    ["MEDIUM_ACCESS_TOKEN"],
        "hashnode":  ["HASHNODE_ACCESS_TOKEN"],
    }
    results = {}
    for platform, keys in env_keys.items():
        results[platform] = all(os.getenv(k) for k in keys)
    return results

def check_existing_pages():
    existing = set()
    for section in ["review", "compare", "alternatives", "best"]:
        path = os.path.join(HTML_DIR, section)
        if os.path.exists(path):
            for d in os.listdir(path):
                if os.path.isdir(os.path.join(path, d)):
                    existing.add(f"{section}/{d}")
    return existing

def revenue_potential(tool_slug):
    c = COMMISSION.get(tool_slug, {})
    if not c or not c.get("rate"):
        return 0
    return c["rate"] * c["avg_price"]

def print_weekly_report():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    week = datetime.datetime.now().isocalendar()[1]

    sep()
    print(f"  RANKERTOOLAI — WEEKLY OPERATIONS REPORT")
    print(f"  Week {week} — {today}")
    sep()

    # 1. Content stats
    print("\n[1] CONTENT STATS")
    sep("-")
    counts = count_html_pages()
    total = sum(counts.values())
    for section, count in counts.items():
        bar = "#" * min(count, 30)
        print(f"  {section:<14} {count:>3}  {bar}")
    print(f"  {'TOTAL':<14} {total:>3}")

    # 2. Social stats
    print("\n[2] SOCIAL POSTING STATS (all time)")
    sep("-")
    stats = get_social_stats()
    creds = check_credentials()
    platforms = ["twitter", "discord", "devto", "quora", "reddit",
                 "medium", "hashnode", "linkedin", "pinterest", "instagram"]
    for p in platforms:
        count = stats.get(p, 0)
        ok = creds.get(p, False)
        status = "ACTIVE" if ok else "NO CREDS"
        print(f"  {p:<12} {count:>4} posts  [{status}]")

    # 3. Recent social runs
    print("\n[3] SOCIAL RUNS — LAST 7 DAYS")
    sep("-")
    runs = get_recent_runs(7)
    if runs:
        for line in runs[-20:]:
            print(f"  {line}")
    else:
        print("  No recent runs found")

    # 4. Content gaps (priority list)
    print("\n[4] CONTENT GAPS — PRIORITY ORDER")
    sep("-")
    existing = check_existing_pages()
    missing = []
    for gap in CONTENT_GAPS:
        if gap["type"] == "compare":
            slug = f"compare/{gap['a']}-vs-{gap['b']}"
        elif gap["type"] == "alts":
            slug = f"alternatives/{gap['slug']}"
        elif gap["type"] == "best":
            slug = f"best/{gap['slug']}"
        else:
            slug = f"review/{gap['slug']}"

        if slug not in existing:
            missing.append((gap["priority"], slug, gap["reason"]))

    missing.sort(key=lambda x: x[0])
    for i, (prio, slug, reason) in enumerate(missing[:10], 1):
        print(f"  P{prio} [{i:>2}]  /{slug}/")
        print(f"         → {reason}")

    # 5. Revenue potential by tool
    print("\n[5] REVENUE PRIORITY (commission/sale)")
    sep("-")
    for tool, data in sorted(COMMISSION.items(),
                              key=lambda x: revenue_potential(x[0]),
                              reverse=True):
        if data["rate"]:
            monthly = data["rate"] * data["avg_price"]
            print(f"  {tool:<15} ${monthly:>6.2f}/sale  ({int(data['rate']*100)}% {data['type']})")

    # 6. Google Ads status
    print("\n[6] GOOGLE ADS STATUS")
    sep("-")
    config_path = os.path.join(ROOT, "google_ads", "data", "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
        ads_id = cfg.get("google_ads_id", "NOT SET")
        ga4_id = cfg.get("ga4_id", "NOT SET")
        print(f"  GA4 ID:       {ga4_id}")
        print(f"  Google Ads:   {ads_id}")
        if "AW-XXXXXXXXXX" in str(ads_id) or not ads_id or ads_id == "NOT SET":
            print("  STATUS:       ❌ Cần điền Google Ads ID vào config.json")
        else:
            print("  STATUS:       ✅ Config sẵn sàng")
    else:
        print("  config.json không tìm thấy")

    # 7. Action items
    print("\n[7] ACTION ITEMS TUẦN NÀY")
    sep("-")
    actions = []

    # Check missing credentials
    for p, ok in creds.items():
        if not ok and p in ["reddit", "linkedin", "pinterest"]:
            actions.append(f"  ❌ Kích hoạt {p} (thiếu credentials)")

    # Check content velocity
    if total < 120:
        actions.append(f"  📝 Content: tạo thêm {120-total} trang để đạt 120")

    # Always suggest top content gap
    if missing:
        top = missing[0]
        actions.append(f"  📝 Tạo ngay: /{top[1]}/ ({top[2]})")

    if not actions:
        actions.append("  ✅ Tất cả đang tốt — tập trung scale!")

    for a in actions:
        print(a)

    print()
    sep()
    print("  COMMANDS:")
    print("  python weekly_ops.py --plan   → Content plan tuần tới")
    print("  python social_agent/run_all.py --status  → Social status")
    print("  python google_ads/monitoring/budget_tracker.py --status")
    sep()

def print_content_plan(n=10):
    print("\n[CONTENT PLAN] Trang cần tạo — theo thứ tự doanh thu")
    sep()
    existing = check_existing_pages()

    pipeline_cmds = []
    rank = 1
    for gap in CONTENT_GAPS:
        if gap["type"] == "compare":
            slug = f"compare/{gap['a']}-vs-{gap['b']}"
            cmd = f"/compare {gap['a']} {gap['b']}"
        elif gap["type"] == "alts":
            slug = f"alternatives/{gap['slug']}"
            cmd = f"/alternatives {gap['slug']}"
        elif gap["type"] == "best":
            slug = f"best/{gap['slug']}"
            cmd = f"/best {gap['slug'].replace('-', ' ')}"
        else:
            slug = f"review/{gap['slug']}"
            cmd = f"/review {gap['slug']}"

        if slug not in existing:
            p = gap["priority"]
            print(f"  #{rank:<2}  P{p}  /{slug}/")
            print(f"       Revenue: {gap['reason']}")
            print(f"       Lệnh:   {cmd}")
            print()
            pipeline_cmds.append(cmd)
            rank += 1
            if rank > n:
                break

    print(f"\nCopy các lệnh này vào Claude với PIPELINE.md:")
    sep("-")
    for cmd in pipeline_cmds[:5]:
        print(f"  {cmd}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()

    if args.plan:
        print_content_plan(10)
    else:
        print_weekly_report()

if __name__ == "__main__":
    main()
