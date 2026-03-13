# Task 1: Call an LLM from Code

## Выбор провайдера и модели
- Провайдер: OpenRouter (бесплатные модели, поддержка tool calling).
- Модель: `meta-llama/llama-3.3-70b-instruct:free` – хорошо поддерживает вызов инструментов, бесплатна.
- API: OpenAI-совместимый, используем библиотеку `openai`.

## Структура агента
- Чтение конфигурации из `.env.agent.secret`.
- Обработка аргумента командной строки.
- Запрос к LLM через `client.chat.completions.create`.
- Формирование JSON с полями `answer` и `tool_calls` (пока пустой массив).
- Вывод только JSON в stdout, все диагностические сообщения в stderr.

## Запуск
```bash
uv run agent.py "What does REST stand for?"