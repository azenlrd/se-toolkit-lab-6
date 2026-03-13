import os
import sys
import json
import urllib.request
import urllib.error

# ==========================================
# 1. КОНФИГУРАЦИЯ (ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ)
# ==========================================
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

LMS_API_KEY = os.getenv("LMS_API_KEY", "")
AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

# ==========================================
# 2. РЕАЛИЗАЦИЯ ИНСТРУМЕНТОВ (TOOLS)
# ==========================================

def read_file(path: str) -> str:
    """Reads a local file (useful for source code or wiki)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            # Ограничиваем чтение, чтобы не превысить лимит контекста LLM
            return f.read()[:10000] 
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def list_files(path: str = ".") -> str:
    """Lists files in a directory to help agent find documents."""
    try:
        return json.dumps(os.listdir(path))
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"

def query_api(method: str, path: str, body: str = None) -> str:
    """Calls the deployed backend API."""
    url = f"{AGENT_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    
    # Авторизация бекенда (передаем как Bearer токен, а также как X-API-Key на всякий случай)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LMS_API_KEY}",
        "X-API-Key": LMS_API_KEY 
    }
    
    req_body = body.encode('utf-8') if body else None
    req = urllib.request.Request(url, data=req_body, headers=headers, method=method.upper())
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        status_code = e.code
        response_body = e.read().decode('utf-8')
    except urllib.error.URLError as e:
        return json.dumps({"error": f"Failed to connect to backend: {str(e.reason)}"})

    # Пытаемся распарсить JSON-ответ, если он есть
    try:
        parsed_body = json.loads(response_body) if response_body else None
    except json.JSONDecodeError:
        parsed_body = response_body

    return json.dumps({
        "status_code": status_code,
        "body": parsed_body
    })

# ==========================================
# 3. СХЕМА ИНСТРУМЕНТОВ ДЛЯ LLM
# ==========================================
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a local file. Use this to read documentation, wiki, or source code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory. Use this to search for documentation files or code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path, default is '.'"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Call the live deployed backend API. Use this ONLY for fetching live system data, item counts, scores, or testing live endpoints. Do NOT use this for reading static code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP method: GET, POST, PUT, DELETE"},
                    "path": {"type": "string", "description": "API path starting with slash, e.g., /items/ or /analytics/completion-rate"},
                    "body": {"type": "string", "description": "Optional JSON formatted string for the request body (e.g., '{\"key\": \"value\"}')"}
                },
                "required": ["method", "path"]
            }
        }
    }
]

# ==========================================
# 4. ФУНКЦИИ ВЗАИМОДЕЙСТВИЯ С LLM И АГЕНТОМ
# ==========================================
def call_llm(messages: list) -> dict:
    """Отправляет запрос к LLM (OpenAI-compatible) используя urllib."""
    url = f"{LLM_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "tool_choice": "auto"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"LLM API Error: {e}", file=sys.stderr)
        sys.exit(1)

def run_agent(query: str):
    """Основной цикл (Agentic Loop)."""
    system_prompt = (
        "You are an expert system agent with access to the project's codebase, wiki, and live backend API. "
        "Your job is to answer the user's questions correctly by utilizing your tools.\n"
        "- Use `list_files` and `read_file` to find static information: frameworks, ports, wiki documentation, or source code logic.\n"
        "- Use `query_api` to find dynamic/live information: database item counts, analytics, current scores, or to test endpoints.\n"
        "Think step by step. If a file or endpoint gives an error, diagnose it and try a different path."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    executed_tool_calls = []
    max_iterations = 10
    
    for _ in range(max_iterations):
        response = call_llm(messages)
        message = response["choices"][0]["message"]
        
        # Защита от AttributeError: 'NoneType' (LLM может вернуть null в content, если использует tools)
        content = message.get("content") or ""
        
        # Добавляем ответ ассистента в историю
        assistant_msg = {"role": "assistant", "content": content}
        if "tool_calls" in message:
            assistant_msg["tool_calls"] = message["tool_calls"]
        messages.append(assistant_msg)
        
        # Если LLM решила не использовать инструменты — цикл завершен, выдаем ответ
        if "tool_calls" not in message or not message["tool_calls"]:
            break
            
        # Исполняем вызванные инструменты
        for tool_call in message["tool_calls"]:
            func_name = tool_call["function"]["name"]
            try:
                args = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}
                
            result_str = ""
            if func_name == "read_file":
                result_str = read_file(args.get("path", ""))
            elif func_name == "list_files":
                result_str = list_files(args.get("path", "."))
            elif func_name == "query_api":
                result_str = query_api(args.get("method"), args.get("path"), args.get("body"))
            else:
                result_str = f"Error: Tool {func_name} not found."
                
            # Сохраняем информацию о вызове для итогового JSON
            executed_tool_calls.append({
                "tool": func_name,
                "args": args,
                "result": result_str
            })
            
            # Возвращаем результат инструмента обратно LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result_str
            })
            
    # Формируем и печатаем итоговый JSON для CLI-интерфейса
    final_output = {
        "answer": messages[-1]["content"] if messages[-1]["role"] == "assistant" else "Error: Failed to generate answer.",
        "tool_calls": executed_tool_calls
    }
    
    print(json.dumps(final_output, indent=2))

# ==========================================
# 5. ТОЧКА ВХОДА (CLI)
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"")
        sys.exit(1)
        
    user_query = sys.argv[1]
    run_agent(user_query)