#!/usr/bin/env python3
"""PreToolUse hook for Agent tool — suggests optimal model routing.

Fires when a subagent is about to spawn. If no model is specified
(defaults to Opus), analyzes the prompt/subagent_type and suggests a
lighter model when appropriate. Never blocks — only suggests via "ask".

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


def classify_task(prompt, subagent_type, description):
    """Return (suggested_model, reason) or (None, None) if Opus is fine."""
    text = f"{prompt} {description}".lower()

    # Subagent type is a strong signal
    if subagent_type == "Explore":
        return "haiku", "Explore agents only search and read files"
    if subagent_type == "Bash":
        return "haiku", "Bash agents run simple shell commands"

    # Complex signals override everything — Opus is correct
    complex_score = sum(1 for p in COMPLEX_PATTERNS if re.search(p, text))
    if complex_score > 0:
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

    # No model = inherits parent (likely Opus). Check if lighter model works.
    suggested, reason = classify_task(prompt, subagent_type, description)

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
