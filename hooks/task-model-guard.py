#!/usr/bin/env python3
"""PreToolUse hook for Agent tool — suggests optimal model routing.

Fires when a subagent is about to spawn. If no model is specified (the
subagent then inherits the session model), analyzes the prompt/subagent_type
and suggests a cheaper model when appropriate. Never blocks — it only adds a
suggestion to the allow decision.

Tier-aware: set LEAN_SESSION_MODEL to your session model (haiku | sonnet |
opus | fable, or a full model id such as claude-opus-5-5). The hook then only
suggests tiers strictly cheaper than it, and — when the session runs above
Opus — suggests opus for complex delegated work. Unset or unrecognised: the
v2.0.0 behaviour (no assumption about the session model).

Also nudges the user to run /lean when a complex multi-step task is
detected without a .lean-plan.md in the working directory.

Setup: Add to your Claude Code settings.json:
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Agent",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/task-model-guard.py"
          }
        ]
      }
    ]
  }
}
"""

import json
import os
import re
import sys


# --- Tier ladder (cheapest -> priciest) ---

TIERS = ["haiku", "sonnet", "opus", "fable"]


def session_tier():
    """Rank of the session model from LEAN_SESSION_MODEL, or None if unknown."""
    raw = os.environ.get("LEAN_SESSION_MODEL", "").lower()
    for rank, name in enumerate(TIERS):
        if name in raw:
            return rank
    return None


# --- Pattern banks for task classification ---

EXPLORE_PATTERNS = [
    r"\b(search|find|locate|list|grep|glob|look for|check if)\b",
    r"\b(what files|where is|how many|count)\b",
    r"\bread\b.{0,30}\b(summarize|extract|return|list)\b",
    r"\b(map|scan|discover|inventory)\b",
]

CODEGEN_PATTERNS = [
    r"\b(write|implement|create|add|generate)\b.{0,40}\b(code|function|test|class|module|endpoint|handler|script)\b",
    r"\b(write tests|add tests|update tests|run tests)\b",
    r"\b(refactor|rename|move|migrate)\b.{0,30}\b(to|from|into)\b",
    r"\b(straightforward|mechanical|following.{0,20}pattern)\b",
]

COMPLEX_PATTERNS = [
    r"\b(debug|architect|design|investigate|figure out)\b",
    r"\b(why does|root cause|trade.?off|novel|complex)\b",
    r"\b(redesign|rethink|new approach|ambiguous)\b",
    r"\b(analyze.{0,20}(issue|problem|bug|error))\b",
]

# Signals that the task is multi-step and would benefit from /lean planning
MULTI_STEP_PATTERNS = [
    r"\b(all|each|every|remaining)\b.{0,30}\b(files?|endpoints?|components?|adapters?|modules?|tests?)\b",
    r"\b(migrate|convert|rewrite|refactor)\b.{0,30}\b\d+\b",
    r"\b(step\s*[123456789]|phase\s*[123456789]|first.{0,20}then)\b",
    r"\b(bulk|batch|across|throughout)\b",
]


def classify_task(prompt, subagent_type, description, session=None):
    """Return (suggested_model, reason) or (None, None) if no cheaper tier fits.

    session: rank of the session model in TIERS, or None when unknown.
    """
    text = f"{prompt} {description}".lower()

    # Subagent type is a strong signal
    if subagent_type == "Explore":
        return "haiku", "Explore agents only search and read files"
    if subagent_type == "Bash":
        return "haiku", "Bash agents run simple shell commands"

    # Complex signals override everything — opus-class work. Only worth a
    # suggestion when the session runs above opus (opus is then cheaper).
    complex_score = sum(1 for p in COMPLEX_PATTERNS if re.search(p, text))
    if complex_score > 0:
        if session is not None and session > TIERS.index("opus"):
            return "opus", "Complex delegated work — opus is cheaper than the session model"
        return None, None

    # Score the task
    explore_score = sum(1 for p in EXPLORE_PATTERNS if re.search(p, text))
    codegen_score = sum(1 for p in CODEGEN_PATTERNS if re.search(p, text))

    if explore_score > codegen_score and explore_score > 0:
        return "haiku", "Task looks like exploration/search"

    if codegen_score > 0:
        return "sonnet", "Task looks like well-defined code generation"

    # Short prompts on general-purpose agents are often simple tasks
    if len(prompt) < 200 and subagent_type == "general-purpose":
        return "haiku", "Short prompt on general-purpose agent"

    # Can't classify confidently — don't nag
    return None, None


def detect_lean_opportunity(prompt, description):
    """Check if task looks complex enough to benefit from /lean planning."""
    text = f"{prompt} {description}".lower()

    # Already running under a lean plan — don't nag
    if os.path.exists(".lean-plan.md"):
        return None

    multi_step_score = sum(1 for p in MULTI_STEP_PATTERNS if re.search(p, text))
    long_prompt = len(prompt) > 500

    if multi_step_score >= 2 or (multi_step_score >= 1 and long_prompt):
        return "This looks like a multi-step task. Consider running /lean first for optimized model routing."

    return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return  # exit 0 with no output = allow

    tool_input = input_data.get("tool_input", {})
    model = tool_input.get("model")
    prompt = tool_input.get("prompt", "")
    subagent_type = tool_input.get("subagent_type", "")
    description = tool_input.get("description", "")

    # Model explicitly set — Claude made a deliberate choice, allow
    if model:
        return  # exit 0 with no output = allow

    # No model = inherits the session model. Check if a cheaper tier works.
    session = session_tier()
    suggested, reason = classify_task(prompt, subagent_type, description, session)
    # Only suggest a tier strictly cheaper than a known session model.
    if suggested and session is not None and TIERS.index(suggested) >= session:
        suggested, reason = None, None

    # Also check if /lean would help
    lean_nudge = detect_lean_opportunity(prompt, description)

    reason_parts = []
    if suggested:
        reason_parts.append(f'Suggestion: model="{suggested}" — {reason}.')
    if lean_nudge:
        reason_parts.append(lean_nudge)

    if reason_parts:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": (
                        "Auto-approved. " + " ".join(reason_parts)
                    ),
                }
            },
            sys.stdout,
        )
    # else: exit 0 with no output = allow


if __name__ == "__main__":
    main()
