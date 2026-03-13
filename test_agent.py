import subprocess
import json
import sys

def test_agent_outputs_json():
    """Test that agent.py returns valid JSON with answer and tool_calls."""
    # Запускаем агента с тестовым вопросом
    result = subprocess.run(
        [sys.executable, "agent.py", "What is the capital of France?"],
        capture_output=True,
        text=True,
        timeout=30
    )

    # Проверяем код возврата
    assert result.returncode == 0, f"Agent failed with error: {result.stderr}"

    # Проверяем, что stdout — валидный JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.stdout}"

    # Проверяем наличие обязательных полей
    assert "answer" in output, "Missing 'answer' field in output"
    assert isinstance(output["answer"], str), "'answer' must be a string"

    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be a list"
    assert output["tool_calls"] == [], "'tool_calls' should be an empty list in Task 1"