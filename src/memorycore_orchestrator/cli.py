"""Command line interface for running the sample orchestrator."""
from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

from .adk.runtime import OpenAIClient
from .orchestrator import run_demo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the planning and promotions agent demo using the ADK runtime.",
    )
    parser.add_argument("objective", help="Business objective the planner should tackle.")
    parser.add_argument(
        "--audience",
        default="existing customers",
        help="Audience to target with the promotional copy.",
    )
    parser.add_argument(
        "--channel",
        default="email",
        help="Channel used for the promotional message (email, social, etc.).",
    )
    parser.add_argument(
        "--tone",
        default="enthusiastic",
        help="Tone for the promotional message (enthusiastic, professional, etc.).",
    )
    parser.add_argument(
        "--time-horizon",
        default="two weeks",
        help="Planning horizon communicated to the planning agent.",
    )
    parser.add_argument(
        "--deliverables",
        default=None,
        help="Optional deliverables the plan must include.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Base temperature forwarded to the runtime.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the orchestrator output as JSON instead of formatted text.",
    )
    return parser.parse_args()


def main() -> None:  # pragma: no cover - exercised via CLI
    args = parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY must be set in the environment to call the OpenAI Responses API."
        )

    client = OpenAIClient()
    results: Dict[str, Any] = run_demo(
        llm_client=client,
        objective=args.objective,
        audience=args.audience,
        channel=args.channel,
        tone=args.tone,
        time_horizon=args.time_horizon,
        deliverables=args.deliverables,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=== Plan ===")
        print(results["plan"].strip())
        print("\n=== Promotion ===")
        print(results["promotion"].strip())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
