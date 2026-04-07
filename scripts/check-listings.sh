#!/bin/bash
# check-listings.sh — Monitor public repo directory listing PRs
# Runs daily via launchd. Sends email only on status changes.
#
# Tracks: lean-skill listings + Saudi-RE-Data directories + FDA-Tunnel directories
#
# Configure recipient via LEAN_LISTINGS_EMAIL env var (launchd plist or shell).
# If unset, the script logs but does not send email.

set -euo pipefail

STATE_FILE="$HOME/.local/state/lean-listings.state"
EMAIL="${LEAN_LISTINGS_EMAIL:-}"
SUBJECT="[repo listings] Status change detected"

mkdir -p "$(dirname "$STATE_FILE")"

# Collect current statuses
declare -A STATUS

# ── lean-skill listings ──

# 1. ComposioHQ PR #481 (CLOSED — kept for history)
composio_state=$(gh pr view 481 --repo ComposioHQ/awesome-claude-skills --json state -q .state 2>/dev/null || echo "ERROR")
STATUS[lean_composio]="$composio_state"

# 2. travisvn PR #457 (CLOSED — kept for history)
travisvn_state=$(gh pr view 457 --repo travisvn/awesome-claude-skills --json state -q .state 2>/dev/null || echo "ERROR")
STATUS[lean_travisvn]="$travisvn_state"

# 3. hesreallyhim issue #1323
hesreallyhim_state=$(gh issue view 1323 --repo hesreallyhim/awesome-claude-code --json state -q .state 2>/dev/null || echo "ERROR")
STATUS[lean_hesreallyhim]="$hesreallyhim_state"

# 4. SkillHub — check if indexed
skillhub_check=$(curl -s "https://www.skillhub.club/skills?search=lean" 2>/dev/null | grep -oi "civillizard\|claude-lean-skill" | head -1 || true)
if [ -n "$skillhub_check" ]; then
    STATUS[lean_skillhub]="INDEXED"
else
    STATUS[lean_skillhub]="NOT_INDEXED"
fi

# 5. Anthropic — can't check programmatically (needs browser auth)
anthropic_check=$(curl -s "https://claude.com/plugins" 2>/dev/null | grep -oi '"lean"' | head -1 || true)
if [ -n "$anthropic_check" ]; then
    STATUS[lean_anthropic]="LISTED"
else
    STATUS[lean_anthropic]="PENDING"
fi

# ── Saudi-Real-Estate-Data listings ──

# 6. awesomedata/apd-core PR #374
apd_state=$(gh pr view 374 --repo awesomedata/apd-core --json state,mergedAt -q 'if .mergedAt then "MERGED" else .state end' 2>/dev/null || echo "ERROR")
STATUS[saudi_apd]="$apd_state"

# 7. NajiElKotob/Awesome-Datasets PR #3
naji_state=$(gh pr view 3 --repo NajiElKotob/Awesome-Datasets --json state,mergedAt -q 'if .mergedAt then "MERGED" else .state end' 2>/dev/null || echo "ERROR")
STATUS[saudi_naji]="$naji_state"

# ── MacOS-Full-Disk-Access-Tunnel listings ──

# 8. iCHAIT/awesome-macOS PR #772
macos_state=$(gh pr view 772 --repo iCHAIT/awesome-macOS --json state,mergedAt -q 'if .mergedAt then "MERGED" else .state end' 2>/dev/null || echo "ERROR")
STATUS[fda_macos]="$macos_state"

# 9. BlackSquirrelz/awesome-apple-security PR #2
apple_sec_state=$(gh pr view 2 --repo BlackSquirrelz/awesome-apple-security --json state,mergedAt -q 'if .mergedAt then "MERGED" else .state end' 2>/dev/null || echo "ERROR")
STATUS[fda_apple_sec]="$apple_sec_state"

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
for key in lean_anthropic lean_composio lean_travisvn lean_hesreallyhim lean_skillhub saudi_apd saudi_naji fda_macos fda_apple_sec health; do
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
REPORT="Public Repo Listing Status — $(date '+%Y-%m-%d %H:%M AST')

── claude-lean-skill ──
Directory               Status
───────────────────     ──────────────────
Anthropic Directory     ${STATUS[lean_anthropic]}
ComposioHQ PR #481      ${STATUS[lean_composio]}
travisvn PR #457        ${STATUS[lean_travisvn]}
hesreallyhim #1323      ${STATUS[lean_hesreallyhim]}
SkillHub                ${STATUS[lean_skillhub]}

── Saudi-Real-Estate-Data ──
Directory               Status
───────────────────     ──────────────────
apd-core PR #374        ${STATUS[saudi_apd]}
Awesome-Datasets PR #3  ${STATUS[saudi_naji]}

── MacOS-FDA-Tunnel ──
Directory               Status
───────────────────     ──────────────────
awesome-macOS PR #772   ${STATUS[fda_macos]}
apple-security PR #2    ${STATUS[fda_apple_sec]}

Plugin health           ${STATUS[health]}

Links:
  hesreallyhim: https://github.com/hesreallyhim/awesome-claude-code/issues/1323
  apd-core: https://github.com/awesomedata/apd-core/pull/374
  Awesome-Datasets: https://github.com/NajiElKotob/Awesome-Datasets/pull/3
  awesome-macOS: https://github.com/iCHAIT/awesome-macOS/pull/772
  apple-security: https://github.com/BlackSquirrelz/awesome-apple-security/pull/2
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

    # Send email if recipient is configured
    if [ -n "$EMAIL" ]; then
        echo "$REPORT" | mail -s "$SUBJECT" "$EMAIL" 2>/dev/null || true
    fi

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
