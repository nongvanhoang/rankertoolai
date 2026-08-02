# RankerToolAI Agent Quick Reference

**Fastest path — 2 slash commands exist:** `/ship [what to create]` and `/health-check`. Both just dispatch the orchestrator/monitor for you; no agent names to remember.

Otherwise, you almost never need to name a specific agent — just tell `rankertoolai-orchestrator` what you want in plain language and it dispatches the right one(s). This table exists for when you want to skip straight to a specialist, or want to know what exists before asking for something new.

| Say this | Gets you |
|---|---|
| "Create a review of [tool]" | Full pipeline: keyword → brief → affiliate → **review** → seo → linking → qa → deploy |
| "Compare [tool A] vs [tool B]" | Same pipeline, **comparison** writer instead of review |
| "Best alternatives to [tool]" | Same pipeline, **alternatives** writer instead of review |
| "Find new AI tools to cover" | `rankertoolai-scout` |
| "Is [keyword] worth targeting?" | `rankertoolai-keyword` |
| "What's [tool]'s affiliate link / is it still active?" | `rankertoolai-affiliate` |
| "Fix the meta tags/schema on [page]" | `rankertoolai-seo` |
| "Add internal links to [page]" | `rankertoolai-internal-linking` |
| "Check if [page] is ready to ship" | `rankertoolai-qa` |
| "Deploy" / "Ship [page]" | `rankertoolai-deploy` |
| "Is the site healthy?" / "Any broken links?" | `rankertoolai-monitor` |
| "Why is ad spend leaking / check Google Ads compliance" | `rankertoolai-ads` |
| "Is tracking actually working?" | `rankertoolai-analytics` |
| "What's missing on the site technically?" (schema, sitemap, redirects — not a page's content) | `rankertoolai-website-completion` |
| "Audit the whole site strategy" | `rankertoolai-architect` |
| "What's the pipeline status?" | `rankertoolai-orchestrator` directly |

Shared rules all content-writing agents follow (disclosure block, `/go/` link format, no-fabrication policy, schema shape): `.claude/AGENT_CONVENTIONS.md`.

**Reminder:** these only show up as dispatchable agents when your session's working directory is this repo root (`C:\Users\Admin\RankerToolAI`) — a session opened elsewhere won't see them.

**Known open issue (2026-08-01):** `html/` (the real deploy folder) is ~9 days behind the root-level page files — see `rankertoolai-monitor.md`'s Category 0b before assuming a page you just edited is actually live.
