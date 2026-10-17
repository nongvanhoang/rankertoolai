-- One row per card (one video for one brand on one day).
CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,          -- e.g. 20261018rn1
  site TEXT NOT NULL,           -- rn | rta
  date TEXT NOT NULL,           -- YYYY-MM-DD (Vietnam time)
  title TEXT NOT NULL,
  reel TEXT NOT NULL,           -- video file name without .mp4 (used for duplicate checks)
  channels TEXT NOT NULL,       -- JSON array of channel keys
  chat_id INTEGER NOT NULL,
  thread_id INTEGER,
  card_msg INTEGER NOT NULL,    -- Telegram message id of the card
  card_is_caption INTEGER DEFAULT 0,
  kit TEXT,                     -- JSON {channel: {caption, comment}} (Telegram HTML)
  skipped INTEGER DEFAULT 0,
  created TEXT
);
CREATE INDEX IF NOT EXISTS items_date ON items (date, site);
CREATE INDEX IF NOT EXISTS items_reel ON items (reel);

-- One row per channel marked as posted.
CREATE TABLE IF NOT EXISTS marks (
  item_id TEXT NOT NULL,
  ch TEXT NOT NULL,
  at TEXT NOT NULL,
  PRIMARY KEY (item_id, ch)
);
