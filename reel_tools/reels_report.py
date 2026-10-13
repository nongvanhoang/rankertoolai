"""
Weekly reels report: which channel, video and hook (A/B/C) sent visitors and affiliate clicks.

Reads GA4 for both sites (service account in RankerToolAI/ga4_service_account.json; it must be
a Viewer on each property). Only traffic tagged by the posting kits counts:
utm_campaign=reel_video, utm_content=reel-<slug>[-hb|-hc], utm_source=<channel>.

Writes social_posts/_bao_cao_<date>/ (tg/01_report.html + BAO_CAO.md). With --push it commits and
pushes that folder on this branch, and the "Send posting kit to Telegram" workflow delivers it.

Usage: python reel_tools/reels_report.py [--days 7] [--push]
"""
import argparse
import html
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent.parent
KEY = Path(r"C:\Users\Admin\RankerToolAI\ga4_service_account.json")
SITES = {"RankerToolAI": "542190396", "RankerNest": "548066278"}
VID = re.compile(r"^reel-(?P<slug>.+?)(?:-h(?P<hook>[a-z]))?$")


def query(svc, prop, days, event=None):
    # synthesia_reel = the Synthesia v3 links posted before the kits existed
    filt = [{"filter": {"fieldName": "sessionCampaignName", "inListFilter": {"values": ["reel_video", "synthesia_reel"]}}}]
    if event:
        filt.append({"filter": {"fieldName": "eventName", "stringFilter": {"value": event}}})
    body = {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "yesterday"}],
        "dimensions": [{"name": "sessionManualAdContent"}, {"name": "sessionSource"}, {"name": "sessionCampaignName"}],
        "metrics": [{"name": "eventCount" if event else "sessions"}],
        "dimensionFilter": {"andGroup": {"expressions": filt}},
        "limit": 10000,
    }
    r = svc.properties().runReport(property=f"properties/{prop}", body=body).execute()
    out = []
    for x in r.get("rows", []):
        content, source, campaign = (d["value"] for d in x["dimensionValues"])
        if content == "(not set)" and campaign == "synthesia_reel":
            content = "reel-synthesia"  # v3 links had no utm_content; count them as Synthesia hook A
        out.append((content, source, float(x["metricValues"][0]["value"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=["https://www.googleapis.com/auth/analytics.readonly"])
    svc = build("analyticsdata", "v1beta", credentials=creds, cache_discovery=False)
    blank = lambda: {"s": 0.0, "c": 0.0}
    by_ch, by_vid, by_hook = defaultdict(blank), defaultdict(blank), defaultdict(lambda: defaultdict(blank))
    notes = []
    for site, prop in SITES.items():
        try:
            visits, clicks = query(svc, prop, a.days), query(svc, prop, a.days, "affiliate_click")
        except Exception as e:  # usually: service account not yet a Viewer on this property
            notes.append(f"{site}: chưa đọc được GA4 ({'chưa cấp quyền' if '403' in str(e) else str(e)[:80]})")
            continue
        for rows, k in ((visits, "s"), (clicks, "c")):
            for content, source, n in rows:
                by_ch[source][k] += n
                by_vid[content][k] += n
                m = VID.match(content)
                if m:
                    by_hook[m["slug"]][(m["hook"] or "a").upper()][k] += n

    day = date.today().isoformat()
    esc = html.escape
    rank = lambda d: sorted(d.items(), key=lambda kv: (-kv[1]["c"], -kv[1]["s"]))
    lines = [f"<b>📊 Báo cáo Reels · {a.days} ngày đến {day}</b>",
             "<i>Lượt vào = người bấm link từ video; Click = bấm sang trang bán (affiliate).</i>"]
    if not by_vid:
        lines.append("\nChưa có lượt vào nào từ link của video. Bình thường nếu mới bắt đầu đăng.")
    else:
        lines.append("\n<b>Theo kênh</b>")
        lines += [f"• {esc(k)}: {v['s']:.0f} lượt vào · {v['c']:.0f} click" for k, v in rank(by_ch)]
        lines.append("\n<b>Kiểu mở đầu (A/B/C) theo sản phẩm</b>")
        for slug, hooks in sorted(by_hook.items()):
            parts = " · ".join(f"{h}: {v['s']:.0f}/{v['c']:.0f}" for h, v in sorted(hooks.items()))
            best = max(hooks.items(), key=lambda kv: (kv[1]["c"], kv[1]["s"]))[0] if len(hooks) > 1 else ""
            lines.append(f"• {esc(slug)} → {parts}" + (f"  👑 {best}" if best else ""))
        lines.append("<i>(số đầu = lượt vào, số sau = click)</i>")
        lines.append("\n<b>Top 5 video</b>")
        lines += [f"• {esc(k)}: {v['s']:.0f} lượt vào · {v['c']:.0f} click" for k, v in rank(by_vid)[:5]]
        dead = [k for k, v in by_vid.items() if v["s"] == 0]
        if dead:
            lines.append("\nKhông ai vào: " + ", ".join(esc(x) for x in dead))
    if notes:
        lines.append("\n⚠️ " + "\n⚠️ ".join(esc(n) for n in notes))
    msg = "\n".join(lines)[:3900]

    out = HERE / "social_posts" / f"_bao_cao_{day}"
    (out / "tg").mkdir(parents=True, exist_ok=True)
    (out / "tg" / "01_report.html").write_text(msg, encoding="utf-8", newline="\n")
    (out / "BAO_CAO.md").write_text(re.sub(r"</?[bi]>", "", msg), encoding="utf-8", newline="\n")
    print(re.sub(r"</?[bi]>", "", msg))
    if a.push:
        rel = out.relative_to(HERE).as_posix()
        subprocess.run(["git", "-C", str(HERE), "pull", "-q", "--rebase", "origin", "video-test-synthesia"], check=False)
        subprocess.run(["git", "-C", str(HERE), "add", rel], check=True)
        subprocess.run(["git", "-C", str(HERE), "commit", "-q", "-m", f"Weekly reels report {day}"], check=False)
        subprocess.run(["git", "-C", str(HERE), "push", "-q", "origin", "video-test-synthesia"], check=True)


if __name__ == "__main__":
    main()
