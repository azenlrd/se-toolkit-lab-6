# Plan: Task 2 - The Documentation Agent

## 1. Tool Schemas
We will define two tools using function calling schema:
- `read_file`: takes `path` (string).
- `list_files`: takes `path` (string).

## 2. Agentic Loop
- The agent will run in a `while` loop (maximum 10 iterations).
- On each iteration, we send the conversation history to the Llama model via OpenRouter API.
- If the LLM returns `tool_calls`, we:
  1. Parse the tool name and arguments.
  2. Execute the local Python function (`read_file` or `list_files`).
  3. Append the result as a `tool` role message to the history.
  4. Record the tool call in a separate `executed_tools` list for the final JSON output.
- If the LLM returns standard text (no tool calls), we treat it as the final answer, extract the JSON (`answer`, `source`), inject the `executed_tools` history, print, and break the loop.

## 3. Path Security
We will use Python's `pathlib`.
- Resolve the requested path: `target = (PROJECT_ROOT / requested_path).resolve()`
- Check if it's within the project: `target.is_relative_to(PROJECT_ROOT)`.
- If false, return a security error message to the LLM instead of crashing.
