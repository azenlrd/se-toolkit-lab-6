# Task 3: The System Agent Plan

## 1. Tool Schema (`query_api`)
- **Name**: `query_api`
- **Description**: Sends HTTP requests to the deployed backend API to get real-time system data, item counts, or test endpoints.
- **Parameters**: 
  - `method` (string): HTTP method (GET, POST, etc.)
  - `path` (string): API endpoint path (e.g., `/items/`)
  - `body` (string, optional): JSON formatted request body.

## 2. Authentication & Configuration
- Backend Base URL: `os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")`
- Backend API Key: `os.getenv("LMS_API_KEY")` (Passed in headers, e.g., `X-API-Key` or `Authorization: Bearer`).
- LLM Auth: `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL` (from `os.getenv`).

## 3. Prompt Updates
I will update the system prompt to explicitly tell the agent:
- Use `wiki_search`/`read_file` for documentation and source code.
- Use `query_api` when asked about live database items, current system status, or real-time metrics.

## 4. Benchmark Iteration (To be filled after first run)
- Initial Score: TBD
- First failures: TBD
- Fix strategy: TBD
