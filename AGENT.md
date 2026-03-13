# Agent CLI — Task 1: Call an LLM from Code

## Overview
`agent.py` is a command-line interface (CLI) that takes a user’s question, sends it to a language model (LLM) via OpenRouter, and returns a structured JSON response. This serves as the foundation for future tasks, where tool calls will be added.

## LLM Used
- **Provider**: [OpenRouter](https://openrouter.ai) — provides free access to many models with OpenAI‑compatible API support.
- **Default model**: `meta-llama/llama-3.3-70b-instruct:free` (free, with good tool‑calling support needed for Tasks 2–3).
- **Alternative models**: you can choose other free models from the [OpenRouter free models collection](https://openrouter.ai/collections/free-models), making sure they support tool calling.
- **API**: OpenAI‑compatible chat completions, implemented via the `openai` library.

## Configuration
All settings are stored in the `.env.agent.secret` file (copied from `.env.agent.example` and added to `.gitignore`). Example contents:

```bash
LLM_API_KEY=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
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free