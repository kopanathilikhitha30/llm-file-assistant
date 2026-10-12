"""CLI LLM assistant demonstrating OpenAI tool/function calling.

Examples:
  python llm_file_assistant.py "Read all resumes in the resumes folder"
  python llm_file_assistant.py "Find resumes mentioning Python experience"
  python llm_file_assistant.py "Create a summary file for resumes/resume_john_doe.txt"
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from openai import OpenAI
import fs_tools

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

TOOLS = [
    {
        "type": "function",
        "name": "list_files",
        "description": "List files in a directory, optionally filtered by extension.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path"},
                "extension": {"type": ["string", "null"], "description": "Optional extension such as .pdf or .txt"}
            },
            "required": ["directory", "extension"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Extract text and metadata from a PDF, TXT, or DOCX file.",
        "parameters": {
            "type": "object",
            "properties": {"filepath": {"type": "string"}},
            "required": ["filepath"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Write text to a file, creating parent directories as needed.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["filepath", "content"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "search_in_file",
        "description": "Search PDF, TXT, or DOCX text for a case-insensitive keyword and return context snippets.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "keyword": {"type": "string"}
            },
            "required": ["filepath", "keyword"],
            "additionalProperties": False
        },
        "strict": True
    }
]

FUNCTIONS = {
    "list_files": fs_tools.list_files,
    "read_file": fs_tools.read_file,
    "write_file": fs_tools.write_file,
    "search_in_file": fs_tools.search_in_file,
}


def run_assistant(query: str) -> str:
    """Run a user request through the model and execute any requested tools."""
    client = OpenAI()  # reads OPENAI_API_KEY from environment
    instructions = (
        "You are a resume file assistant. Use the provided tools for filesystem operations; "
        "never claim you read or wrote a file unless a tool result confirms it. "
        "For requests about all resumes, first list the requested directory and then read relevant files. "
        "For finding a keyword across a folder, list files and search each supported resume file. "
        "For a summary-file request, read the source resume, write a concise factual summary to output/<source-stem>_summary.txt, "
        "and report the output path. Do not invent candidate details. Use relative paths from the project directory when suitable. "
        "Ask for clarification if the target folder or file is genuinely ambiguous."
    )
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=query,
        tools=TOOLS,
    )

    # Tool calls may be returned over multiple rounds; feed each result back to the model.
    for _ in range(8):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return response.output_text or "No text response returned."
        outputs = []
        for call in calls:
            name = call.name
            try:
                args = json.loads(call.arguments)
                if name not in FUNCTIONS:
                    payload = {"success": False, "error": f"Unknown tool: {name}"}
                else:
                    payload = FUNCTIONS[name](**args)
            except Exception as exc:
                payload = {"success": False, "error": f"{type(exc).__name__}: {exc}"}
            outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(payload, ensure_ascii=False),
            })
        response = client.responses.create(
            model=MODEL,
            instructions=instructions,
            input=outputs,
            previous_response_id=response.id,
            tools=TOOLS,
        )
    return "Stopped after 8 tool rounds to avoid an infinite loop."


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("What would you like me to do with the resume files? ").strip()
    if not user_query:
        raise SystemExit("Please enter a request.")
    print(run_assistant(user_query))
