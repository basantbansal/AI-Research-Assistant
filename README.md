# AI Research Assistant

A small command-line research assistant that searches Tavily for a user-provided topic, then summarizes the findings using a Groq-powered LLM. It provides a simple conversational CLI and is organized as a compact state-graph-based agent in `agentv1.py`.

## Stack
- Language: Python (3.10+)
- Runtime: CLI script
- Notable libraries: requests, python-dotenv, langchain-core, langchain-groq, langgraph

## Features
- Query the Tavily search API for relevant results and answers
- Produce a concise, user-friendly summary using a Groq chat model
- Small, readable orchestration using a StateGraph with clear steps (research -> summarize)

## Files of interest
- `agentv1.py` — main agent implementation and CLI entrypoint
- `.gitignore`, `LICENSE` — repository metadata

## Quick start
1. Clone the repository:

```bash
git clone https://github.com/basantbansal/AI-Research-Assistant.git
cd AI-Research-Assistant
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.\.venv\Scripts\activate   # Windows (PowerShell)
```

3. Install dependencies:

```bash
pip install requests python-dotenv langchain-core langchain-groq langgraph
```

Note: If you prefer, add a `requirements.txt` with pinned versions and install from it.

## Configuration
The agent reads API keys from a `.env` file in the project root. Create a `.env` with the following keys:

```env
TAVILY_API_KEY=your_tavily_api_key_here
GROQ_API_KEY=your_groq_api_key_here
# Optional: override the Groq model (defaults to llama-3.1-8b-instant)
GROQ_MODEL=llama-3.1-8b-instant
```

The code will raise a clear error if either `TAVILY_API_KEY` or `GROQ_API_KEY` is missing.

## Usage
Run the CLI and type a research topic when prompted:

```bash
python agentv1.py
```

Example session:

```
Research Agent
Type a research topic, or type 'exit' to quit.

You: retrieval-augmented generation

Researching...

Agent:
<summary produced by the Groq model>
```

## How it works (brief)
- `research_topic` (agentv1.py): calls the Tavily Search API to fetch up to 5 results and an optional direct answer.
- `summarize_findings`: assembles the results and sends them as System/Human messages to a Groq Chat model via `langchain_groq`.
- A `StateGraph` (from `langgraph`) composes the two steps in sequence and exposes `run_research(topic)` as the programmatic entrypoint.

This separation keeps the concerns clear: retrieval and summarization are separate nodes, which makes it straightforward to add steps like filtering, citation extraction, or longer-form reporting.

## Development
- Add tests around `research_topic` by mocking the Tavily API responses.
- Consider adding `pyproject.toml` or `requirements.txt` to lock dependencies.
- For faster iteration, inject mocked LLMs or use a small local model when developing.

## Security & Privacy
- Do not commit your `.env` file or API keys to source control.
- The agent forwards retrieved content to the LLM — review and redact any sensitive material before sending.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
