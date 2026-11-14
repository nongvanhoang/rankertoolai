"""Bing section of the Monday Telegram report.

Reads Bing Webmaster stats for both sites (key in C:/Users/Admin/RankerToolAI/.env, via
RankerToolAI/bing_report.py) and writes social_posts/_bao_cao_<today>/tg/02_bing.html, which
daily/send_reports.js then delivers. Run after reels_report.py and before send_reports.js.

Usage: python reel_tools/bing_weekly.py [--dry-run]
"""
import datetime as dt
import html
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RTA = Path("C:/Users/Admin/RankerToolAI")
sys.path.insert(0, str(RTA))
import bing_report as br  # noqa: E402

MIN_IMPR_FIX = 30     # 28-day impressions before a low-CTR page is worth fixing
LOW_CTR = 2.0         # % CTR under which a page "shows but nobody clicks"


def esc(s):
    return html.escape(str(s), quote=False)


def short(url):
    return url.split("//", 1)[-1].split("/", 1)[-1].rstrip("/") or "(trang chủ)"


def site_block(site, key, today):
    name = site.split("//")[1].strip("/")
    raw_pages = br.call("GetPageStats", site, key)
    raw_q = br.call("GetQueryStats", site, key)
    # Page/query stats come back as one rolling aggregate (single date stamp), so no date filter.
    p28 = br.summarise(raw_pages, "Query", dt.date.min)
    q28 = br.summarise(raw_q, "Query", dt.date.min)
    daily = sorted((br.when(r), r.get("Clicks", 0), r.get("Impressions", 0))
                   for r in br.call("GetRankAndTrafficStats", site, key) if br.when(r))
    out = [f"\n<b>{esc(name)}</b>"]
    if daily:
        last, prev = daily[-7:], daily[-14:-7]
        line = (f"{last[0][0]:%d/%m}–{last[-1][0]:%d/%m}: {sum(d[1] for d in last)} lượt bấm · "
                f"{sum(d[2] for d in last)} lượt hiện")
        if len(prev) == 7:
            line += f"  (7 ngày trước đó: {sum(d[1] for d in prev)} bấm · {sum(d[2] for d in prev)} hiện)"
        out.append(line)
    fix = [r for r in p28 if r[2] >= MIN_IMPR_FIX and r[3] < LOW_CTR][:3]
    if fix:
        out.append("🔧 <b>Hiện nhiều, ít người bấm</b> (nên sửa tiêu đề/mô tả):")
        out += [f"• /{esc(short(r[0]))}: {r[2]} hiện · {r[1]} bấm · hạng {r[4]}" for r in fix]
    near = [r for r in p28 if 4 <= r[4] <= 10 and r[2] >= 20 and r not in fix][:3]
    if near:
        out.append("📈 <b>Sắp vào top 3</b> (thêm link nội bộ, cập nhật nội dung):")
        out += [f"• /{esc(short(r[0]))}: hạng {r[4]} · {r[2]} hiện · {r[1]} bấm" for r in near]
    if q28:
        out.append("🔎 Từ khóa nhiều nhất: " + ", ".join(f"{esc(r[0])} ({r[2]})" for r in q28[:5]))
    if not p28:
        out.append("Bing chưa có số liệu trang.")
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    today = dt.date.today()
    key = br.api_key()
    lines = [f"<b>🔍 Bing · tuần đến {today}</b>",
             "<i>Bing (và ChatGPT, vốn tìm qua Bing) là nguồn khách miễn phí chính. "
             "Số liệu Bing trễ vài ngày; bảng trang/từ khóa là tổng gần đây do Bing gộp sẵn.</i>"]
    for site in br.SITES:
        try:
            lines += site_block(site, key, today)
        except Exception as e:  # noqa: BLE001
            lines.append(f"\n⚠️ {esc(site)}: lỗi lấy số liệu Bing ({esc(e)})")
    msg = "\n".join(lines)[:3900]
    print(msg)
    if "--dry-run" in sys.argv:
        return
    out = HERE / "social_posts" / f"_bao_cao_{today}" / "tg"
    out.mkdir(parents=True, exist_ok=True)
    (out / "02_bing.html").write_text(msg, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
