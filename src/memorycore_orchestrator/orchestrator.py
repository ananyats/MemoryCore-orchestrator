"""Helper utilities to bootstrap the planning and promotions agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .adk.agents import PlanAndPromotionsOrchestrator as _PlanAndPromotionsOrchestrator
from .adk.runtime import AgentRuntime, LLMClient

PlanAndPromotionsOrchestrator = _PlanAndPromotionsOrchestrator


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator factory."""

    llm_client: LLMClient
    default_temperature: float = 0.2


def build_orchestrator(config: OrchestratorConfig) -> PlanAndPromotionsOrchestrator:
    """Create a :class:`PlanAndPromotionsOrchestrator` bound to the provided LLM."""

    runtime = AgentRuntime(
        llm_client=config.llm_client,
        default_temperature=config.default_temperature,
    )
    return PlanAndPromotionsOrchestrator(runtime)


def run_demo(
    *,
    llm_client: LLMClient,
    objective: str,
    audience: str = "existing customers",
    channel: str = "email",
    tone: str = "enthusiastic",
    time_horizon: str = "two weeks",
    deliverables: Optional[str] = None,
) -> Dict[str, str]:
    """Convenience helper used by the command line interface."""

    orchestrator = build_orchestrator(
        OrchestratorConfig(llm_client=llm_client, default_temperature=0.2)
    )
    return orchestrator.run(
        objective=objective,
        audience=audience,
        channel=channel,
        tone=tone,
        time_horizon=time_horizon,
        deliverables=deliverables,
    )


__all__ = [
    "OrchestratorConfig",
    "PlanAndPromotionsOrchestrator",
    "build_orchestrator",
    "run_demo",
]
