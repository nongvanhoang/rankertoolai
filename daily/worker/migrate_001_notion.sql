
-- 2026-10-17: slim cards linked to the Notion row
ALTER TABLE items ADD COLUMN notion_page TEXT;
ALTER TABLE items ADD COLUMN notion_url TEXT;
