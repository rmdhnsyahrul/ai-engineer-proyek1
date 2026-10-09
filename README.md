# AI Engineer Proyek 1

A prototype data-analysis agent that uses a language model hosted through
[OpenRouter](https://openrouter.ai/) to analyze a CSV file. The agent exposes a
CSV analysis tool that reads a file with pandas and returns descriptive
statistics; the model can call that tool in response to a user request.

The current example analyzes `data/transaksi_pengadaan.csv`. This is a
command-line prototype: a FastAPI service and a configurable interactive
interface are not implemented yet.

## How it works

1. `agent_analyst.py` loads environment variables from `.env`.
2. LangChain's `ChatOpenRouter` client is configured to use the
   `openrouter/free` model.
3. The model receives a request to analyze the example CSV and can call the
   `analyze_csv` tool.
4. The tool reads the CSV with pandas and returns `DataFrame.describe()`
   output. That result is sent back to the model, which prints its final
   response.

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
```

`OPENROUTER_API_BASE` can also be set if you need a custom API endpoint; it is
not required for the default OpenRouter setup. Do not commit `.env` or share
your API key.

## Run

Run the CSV analysis example from the repository root:

```bash
uv run python -m ai_engineer_proyek1.agent_analyst
```

The example expects `data/transaksi_pengadaan.csv` to exist at that relative
path. It prints the model's tool call, the CSV summary returned by the tool,
and the model's final response. The CSV path is currently set in the module;
it is not yet a command-line argument.

## Build

Build a distributable package with:

```bash
uv build
```

The `ai-engineer-proyek1` console command currently runs a starter greeting,
not the analysis agent. Use the module command above to run the prototype.

## References

- [LangChain ChatOpenRouter integration](https://docs.langchain.com/oss/python/integrations/chat/openrouter)
- [OpenRouter API quickstart](https://openrouter.ai/docs/quickstart)
