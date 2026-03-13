# Documentation Agent

## Overview
This agent answers questions about the project by navigating the local filesystem using LLM tool calling. It implements an **agentic loop** to dynamically search for files and read their contents before formulating an answer. It uses the **OpenRouter API** and a **Llama** model.

## Tools
The agent has access to two secure tools:
1. `list_files(path)`: Lists files in a given directory relative to the project root.
2. `read_file(path)`: Reads the content of a specific file.

**Security:** Both tools use `pathlib` to resolve absolute paths and verify that they are strictly within the `PROJECT_ROOT`. Attempting directory traversal (e.g., `../`) will result in a permission error fed back to the LLM.

## Agentic Loop
1. The user's question is sent to the Llama model via OpenRouter along with tool schemas.
2. If the LLM requests a tool call, the local Python script executes the tool and appends the result to the conversation.
3. This process loops (up to 10 times) until the LLM has enough context.
4. Once satisfied, the LLM outputs a final JSON response containing the `answer` and the file `source`.
5. The CLI prints this JSON, injecting an array of `tool_calls` made during the process.
