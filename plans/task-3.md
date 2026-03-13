# Task 3: The System Agent Plan

## 1. Tool Schema (`query_api`)
- **Name**: `query_api`
- **Description**: Sends HTTP requests to the deployed backend API to get real-time system data, item counts, or test endpoints.
- **Parameters**: `method`, `path`, and optional `body`.

## 2. Authentication & Configuration
- Backend Base URL: `os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")`
- Backend API Key: `os.getenv("LMS_API_KEY")` (Passed in headers).
- LLM Auth: `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`.

## 3. Prompt Updates
Instruct the agent to use `read_file` for static code/wiki, and `query_api` for live DB data, scores, or endpoint testing.

## 4. Benchmark Iteration
- Initial Score: 0/10 (before implementation)
- Fix strategy: Implemented robust urllib error handling to return JSON with status_code instead of crashing. Now 10/10.
