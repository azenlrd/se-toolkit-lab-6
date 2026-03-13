# Agent Documentation

## Architecture & Tools
Our agent is built upon a robust architecture that utilizes a Large Language Model (LLM) to dynamically select and execute tools based on natural language user queries. In addition to reading local documentation and source code via the `read_file` and `list_files` tools, the agent is now equipped with a powerful `query_api` tool. This critical addition allows the agent to bridge the gap between static repository knowledge and the real-time, dynamic state of the deployed backend system.

## The `query_api` Tool and Authentication
The `query_api` tool enables the agent to craft and send HTTP requests (such as GET, POST, PUT, and DELETE) directly to the live backend API. It operates using two strict configuration parameters that are securely injected via environment variables:
1. `AGENT_API_BASE_URL`: Defines the target host network address (which defaults to `http://localhost:42002`). This is explicitly read using `os.getenv`.
2. `LMS_API_KEY`: A secure backend authentication token passed seamlessly in the HTTP headers to authorize the requests.
This architectural separation ensures that the LLM API credentials and the Backend system API keys maintain completely isolated security contexts, following best security practices.

## Decision Making and Lessons Learned
The LLM's system prompt has been carefully engineered to differentiate between static and dynamic queries. If a user asks "What framework does the backend use?", the LLM recognizes this as static system architecture and uses `read_file`. Conversely, for "How many items are in the database?", it invokes `query_api`.

During the benchmark evaluation, several challenges emerged. Initially, the agent struggled with formatting the JSON body for POST requests. This was resolved by clarifying the `body` parameter description in the schema. Furthermore, handling HTTP errors gracefully inside the `query_api` function proved crucial. By returning the exact `status_code` and error payload, the LLM can now self-correct and debug issues on the fly rather than crashing. The final evaluation score demonstrated a complete pass rate on local benchmarks.
