---
name: health-check
description: Runs a full RankerToolAI site health check via rankertoolai-monitor (uptime, /go/ link integrity, deploy freshness, SSL, sitemap, and the known root-vs-html/ drift check). Use when the user asks "is everything OK", wants a status check, or after any deploy.
---

Dispatch the `rankertoolai-monitor` subagent (Agent tool, `subagent_type: "rankertoolai-monitor"`) with this prompt: "Run a full health check — all monitoring categories including Category 0 (deploy freshness, both 0a Cloudflare-vs-html/ and 0b root-vs-html/ drift). Report status per category and flag anything needing action."

Summarize the result for the user; if it flags the html/ drift or any other action item, ask whether they want it routed to the relevant agent (e.g. `rankertoolai-deploy`) or left for them to decide manually.

This only works when the session's cwd is `C:\Users\Admin\RankerToolAI` — if `rankertoolai-monitor` isn't an available agent type, tell the user to reopen the session at that path.
