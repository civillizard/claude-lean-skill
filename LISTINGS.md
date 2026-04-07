# Directory Listings & Distribution

Tracking all public listings, submissions, and distribution channels for the `/lean` skill.

## Active Listings

### hesreallyhim / awesome-claude-code
- **URL:** https://github.com/hesreallyhim/awesome-claude-code/issues/1323
- **Status:** OPEN — validation-passed, awaiting maintainer review
- **Submitted:** 2026-04-03 (resubmission of #1091, closed 2026-03-24 for 7-day cooldown)
- **Method:** Issue form (web UI only — CLI/PR submissions risk ban)
- **Labels:** validation-passed, resource-submission
- **Notes:** All validation checks passed. Maintainer asked to resubmit after cooldown. Use web UI form only.

### Anthropic Plugin Directory
- **URL:** https://platform.claude.com/plugins/submissions (track status here)
- **Status:** SUBMITTED — pending review
- **Submitted:** 2026-03-30
- **Method:** Web form at `platform.claude.com/plugins/submit`
- **Portal:** Submit: `/plugins/submit` | Track: `/plugins/submissions` (only visible after submitting)
- **Details submitted:** Name: lean, Platform: Claude Code, License: MIT
- **Notes:** No confirmation email sent. Status trackable only via the submissions page. Review timeline unknown.

### SkillHub (skillhub.club)
- **Status:** NOT INDEXED (as of 2026-04-07, waiting for auto-discovery)
- **How it works:** Auto-indexes GitHub repos with `SKILL.md` files — no manual submission needed
- **SKILL.md location:** `skills/lean/SKILL.md` is correct (matches Anthropic's own repo pattern at `anthropics/skills`)
- **CLI:** Broken (v0.1.2, malformed OAuth URL). Not needed — auto-indexing is the standard path.
- **Platform:** Legitimate (36K+ skills, Anthropic's own 17 skills listed, desktop app with 494 GitHub stars)

### Anthropic Skills Repo (anthropics/skills)
- **Status:** NOT SUBMITTED
- **Method:** PR to official repo — more formal, gives Anthropic endorsement
- **Notes:** Would be the highest-value listing if accepted

## Closed Listings

### ComposioHQ / awesome-claude-skills
- **URL:** https://github.com/ComposioHQ/awesome-claude-skills/pull/481
- **Status:** CLOSED (not merged)
- **Submitted:** 2026-03-24 | **Closed:** before 2026-04-07
- **Notes:** Repo renamed from `awesome-claude-code` to `awesome-claude-skills`. PR closed without merge.

### travisvn / awesome-claude-skills
- **URL:** https://github.com/travisvn/awesome-claude-skills/pull/457
- **Status:** CLOSED (not merged)
- **Submitted:** 2026-03-30 | **Closed:** before 2026-04-07
- **Notes:** 216 open PRs at time of submission. Closed without merge.

---

## MacOS Full Disk Access Tunnel — Directory Listings

### iCHAIT / awesome-macOS
- **URL:** https://github.com/iCHAIT/awesome-macOS/pull/772
- **Status:** REJECTED — closed by maintainer (herrbischoff) on 2026-04-07
- **Submitted:** 2026-04-03
- **Rejection reasons:** New repo with no stars; perceived as "circumventing security"; AI integration section flagged; didn't follow PR template (checklist items, alphabetical order, icon badges)
- **Maintainer:** Marcel Bischoff (marcel@herrbischoff.com, @herrbischoff)
- **Notes:** Hostile tone ("Don't submit this again"). Consider improving README framing before any future engagement. Do NOT resubmit.

### BlackSquirrelz / awesome-apple-security
- **URL:** https://github.com/BlackSquirrelz/awesome-apple-security/pull/2
- **Status:** OPEN — awaiting review
- **Submitted:** 2026-04-03
- **Notes:** Security-focused audience, more likely to understand FDA's legitimate use case

---

## Distribution Channels (lean-skill)

### GitHub Repository
- **URL:** https://github.com/civillizard/claude-lean-skill
- **Visibility:** Public
- **Stats (2026-04-07):** 0 stars, 0 forks, 114 clones (76 unique), 25 views (17 unique) in last 14 days
- **Referrers:** github.com, Google, Bing

### YouTube
- **Short:** https://youtube.com/shorts/FdOQP8GZVrs (shared 2026-03-26)

## Submission Best Practices (Reference)

From research on 2026-03-30:

1. `SKILL.md` is THE standard — YAML frontmatter (`name`, `description`) required
2. Description must say WHAT it does AND WHEN to use it (Claude uses this for auto-discovery)
3. Keep SKILL.md body under 500 lines
4. Test with Haiku, Sonnet, and Opus (behavior differs)
5. Include LICENSE
6. Reference files should be one level deep from SKILL.md
7. For SkillHub: repos with SKILL.md auto-index; can also use `npx @skill-hub/cli publish`
