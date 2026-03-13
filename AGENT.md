# Agent Documentation

## Architecture & Tools
Our agent utilizes an LLM to dynamically select tools based on user queries. In addition to reading local documentation and source code (`read_file`, `wiki_search`), the agent is now equipped with the `query_api` tool. This allows it to bridge the gap between static knowledge and the real-time, dynamic state of the deployed system.

## The `query_api` Tool and Authentication
The `query_api` tool allows the agent to make HTTP requests (GET, POST, etc.) directly to the live backend. 
It operates using two strict configuration parameters injected via environment variables:
1. `AGENT_API_BASE_URL`: Defines the target host (defaults to `http://localhost:42002`).
2. `LMS_API_KEY`: A secure backend token passed in the HTTP headers to authenticate the requests.
This separation ensures that the LLM (`LLM_API_KEY`) and the Backend (`LMS_API_KEY`) have completely isolated security contexts.

## Decision Making: Wiki vs System Tools
The LLM's system prompt has been carefully engineered to differentiate between static and dynamic queries. 
- If the user asks "What framework does the backend use?", the LLM recognizes this as static system architecture and uses `read_file` to inspect `requirements.txt` or source code.
- If the user asks "How many items are in the database?", the LLM recognizes this as stateful data and invokes `query_api` with `GET /items/`.

## Lessons Learned from Benchmarking
During the benchmark evaluation (`run_eval.py`), several challenges emerged. Initially, the agent struggled with formatting the JSON body for POST requests, which was resolved by clarifying the `body` parameter description in the schema. Additionally, handling HTTP errors gracefully inside the `query_api` function was crucial; returning the exact `status_code` and error payload allowed the LLM to self-correct and debug issues on the fly rather than crashing. The final evaluation score resulted in a 10/10 pass rate on local tests.
