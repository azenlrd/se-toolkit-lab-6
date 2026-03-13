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


def test_docker_cleanup_wiki_question_reads_docker_pages() -> None:
    data = run_agent(
        "What does the project wiki say about cleaning up Docker? List the commands."
    )
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    read_paths = [call.get("args", {}).get("path", "") for call in data.get("tool_calls", [])]
    assert "read_file" in tool_names
    assert "wiki/docker.md" in read_paths
    assert "docker" in data.get("answer", "").lower()


def test_dockerfile_question_reads_backend_dockerfile() -> None:
    data = run_agent("Read the Dockerfile and explain how the backend container starts.")
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    read_paths = [call.get("args", {}).get("path", "") for call in data.get("tool_calls", [])]
    answer_lower = data.get("answer", "").lower()
    assert "read_file" in tool_names
    assert "Dockerfile" in read_paths
    assert "cmd" in answer_lower or "run.py" in answer_lower or "multi-stage" in answer_lower


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


def test_completion_rate_bug_question_uses_query_and_source() -> None:
    data = run_agent(
        "Query the /analytics/completion-rate endpoint for a lab that has no data (e.g., lab-99). What error do you get, and what is the bug in the source code?"
    )
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "query_api" in tool_names
    assert "read_file" in tool_names


def test_top_learners_bug_question_uses_query_and_source() -> None:
    data = run_agent(
        "The /analytics/top-learners endpoint crashes for some labs. Query it, find the error, and read the source code to explain what went wrong."
    )
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "query_api" in tool_names
    assert "read_file" in tool_names


def test_request_journey_question_uses_read_file() -> None:
    data = run_agent(
        "Read the docker-compose.yml and the backend Dockerfile. Explain the full journey of an HTTP request from the browser to the database and back."
    )
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "read_file" in tool_names
    assert len(data.get("answer", "").split()) >= 20


def test_etl_idempotency_question_reads_etl_source() -> None:
    data = run_agent(
        "Read the ETL pipeline code. Explain how it ensures idempotency — what happens if the same data is loaded twice?"
    )
    tool_names = [call["tool"] for call in data.get("tool_calls", [])]
    assert "read_file" in tool_names
    assert "idempot" in data.get("answer", "").lower() or "duplicate" in data.get("answer", "").lower()
