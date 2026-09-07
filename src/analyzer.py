#!/usr/bin/env python3
"""Analyze a support ticket and print structured JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "ticket_analysis.md"
SCHEMA_PATH = ROOT / "schema" / "analysis.schema.json"
DEFAULT_MODEL = "moonshotai/Kimi-K2-Instruct-0905:novita"

PLACEHOLDER_FIELDS = (
    "troubleshooting_steps",
    "escalate_to_development",
    "escalation_reason",
)


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_system_prompt(schema_text: str) -> str:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    start = text.find("```")
    end = text.rfind("```")
    if start == -1 or end <= start:
        raise SystemExit("Could not find the prompt fence in prompts/ticket_analysis.md")
    prompt = text[start + 3 : end].strip()
    if "{schema}" not in prompt:
        raise SystemExit("Prompt is missing the {schema} placeholder")
    return prompt.replace("{schema}", schema_text)


def read_ticket(path: str) -> str:
    if path == "-":
        ticket = sys.stdin.read()
    else:
        ticket = Path(path).read_text(encoding="utf-8")
    ticket = ticket.strip()
    if not ticket:
        raise SystemExit("Ticket is empty")
    return ticket


def strip_json_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1]
        if stripped.endswith("```"):
            stripped = stripped[: stripped.rfind("```")]
    return stripped.strip()


def apply_placeholders(analysis: dict, schema: dict) -> dict:
    for field in PLACEHOLDER_FIELDS:
        analysis[field] = schema["properties"][field]["const"]
    return analysis


def call_model(system_prompt: str, ticket: str) -> str:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN is not set. Copy .env.example to .env and add your Hugging Face token."
        )
    client = InferenceClient(token=token)
    model = os.environ.get("HF_MODEL", DEFAULT_MODEL)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ticket},
        ],
        temperature=0,
        max_tokens=2048,
    )
    content = response.choices[0].message.content
    if not content:
        raise SystemExit("The model returned an empty response")
    return content


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a support ticket and print structured JSON.",
        epilog="Reads HF_TOKEN and optional HF_MODEL from the environment or .env.",
    )
    parser.add_argument(
        "ticket",
        nargs="?",
        default="-",
        help="Path to a ticket file, or - for stdin (default)",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv(ROOT / ".env")
    args = parse_args()
    schema = load_schema()
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
    system_prompt = load_system_prompt(schema_text)
    ticket = read_ticket(args.ticket)

    raw = call_model(system_prompt, ticket)
    try:
        analysis = json.loads(strip_json_fences(raw))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Model output is not valid JSON: {exc}") from exc

    if not isinstance(analysis, dict):
        raise SystemExit("Model output must be a JSON object")

    analysis = apply_placeholders(analysis, schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(analysis), key=lambda e: e.path)
    if errors:
        details = "\n".join(f"- {error.json_path}: {error.message}" for error in errors)
        raise SystemExit(f"Analysis does not match the schema:\n{details}")

    json.dump(analysis, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
