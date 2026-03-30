#!/bin/bash
# check-listings.sh — Monitor lean skill directory listing statuses
# Runs daily via launchd. Emails mao@6ra3.com only on status changes.

set -euo pipefail

STATE_FILE="$HOME/.local/state/lean-listings.state"
EMAIL="mao@6ra3.com"
SUBJECT="[lean skill] Listing status change"

mkdir -p "$(dirname "$STATE_FILE")"

# Collect current statuses
declare -A STATUS

# 1. ComposioHQ PR #481
composio_state=$(gh pr view 481 --repo ComposioHQ/awesome-claude-skills --json state -q .state 2>/dev/null || echo "ERROR")
STATUS[composio]="$composio_state"

# 2. travisvn PR #457
travisvn_state=$(gh pr view 457 --repo travisvn/awesome-claude-skills --json state -q .state 2>/dev/null || echo "ERROR")
STATUS[travisvn]="$travisvn_state"

# 3. hesreallyhim issue #1091
hesreallyhim_state=$(gh issue view 1091 --repo hesreallyhim/awesome-claude-code --json state -q .state 2>/dev/null || echo "ERROR")
STATUS[hesreallyhim]="$hesreallyhim_state"

# 4. SkillHub — check if indexed
skillhub_check=$(curl -s "https://www.skillhub.club/skills?search=lean" 2>/dev/null | grep -oi "civillizard\|claude-lean-skill" | head -1 || true)
if [ -n "$skillhub_check" ]; then
    STATUS[skillhub]="INDEXED"
else
    STATUS[skillhub]="NOT_INDEXED"
fi

# 5. Anthropic — can't check programmatically (needs browser auth)
#    Placeholder: check if "lean" appears in the public marketplace
anthropic_check=$(curl -s "https://claude.com/plugins" 2>/dev/null | grep -oi '"lean"' | head -1 || true)
if [ -n "$anthropic_check" ]; then
    STATUS[anthropic]="LISTED"
else
    STATUS[anthropic]="PENDING"
fi

# 6. Functional check — repo accessible, SKILL.md exists, install path works
HEALTH_ISSUES=""
# Check repo is public and accessible
repo_check=$(curl -s -o /dev/null -w "%{http_code}" "https://github.com/civillizard/claude-lean-skill" 2>/dev/null || echo "000")
if [ "$repo_check" != "200" ]; then
    HEALTH_ISSUES+="  - GitHub repo returned HTTP $repo_check (not 200)\n"
fi
# Check SKILL.md is fetchable
skill_check=$(curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/civillizard/claude-lean-skill/main/skills/lean/SKILL.md" 2>/dev/null || echo "000")
if [ "$skill_check" != "200" ]; then
    HEALTH_ISSUES+="  - SKILL.md returned HTTP $skill_check (not 200)\n"
fi
# Check hook script is fetchable
hook_check=$(curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/civillizard/claude-lean-skill/main/hooks/task-model-guard.py" 2>/dev/null || echo "000")
if [ "$hook_check" != "200" ]; then
    HEALTH_ISSUES+="  - task-model-guard.py returned HTTP $hook_check (not 200)\n"
fi
# Check marketplace.json is valid JSON
manifest_check=$(curl -s "https://raw.githubusercontent.com/civillizard/claude-lean-skill/main/.claude-plugin/marketplace.json" 2>/dev/null | python3 -c "import json,sys; json.load(sys.stdin); print('OK')" 2>/dev/null || echo "INVALID")
if [ "$manifest_check" != "OK" ]; then
    HEALTH_ISSUES+="  - marketplace.json is missing or invalid JSON\n"
fi

if [ -n "$HEALTH_ISSUES" ]; then
    STATUS[health]="BROKEN"
else
    STATUS[health]="OK"
fi

# Build current state string
CURRENT=""
for key in anthropic composio travisvn hesreallyhim skillhub health; do
    CURRENT+="${key}=${STATUS[$key]}"$'\n'
done

# Compare with previous state
CHANGED=false
if [ -f "$STATE_FILE" ]; then
    PREVIOUS=$(cat "$STATE_FILE")
    if [ "$CURRENT" != "$PREVIOUS" ]; then
        CHANGED=true
    fi
else
    # First run — save state, send initial report
    CHANGED=true
fi

# Save current state
echo -n "$CURRENT" > "$STATE_FILE"

# Build report
REPORT="Lean Skill Listing Status — $(date '+%Y-%m-%d %H:%M AST')

Directory             Status
─────────────────     ──────────────────
Anthropic Directory   ${STATUS[anthropic]}
ComposioHQ PR #481    ${STATUS[composio]}
travisvn PR #457      ${STATUS[travisvn]}
hesreallyhim #1091    ${STATUS[hesreallyhim]}
SkillHub              ${STATUS[skillhub]}

Plugin health       ${STATUS[health]}

Track Anthropic manually: https://platform.claude.com/plugins/submissions
ComposioHQ: https://github.com/ComposioHQ/awesome-claude-skills/pull/481
travisvn: https://github.com/travisvn/awesome-claude-skills/pull/457
hesreallyhim: https://github.com/hesreallyhim/awesome-claude-code/issues/1091
"

if [ -n "$HEALTH_ISSUES" ]; then
    REPORT+="
Health issues:
$(echo -e "$HEALTH_ISSUES")
"
fi

if [ "$CHANGED" = true ]; then
    # Show diff if previous state exists
    if [ -n "${PREVIOUS:-}" ]; then
        REPORT+="
Changes detected:
$(diff <(echo "$PREVIOUS") <(echo "$CURRENT") || true)
"
    fi

    # Send email
    echo "$REPORT" | mail -s "$SUBJECT" "$EMAIL" 2>/dev/null || true

    # Also log
    echo "[$(date '+%Y-%m-%d %H:%M')] Status change detected:" >> "$HOME/.local/log/lean-listings.log"
    echo "$REPORT" >> "$HOME/.local/log/lean-listings.log"
else
    echo "[$(date '+%Y-%m-%d %H:%M')] No changes." >> "$HOME/.local/log/lean-listings.log"
fi

# Always print to stdout (for manual runs)
echo "$REPORT"
if [ "$CHANGED" = true ]; then
    echo "(Status change detected — email sent)"
else
    echo "(No changes since last check)"
fi
