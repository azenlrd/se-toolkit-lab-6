import os
import sys
import json
import argparse
from pathlib import Path
from openai import OpenAI

# Initialize client for OpenRouter
# Ensure OPENROUTER_API_KEY environment variable is set
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Choose a Llama model that supports tool calling
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct" # or "meta-llama/llama-3.1-8b-instruct"

def secure_path(path_str):
    """Secures the path to prevent directory traversal outside PROJECT_ROOT."""
    target_path = (PROJECT_ROOT / path_str).resolve()
    if not target_path.is_relative_to(PROJECT_ROOT):
        raise PermissionError("Access denied. Path is outside the project root.")
    return target_path

def list_files(path: str) -> str:
    """Lists files and directories at a given path."""
    try:
        target_path = secure_path(path)
        if not target_path.exists():
            return f"Error: Directory '{path}' does not exist."
        if not target_path.is_dir():
            return f"Error: '{path}' is not a directory."
        
        entries = os.listdir(target_path)
        return "\n".join(entries) if entries else "Directory is empty."
    except PermissionError as e:
        return str(e)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_file(path: str) -> str:
    """Reads the contents of a file."""
    try:
        target_path = secure_path(path)
        if not target_path.exists():
            return f"Error: File '{path}' does not exist."
        if not target_path.is_file():
            return f"Error: '{path}' is not a file."
        
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    except PermissionError as e:
        return str(e)
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Define the tools schema
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given relative path from the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative directory path (e.g. 'wiki')"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path (e.g. 'wiki/git-workflow.md')"}
                },
                "required": ["path"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a Documentation Agent. You have access to tools to explore the project.
Always use `list_files` to discover files in directories (like 'wiki'), and `read_file` to read content to find answers.

CRITICAL INSTRUCTION: When you have found the final answer, you MUST output ONLY a valid JSON object. Do not include markdown code blocks (like ```json), do not include explanatory text before or after the JSON.

Format exactly like this:
{
  "answer": "Your detailed answer here.",
  "source": "wiki/file-name.md#section-anchor"
}
The 'source' must include the file path and the relevant markdown section anchor if applicable.
"""

def extract_json_from_text(text):
    """Helper to cleanly extract JSON if the LLM adds markdown blocks."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="Documentation Agent")
    parser.add_argument("question", type=str, help="The question to ask the agent")
    args = parser.parse_args()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": args.question}
    ]

    executed_tools = []
    max_iterations = 10

    for i in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            temperature=0.1
        )

        msg = response.choices[0].message
        
        # If the LLM didn't call any tools, it's giving the final answer
        if not msg.tool_calls:
            try:
                # Clean up response in case Llama outputs markdown formatting
                clean_content = extract_json_from_text(msg.content)
                final_output = json.loads(clean_content)
            except json.JSONDecodeError:
                # Fallback if the LLM failed to return valid JSON
                final_output = {"answer": msg.content, "source": "unknown"}
            
            # Attach the tool calls history to the final JSON
            final_output["tool_calls"] = executed_tools
            print(json.dumps(final_output, indent=2))
            sys.exit(0)

        # If tools were called, process them
        messages.append(msg) # Append the assistant's tool call request

        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            
            # Handle empty arguments gracefully (sometimes happens with open source models)
            args_str = tool_call.function.arguments or "{}"
            try:
                tool_args = json.loads(args_str)
            except json.JSONDecodeError:
                tool_args = {}
            
            if tool_name == "list_files":
                result = list_files(tool_args.get("path", ""))
            elif tool_name == "read_file":
                result = read_file(tool_args.get("path", ""))
            else:
                result = f"Error: Unknown tool '{tool_name}'"

            # Record for our final JSON output
            executed_tools.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result[:500] + "..." if len(result) > 500 else result # Truncate massive results
            })

            # Append tool result to conversation history
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    # If we hit the 10 loop limit
    fallback = {
        "answer": "Reached maximum tool execution limit.",
        "source": "unknown",
        "tool_calls": executed_tools
    }
    print(json.dumps(fallback, indent=2))

if __name__ == "__main__":
    main()
