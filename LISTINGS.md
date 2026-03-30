# Directory Listings & Distribution

Tracking all public listings, submissions, and distribution channels for the `/lean` skill.

## Active Listings

### ComposioHQ / awesome-claude-skills
- **URL:** https://github.com/ComposioHQ/awesome-claude-skills/pull/481
- **Status:** OPEN, mergeable, awaiting maintainer review
- **Submitted:** 2026-03-24
- **Method:** PR from fork (`civillizard/awesome-claude-skills`, branch `add-lean-skill`)
- **Category:** Development & Code Tools (alphabetical, between LangSmith Fetch and MCP Builder)
- **Notes:** Repo was originally `awesome-claude-code`, renamed to `awesome-claude-skills`. PR survived the rename.

### hesreallyhim / awesome-claude-code
- **URL:** https://github.com/hesreallyhim/awesome-claude-code/issues/1091
- **Status:** CLOSED — 7-day cooldown applied (repo was <1 week old at submission)
- **Submitted:** 2026-03-24
- **Resubmit after:** 2026-03-31
- **Method:** Issue form (web UI only — CLI/PR submissions risk ban)
- **Labels:** validation-passed, resource-submission
- **Notes:** All validation checks passed. Maintainer asked to resubmit after cooldown. Use web UI form only.

### travisvn / awesome-claude-code
- **Status:** NOT YET SUBMITTED
- **Method:** Web UI issue form only (strict policy — ban risk for PR/CLI submissions)
- **Requirements:** Quality README, OSS license, evidence-based claims, unique (no duplicates)
- **Notes:** CONTRIBUTING.md warns against any submission method other than their web form template

### Anthropic Plugin Directory
- **Status:** Submitted for review (no confirmation email received)
- **Submitted:** ~2026-03-24 (via Anthropic website)
- **Method:** Web form on anthropic.com
- **Notes:** No email confirmation or status tracking mechanism found. Gmail search (API) returned only billing emails from Anthropic.

### SkillHub (skillhub.club)
- **Status:** NOT INDEXED (as of 2026-03-30, waiting for auto-discovery)
- **How it works:** Auto-indexes GitHub repos with `SKILL.md` files — no manual submission needed
- **SKILL.md location:** `skills/lean/SKILL.md` is correct (matches Anthropic's own repo pattern at `anthropics/skills`)
- **CLI:** Broken (v0.1.2, malformed OAuth URL — concatenates domain twice). Not needed — auto-indexing is the standard path.
- **Platform:** Legitimate (36K+ skills, Anthropic's own 17 skills listed, desktop app with 494 GitHub stars)
- **Next check:** If not indexed by 2026-04-01, file issue on `skillhub-club/cli` repo

## Distribution Channels

### GitHub Repository
- **URL:** https://github.com/civillizard/claude-lean-skill
- **Visibility:** Public
- **Stats (as of 2026-03-30):** 0 stars, 0 forks, 22 clones (21 unique) in last 14 days, 4 unique page views

### YouTube
- **Short:** https://youtube.com/shorts/FdOQP8GZVrs (shared 2026-03-26)

### Anthropic Skills Repo (anthropics/skills)
- **Status:** NOT SUBMITTED
- **Method:** PR to official repo — more formal, gives Anthropic endorsement
- **Notes:** Would be the highest-value listing if accepted

## Submission Best Practices (Reference)

From research on 2026-03-30:

1. `SKILL.md` is THE standard — YAML frontmatter (`name`, `description`) required
2. Description must say WHAT it does AND WHEN to use it (Claude uses this for auto-discovery)
3. Keep SKILL.md body under 500 lines
4. Test with Haiku, Sonnet, and Opus (behavior differs)
5. Include LICENSE
6. Reference files should be one level deep from SKILL.md
7. For SkillHub: repos with SKILL.md auto-index; can also use `npx @skill-hub/cli publish`
