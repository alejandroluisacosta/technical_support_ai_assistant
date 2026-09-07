# Support ticket analyzer

CLI that reads a support ticket file and returns a structured JSON analysis for a Support Engineer: summary, classification, priority, confirmed vs unknown facts, questions for the customer, and a draft reply.

It does not invent technical details. Troubleshooting steps and escalation are placeholders until the tool can use product documentation. See `DECISIONS.md`.

## Architecture

```
Ticket file
    → prompt + JSON schema
    → Hugging Face chat completion
    → structured JSON
    → placeholder fields overwritten in code
    → schema validation
    → CLI output
```

The system prompt lives in `prompts/ticket_analysis.md`. At runtime the CLI injects `schema/analysis.schema.json`. The ticket is the user message.

Fact slots (`environment`, `application`, `error_messages`, `object_ids`) are `confirmed` only if the ticket states them; otherwise `unknown`. Classification and priority are judgments from those facts and gaps.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `HF_TOKEN` in `.env`. Do not commit that file. Optional: `HF_MODEL` (default `moonshotai/Kimi-K2-Instruct-0905:novita`).

## How to run

```bash
python src/analyzer.py path/to/ticket.txt
```

### Example

```bash
python src/analyzer.py examples/northstar-manufacturing/ticket.txt
```

Sample tickets and outputs:

- `examples/northstar-manufacturing/` — production submit failure (Bug / High)
- `examples/meridian-supplies/` — Vendor Portal how-to (User question / Medium)

To refresh an example output:

```bash
python src/analyzer.py examples/northstar-manufacturing/ticket.txt > examples/northstar-manufacturing/sample-output.json
```

## AI usage

I used Cursor, an AI-based Intergrated Development Environment (very similar to VS Code) and mainly used model Grok 4.6 to build the whole project. Cursor has "Ask," "Plan" and "Agent" modes, but I limited myself to only "Ask" and "Agent" as the requested features were mostly straightforward. Additionally, I discussed this with ChatGPT while in the gym before the implementation just to better understand the exercise and define what should be delivered. No further tools were needed.

Independent decisions and rejected approaches (no assumed facts; no invented troubleshooting or escalation) are in `DECISIONS.md`.
