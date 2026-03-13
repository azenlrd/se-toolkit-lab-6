import json
import subprocess
import pytest

def run_agent(question):
    """Helper to run the agent CLI and parse its JSON output."""
    result = subprocess.run(
        ["uv", "run", "agent.py", question],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Agent did not return valid JSON. Output was: {result.stdout}\nError: {result.stderr}")

def test_resolve_merge_conflict():
    """Test if agent uses read_file and identifies the correct source."""
    question = "How do you resolve a merge conflict?"
    data = run_agent(question)
    
    assert "tool_calls" in data
    assert "source" in data
    
    # Check if read_file was used
    used_tools = [call["tool"] for call in data["tool_calls"]]
    assert "read_file" in used_tools
    
    # Source should mention git-workflow.md
    assert "git-workflow.md" in data["source"]

def test_what_files_in_wiki():
    """Test if agent uses list_files when asked about directory contents."""
    question = "What files are in the wiki?"
    data = run_agent(question)
    
    assert "tool_calls" in data
    
    # Check if list_files was used
    used_tools = [call["tool"] for call in data["tool_calls"]]
    assert "list_files" in used_tools
