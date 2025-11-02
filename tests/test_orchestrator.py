"""Unit tests for the planning and promotions orchestrator."""
from __future__ import annotations

from textwrap import dedent

import pytest

from memorycore_orchestrator.adk.runtime import AgentRuntime, LLMClient
from memorycore_orchestrator.adk.agents import PlanAndPromotionsOrchestrator


class StubLLM(LLMClient):
    """Deterministic LLM client used for tests.

    The implementation records the last prompt and returns a predictable response
    that includes a prefix identifying the agent that invoked it.  This keeps the
    assertions stable without performing any network traffic.
    """

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, prompt: str, *, temperature: float = 0.0) -> str:  # noqa: D401
        self.prompts.append(prompt)
        if "project planner" in prompt:
            return dedent(
                """
                # Plan: Grow Newsletter Subscribers

                1. Run a referral campaign – Track sign ups per referral link.
                2. Launch weekly expert interviews – Monitor open rate and average read time.
                3. Offer a limited-time bonus – Measure conversions from the promotion landing page.
                """
            ).strip()
        if "marketing specialist" in prompt:
            return dedent(
                """
                # Promo: Help Us Grow Together

                Spread the word! Share the newsletter with a friend and enjoy exclusive
                interviews plus a limited-time bonus. Join the campaign today!
                """
            ).strip()
        raise AssertionError("Unexpected prompt dispatched to the stub LLM")


@pytest.fixture()
def orchestrator() -> PlanAndPromotionsOrchestrator:
    runtime = AgentRuntime(llm_client=StubLLM(), default_temperature=0.2)
    return PlanAndPromotionsOrchestrator(runtime)


def test_orchestrator_generates_plan_and_promotion(orchestrator: PlanAndPromotionsOrchestrator) -> None:
    results = orchestrator.run(objective="Grow newsletter subscribers")

    assert "Plan" in results["plan"]
    assert "Promo" in results["promotion"]
    # Ensure the orchestrator stores intermediate state for downstream agents.
    assert orchestrator.runtime.context["latest_plan"] == results["plan"]
    assert orchestrator.runtime.context["latest_promotion"] == results["promotion"]


def test_stub_llm_receives_structured_prompts(orchestrator: PlanAndPromotionsOrchestrator) -> None:
    orchestrator.run(objective="Grow newsletter subscribers", channel="social media")

    prompts = orchestrator.runtime.llm_client.prompts  # type: ignore[attr-defined]
    assert len(prompts) == 2
    assert "Objective" in prompts[0]
    assert "Plan summary" in prompts[1]
    assert "social media" in prompts[1]
