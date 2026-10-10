# AI Engineer Proyek 1

A streaming data-analysis agent that uses a language model hosted through
[OpenRouter](https://openrouter.ai/) to analyze CSV files. The agent exposes a
pandas-based CSV analysis tool and is available through both a command-line
example and a FastAPI Server-Sent Events (SSE) endpoint.

## How it works

1. `agent_core.py` configures LangChain's `ChatOpenRouter` client and the
   `analyze_csv` tool.
2. The model decides whether to call the tool based on the user's prompt.
3. Tool calls and results are added to the message history using LangChain's
   tool-message protocol.
4. The agent continues until the model returns a final answer or reaches the
   maximum number of iterations.
5. `main.py` exposes each token and tool event as an SSE message.

## Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- An [OpenRouter API key](https://openrouter.ai/keys)

## Set up

From the repository root, install the project and its locked dependencies:

```bash
uv sync
```

Create a `.env` file in the repository root and add your API key:

```dotenv
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
AGENT_MODEL=openrouter/free
```

`AGENT_MODEL` is optional and defaults to `openrouter/free`. Do not commit
`.env` or share your API key.

## Run

### Command-line example

Run the fixed CSV analysis example from the repository root:

```bash
uv run python -m ai_engineer_proyek1.agent_analyst
```

The example expects `data/transaksi_pengadaan.csv` to exist at that relative
path. It prints tool calls, tool results, and the streamed final response.

### FastAPI streaming service

Start the development server:

```bash
uv run uvicorn ai_engineer_proyek1.main:app --reload
```

Send a request with `curl`. The `-N` option disables response buffering so
that events appear as soon as they are emitted:

```bash
curl -N -X POST http://127.0.0.1:8000/agent/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"Analyze the CSV file at data/transaksi_pengadaan.csv"}'
```

The stream can contain the following named events:

- `tool_call`: the tool selected by the model and its arguments.
- `tool_result`: the result returned by the tool.
- `token`: a piece of the model's streamed response.
- `done`: the agent completed successfully.
- `error`: the agent or model returned an error.

Example event sequence:

```text
event: tool_call
data: {"name": "analyze_csv", "args": {"file_path": "data/transaksi_pengadaan.csv"}}

event: token
data: {"content": "The CSV contains..."}

event: done
data: {"iterations": 2}
```

Interactive API documentation is available at
`http://127.0.0.1:8000/docs` while the server is running.

## Test

Run the offline unit tests (no OpenRouter request is made):

```bash
uv run python -m unittest discover -s tests -v
```

## Commit documentation standard

This repository treats commits as durable development context. Every regular
commit must explain why the change exists, what changed, and how it was
verified. Set up the local template and validation hook with:

```bash
./scripts/apply-git-standards.sh .
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow and
[`docs/commit-convention.md`](docs/commit-convention.md) for the complete
specification and examples. The
[`start-to-end commit workflow`](docs/commit-workflow.md) includes setup,
recovery, CI, and Mermaid diagrams.

## Build

Build a distributable package with:

```bash
uv build
```

The `ai-engineer-proyek1` console command still runs the package starter
greeting. Use the module or Uvicorn commands above to run the agent.

## References

- [LangChain ChatOpenRouter integration](https://docs.langchain.com/oss/python/integrations/chat/openrouter)
- [OpenRouter API quickstart](https://openrouter.ai/docs/quickstart)
