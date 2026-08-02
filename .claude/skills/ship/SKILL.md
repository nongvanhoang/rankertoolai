---
name: ship
description: Runs RankerToolAI's full content pipeline (keyword → brief → affiliate → write → seo → linking → qa → deploy) for a page via rankertoolai-orchestrator. Use when the user wants a new review/comparison/alternatives page created and shipped, or an existing page pushed through the remaining pipeline stages.
argument-hint: "[what to create/ship, e.g. \"review of Jasper\" or \"jasper-vs-writesonic comparison\"]"
---

Dispatch the `rankertoolai-orchestrator` subagent (Agent tool, `subagent_type: "rankertoolai-orchestrator"`) with this goal: **$ARGUMENTS**

If no argument was given, ask the user what page/tool they want shipped before dispatching — don't guess.

This only works when the session's cwd is `C:\Users\Admin\RankerToolAI` (subagents load per-repo). If `rankertoolai-orchestrator` doesn't appear as an available agent type, tell the user to reopen the session at that path.
