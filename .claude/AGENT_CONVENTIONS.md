# RankerToolAI — Shared Agent Conventions

Rules referenced by more than one agent in `.claude/agents/`. Written once here so a policy change (e.g. a new affiliate-link rule) only needs updating in one place instead of N near-duplicate copies. Agent-specific specs (page structure, word count, schema type, scoring weights) stay in each agent's own file — only what's genuinely identical across agents lives here.

---

## Affiliate links

- Every affiliate link uses the `/go/[tool-slug]/` redirect — **never** a direct/raw affiliate URL anywhere in page content.
- Every affiliate `<a>` tag includes `rel="nofollow sponsored" target="_blank"`.
- Vary CTA text across placements on the same page (don't repeat the exact same button label 3+ times).

## Disclosure (required near the top of every page with affiliate links)

```html
<p class="disclosure">
  <em>Disclosure: This page contains affiliate links. We may earn a commission if you purchase through our links, at no extra cost to you. <a href="/affiliate-disclosure/">Read our affiliate disclosure →</a></em>
</p>
```

## Never fabricate

- Never invent pricing — write "pricing not available" and link to the tool's own pricing page instead of guessing.
- Never claim a tool does something it doesn't do.
- Never output placeholder text (`[INSERT...]`, `TODO`, etc.) in a finished page.
- Never add a self-serving `aggregateRating` built from our own single editorial score — that's a Google structured-data violation (risks rich-result eligibility site-wide). Our own score belongs in `Review.reviewRating` only. A **real** third-party `aggregateRating` (Trustpilot/G2, fetched via `fetch_external_reviews.py`) is fine and encouraged when available.

## Schema — shared shape

Every content page's `@graph` includes a `BreadcrumbList` following this pattern (swap the middle item's name/URL for the page's section):

```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://rankertoolai.com/"},
    {"@type": "ListItem", "position": 2, "name": "[Section]", "item": "https://rankertoolai.com/[section]/"},
    {"@type": "ListItem", "position": 3, "name": "[Page Title]"}
  ]
}
```

Plus a `FAQPage` node (5 questions minimum, each agent's own file lists the required question *topics* for its page type) — mainEntity question count must match the visible FAQ section exactly.

## Voice

First-person reviewer perspective, authoritative but accessible, no fluff. Prohibited: "In this review we will explore...", "Without further ado...", "In conclusion...", AI clichés ("dive deep", "in the realm of", "cutting-edge").

## Handoff

Every writer agent's output metadata block includes `"recommended_next_agent": "rankertoolai-seo"` — the standard next pipeline stage is SEO, then internal-linking, then QA (see `rankertoolai-orchestrator`'s pipeline diagram for the full order).

## Domain

`https://rankertoolai.com` — every agent's WEBSITE section repeating this is intentional (keeps each file self-contained enough to read alone), not an error.
