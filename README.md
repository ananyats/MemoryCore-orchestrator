# MemoryCore-orchestrator

MemoryCore-orchestrator explores how the OpenAI Agent Development Kit (ADK) can be
used to stitch together multiple lightweight agents.  The example included in this
repository focuses on two cooperating agents:

- **Planning agent** – produces a concise project plan with milestones and success
  metrics.
- **Promotions agent** – turns the generated plan into promotional copy aimed at a
  configurable audience and channel.

The repository provides a small ADK-inspired runtime implemented in pure Python so
that you can experiment with orchestration concepts locally without the full
OpenAI-hosted stack.  When you are ready to connect to real models, install the
[`openai`](https://pypi.org/project/openai/) package and export your
`OPENAI_API_KEY`.

## Installation

```bash
pip install -e .[dev]
```

The optional `dev` extras include `pytest` which is used to exercise the stubbed LLM
client inside the unit tests.

## Usage

Once the dependencies are installed and an API key is available you can run the CLI
entry point to obtain both the plan and the promotional message:

```bash
export OPENAI_API_KEY=your_key_here
python -m memorycore_orchestrator.cli "Launch a loyalty program for premium users" \
  --audience "premium customers" --channel "email" --tone "professional"
```

For testing or offline experimentation you can create your own implementation of the
`LLMClient` protocol and pass it to `memorycore_orchestrator.run_demo`.

## Running tests

```bash
pytest
```
