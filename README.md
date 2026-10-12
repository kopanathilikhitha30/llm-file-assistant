# LLM File Assistant

A small Python project demonstrating LLM tool/function calling for resume file operations.

## Features

- `read_file(filepath)`: extract text and metadata from PDF, TXT, and DOCX.
- `list_files(directory, extension=None)`: list files and metadata, optionally filtering by extension.
- `write_file(filepath, content)`: create parent folders and write UTF-8 text.
- `search_in_file(filepath, keyword)`: case-insensitive search with context snippets.
- `llm_file_assistant.py`: lets an OpenAI model choose and call tools from natural-language requests.

## Requirements

- Python 3.10+
- An OpenAI API key with API access and available credits/billing.

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set the API key

Windows PowerShell (current terminal only):

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="your-api-key"
```

Do not commit your API key to source control.

## Run the assistant

Run commands from the project root:

```bash
python llm_file_assistant.py "Read all resumes in the resumes folder"
python llm_file_assistant.py "Find resumes mentioning Python experience"
python llm_file_assistant.py "Create a summary file for resumes/resume_john_doe.txt"
```

You can also run without a command-line argument and enter a query interactively:

```bash
python llm_file_assistant.py
```

The model may make multiple tool calls. The program executes each requested tool and returns the results to the model for a final natural-language response. Summary files are intended to be written to `output/`.

## Use file tools without an LLM

```python
from fs_tools import read_file, list_files, write_file, search_in_file

print(list_files("resumes", ".txt"))
print(read_file("resumes/resume_john_doe.txt"))
print(search_in_file("resumes/resume_john_doe.txt", "python"))
print(write_file("output/example.txt", "Sample output"))
```

## Example output shape

`read_file` returns a dictionary similar to:

```json
{
  "success": true,
  "content": "Jordan Lee\\nBackend Developer...",
  "metadata": {
    "name": "resume_john_doe.txt",
    "filepath": "/.../resumes/resume_john_doe.txt",
    "extension": ".txt",
    "size_bytes": 240,
    "modified_date": "2026-01-01T12:00:00"
  },
  "character_count": 240
}
```

Exact metadata values depend on the machine and file.

## Notes and limitations

- PDF text extraction works for text-based PDFs. Scanned/image-only PDFs require OCR, which is not included.
- The assistant sends resume text to the configured LLM provider. Use synthetic data for demos and obtain appropriate authorization before processing real resumes.
- Tool schemas use strict JSON schemas. The assistant validates function names and catches tool execution exceptions, but filesystem paths should still be treated as trusted input in a production system. For a public-facing deployment, restrict operations to an approved root directory and add stronger path validation.
- `list_files` lists the immediate directory only (not recursively).
- No API key is required for direct use of `fs_tools.py`; it is required for LLM integration.

## Suggested 2–3 minute demo video

1. **0:00–0:20 — Introduce the project:** explain that the LLM selects tools based on a natural-language request.
2. **0:20–0:55 — List/read resumes:** run `python llm_file_assistant.py "Read all resumes in the resumes folder"`.
3. **0:55–1:35 — Search:** run `python llm_file_assistant.py "Find resumes mentioning Python experience"`. Show the matching files and snippets.
4. **1:35–2:15 — Write a summary:** run `python llm_file_assistant.py "Create a summary file for resumes/resume_john_doe.txt"`, then open the generated file under `output/`.
5. **2:15–2:40 — Explain implementation:** briefly show `TOOLS` in `llm_file_assistant.py` and the four functions in `fs_tools.py`.

## Suggested checks before submission

- Test each function directly with a valid file and a missing file.
- Test keyword matching with different capitalization.
- Test `.pdf`, `.txt`, and `.docx` inputs.
- Confirm `output/` receives the generated summary.
- Record the demo only after setting the API key and confirming the model can call tools.
