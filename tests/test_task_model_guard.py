"""Tests for hooks/task-model-guard.py — the tier-aware model suggestion.

Run: python3 -m pytest -q tests/
"""

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "task-model-guard.py")

COMPLEX = "Investigate why the cache invalidation fails and find the root cause"
EXPLORE = "Search the repo and list every file that imports the config loader"
CODEGEN = "Write tests for the parser function following the existing pattern"


def run_hook(tool_input, session=None, cwd=None):
    env = {k: v for k, v in os.environ.items() if k != "LEAN_SESSION_MODEL"}
    if session is not None:
        env["LEAN_SESSION_MODEL"] = session
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"tool_input": tool_input}),
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=10,
    )
    assert p.returncode == 0, p.stderr
    if not p.stdout.strip():
        return None
    return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecisionReason"]


def ti(prompt, subagent_type="general-purpose"):
    return {"prompt": prompt, "subagent_type": subagent_type, "description": ""}


# --- unset: v2.0.0 behaviour ----------------------------------------------------


def test_unset_complex_is_silent(tmp_path):
    assert run_hook(ti(COMPLEX), cwd=tmp_path) is None


def test_unset_explore_suggests_haiku(tmp_path):
    assert 'model="haiku"' in run_hook(ti(EXPLORE), cwd=tmp_path)


def test_unset_codegen_suggests_sonnet(tmp_path):
    assert 'model="sonnet"' in run_hook(ti(CODEGEN), cwd=tmp_path)


def test_explicit_model_is_never_touched(tmp_path):
    t = dict(ti(EXPLORE), model="opus")
    assert run_hook(t, session="fable", cwd=tmp_path) is None


# --- tier-aware ------------------------------------------------------------------


def test_fable_session_complex_suggests_opus(tmp_path):
    out = run_hook(ti(COMPLEX), session="fable", cwd=tmp_path)
    assert 'model="opus"' in out


@pytest.mark.parametrize("session", ["opus", "sonnet", "haiku"])
def test_complex_never_suggests_opus_at_or_below_opus(tmp_path, session):
    assert run_hook(ti(COMPLEX), session=session, cwd=tmp_path) is None


def test_sonnet_session_drops_sonnet_suggestion(tmp_path):
    assert run_hook(ti(CODEGEN), session="sonnet", cwd=tmp_path) is None


def test_sonnet_session_keeps_haiku_suggestion(tmp_path):
    assert 'model="haiku"' in run_hook(ti(EXPLORE), session="sonnet", cwd=tmp_path)


def test_haiku_session_never_suggests(tmp_path):
    for p in (EXPLORE, CODEGEN, COMPLEX):
        assert run_hook(ti(p), session="haiku", cwd=tmp_path) is None
    assert run_hook(ti("x", "Explore"), session="haiku", cwd=tmp_path) is None


@pytest.mark.parametrize("session", ["claude-opus-5-5", "Claude-Fable-5-2", "OPUS"])
def test_full_model_ids_and_case_are_understood(tmp_path, session):
    out = run_hook(ti(COMPLEX), session=session, cwd=tmp_path)
    if "fable" in session.lower():
        assert 'model="opus"' in out
    else:
        assert out is None


def test_unknown_session_value_behaves_like_unset(tmp_path):
    assert run_hook(ti(COMPLEX), session="gpt-x", cwd=tmp_path) is None
    assert 'model="sonnet"' in run_hook(ti(CODEGEN), session="gpt-x", cwd=tmp_path)


def test_lean_nudge_survives_dropped_suggestion(tmp_path):
    prompt = "Refactor all 12 endpoints across the services in bulk, step 1 then step 2"
    out = run_hook(ti(prompt), session="haiku", cwd=tmp_path)
    assert out is not None and "/lean" in out and "model=" not in out
