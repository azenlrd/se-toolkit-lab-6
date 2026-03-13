import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent


def run_agent(question: str) -> dict:
    result = subprocess.run(
        [sys.executable, "agent.py", question],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR", "/tmp/uv-cache")},
    )
    if result.returncode != 0:
        pytest.fail(f"agent.py exited with {result.returncode}: {result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"Agent did not return valid JSON: {exc}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def test_resolve_merge_conflict_uses_read_file() -> None:
    data = run_agent("How do you resolve a merge conflict?")
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "read_file" in tool_names
    assert "git-workflow.md" in data.get("source", "")


def test_wiki_directory_question_uses_list_files() -> None:
    data = run_agent("What files are in the wiki?")
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "list_files" in tool_names


def test_framework_question_uses_read_file() -> None:
    data = run_agent("What framework does the backend use?")
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "read_file" in tool_names


def test_item_count_question_uses_query_api() -> None:
    data = run_agent("How many items are in the database?")
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "query_api" in tool_names


def test_unauthenticated_items_status_uses_query_api() -> None:
    data = run_agent(
        "What HTTP status code does the API return when you request /items/ without sending an authentication header?"
    )
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "query_api" in tool_names
