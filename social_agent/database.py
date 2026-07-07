import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "posts.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            tool_slug TEXT NOT NULL,
            content_type TEXT,
            post_id TEXT,
            url TEXT,
            status TEXT DEFAULT 'success',
            error TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Track which content variation was last used per tool+platform
    c.execute("""
        CREATE TABLE IF NOT EXISTS content_rotation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            tool_slug TEXT NOT NULL,
            variation TEXT NOT NULL,
            used_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(platform, tool_slug, variation)
        )
    """)
    conn.commit()
    conn.close()


def get_next_variation(platform: str, tool_slug: str, variations: list) -> str:
    """Return the least-recently-used variation for this platform+tool pair."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    used = {}
    for v in variations:
        c.execute(
            "SELECT used_at FROM content_rotation WHERE platform=? AND tool_slug=? AND variation=?",
            (platform, tool_slug, v)
        )
        row = c.fetchone()
        used[v] = row[0] if row else ""
    conn.close()
    return min(used, key=used.get)


def mark_variation_used(platform: str, tool_slug: str, variation: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO content_rotation (platform, tool_slug, variation, used_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(platform, tool_slug, variation) DO UPDATE SET used_at=CURRENT_TIMESTAMP
    """, (platform, tool_slug, variation))
    conn.commit()
    conn.close()

def log_post(platform, tool_slug, content_type=None, post_id=None, url=None, status="success", error=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (platform, tool_slug, content_type, post_id, url, status, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (platform, tool_slug, content_type, post_id, url, status, error))
    conn.commit()
    conn.close()

def already_posted(platform, tool_slug, days=7):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM posts
        WHERE platform=? AND tool_slug=? AND status='success'
        AND created_at >= datetime('now', ?)
    """, (platform, tool_slug, f"-{days} days"))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def has_recent_error(platform, tool_slug, hours=24):
    """Returns True if this platform+tool had an error within the last X hours."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM posts
        WHERE platform=? AND tool_slug=? AND status='error'
        AND created_at >= datetime('now', ?)
    """, (platform, tool_slug, f"-{hours} hours"))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_least_posted_tool(tool_slugs, platform=None):
    """Pick the tool with fewest successful posts. Tools with recent errors get a +100 penalty to avoid retry loops."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    counts = {}
    for slug in tool_slugs:
        if platform and platform != "all_platforms":
            c.execute(
                "SELECT COUNT(*) FROM posts WHERE platform=? AND tool_slug=? AND status='success'",
                (platform, slug)
            )
        else:
            c.execute(
                "SELECT COUNT(*) FROM posts WHERE tool_slug=? AND status='success'",
                (slug,)
            )
        base = c.fetchone()[0]
        # Penalise tools that errored in the last 24h so they're not picked again immediately
        if platform and platform != "all_platforms":
            c.execute(
                "SELECT COUNT(*) FROM posts WHERE platform=? AND tool_slug=? AND status='error' AND created_at >= datetime('now', '-24 hours')",
                (platform, slug)
            )
        else:
            c.execute(
                "SELECT COUNT(*) FROM posts WHERE tool_slug=? AND status='error' AND created_at >= datetime('now', '-24 hours')",
                (slug,)
            )
        recent_errors = c.fetchone()[0]
        counts[slug] = base + (100 if recent_errors > 0 else 0)
    conn.close()
    return min(counts, key=counts.get)

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT platform, COUNT(*) as total, SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as success
        FROM posts GROUP BY platform ORDER BY total DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows
