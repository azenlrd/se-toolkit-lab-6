#!/usr/bin/env python3
"""
Agent that sends a question to an LLM and returns a JSON response.
"""

import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env.agent.secret
load_dotenv(".env.agent.secret")

def main():
    # Read question from command line
    if len(sys.argv) < 2:
        print("Usage: agent.py <question>", file=sys.stderr)
        sys.exit(1)
    question = sys.argv[1]

    # Get LLM configuration
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1")
    model = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    if not api_key:
        print("Error: LLM_API_KEY not set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    # Call LLM
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the user's question concisely."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        sys.exit(1)

    # Build output JSON
    output = {
        "answer": answer,
        "tool_calls": []  # will be used in later tasks
    }

    # Print only JSON to stdout
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()