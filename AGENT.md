# Agent CLI — Task 1: Call an LLM from Code

## Обзор
`agent.py` — это командная строка (CLI), которая принимает вопрос пользователя, отправляет его в языковую модель (LLM) через OpenRouter и возвращает структурированный JSON-ответ. Это база для будущих задач, где будут добавлены вызовы инструментов (tool calls).

## Используемый LLM
- **Провайдер**: [OpenRouter](https://openrouter.ai) — предоставляет бесплатный доступ к множеству моделей с поддержкой OpenAI‑совместимого API.
- **Модель по умолчанию**: `meta-llama/llama-3.3-70b-instruct:free` (бесплатная, с хорошей поддержкой tool calling, что потребуется в Task 2–3).
- **Альтернативные модели**: можно выбрать другие бесплатные модели из [коллекции OpenRouter](https://openrouter.ai/collections/free-models), убедившись, что они поддерживают tool calling.
- **API**: OpenAI-совместимый чат-комплейшнс, реализованный через библиотеку `openai`.

## Конфигурация
Все настройки хранятся в файле `.env.agent.secret` (скопирован из `.env.agent.example` и добавлен в `.gitignore`). Пример содержимого:

```bash
LLM_API_KEY=sk-or-v1-...
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free