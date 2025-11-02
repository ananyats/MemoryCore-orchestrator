"""Agent implementations powered by the local ADK runtime."""
from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import Dict, Optional

from .runtime import AgentRuntime


@dataclass
class BaseAgent:
    """Base class shared by all lightweight agents.

    Agents provide a name, a short description, and the prompt template that is
    used to steer the LLM.  Sub-classes only need to implement the
    :meth:`build_prompt` method which takes arbitrary keyword arguments and
    returns a formatted prompt.
    """

    runtime: AgentRuntime
    name: str
    description: str
    temperature: float = 0.0

    def build_prompt(self, **kwargs: str) -> str:
        raise NotImplementedError

    def run(self, **kwargs: str) -> str:
        prompt = self.build_prompt(**kwargs)
        return self.runtime.complete(prompt, temperature=self.temperature)


class PlanningAgent(BaseAgent):
    """Agent that produces a simple execution plan."""

    def build_prompt(
        self,
        *,
        objective: str,
        time_horizon: str = "two weeks",
        deliverables: Optional[str] = None,
    ) -> str:
        deliverables_text = (
            f"Key deliverables to highlight: {deliverables}." if deliverables else ""
        )
        template = dedent(
            f"""
            You are {self.name}, a meticulous project planner. Your task is to produce
            a concise execution plan for the objective below. The plan must contain a
            short headline followed by three to five numbered steps. Each step should
            include a success metric.

            Objective: {{objective}}
            Planning horizon: {{time_horizon}}
            {deliverables_text}

            Return the plan as markdown.
            """
        ).strip()
        return template.replace("{objective}", objective).replace(
            "{time_horizon}", time_horizon
        )


class PromotionsAgent(BaseAgent):
    """Agent that generates promotional messaging."""

    def build_prompt(
        self,
        *,
        plan_summary: str,
        audience: str = "existing customers",
        channel: str = "email",
        tone: str = "enthusiastic",
    ) -> str:
        template = dedent(
            f"""
            You are {self.name}, a marketing specialist tasked with creating promotional
            copy. Craft a short {channel} announcement aimed at {{audience}} with a
            {tone} tone. The message must reference the plan summary below and include a
            clear call to action.

            Plan summary:
            {{plan_summary}}

            Return the announcement as markdown with a title and a short body paragraph.
            """
        ).strip()
        prompt = template.replace("{audience}", audience).replace("{tone}", tone)
        prompt = prompt.replace("{channel}", channel)
        return prompt.replace("{plan_summary}", plan_summary)


class PlanAndPromotionsOrchestrator:
    """High level orchestrator wiring the planning and promotions agents together."""

    def __init__(self, runtime: AgentRuntime):
        self.runtime = runtime
        self.planner = PlanningAgent(
            runtime,
            name="PlanSmith",
            description="Creates milestone driven execution plans.",
            temperature=0.1,
        )
        self.promoter = PromotionsAgent(
            runtime,
            name="PromoSpark",
            description="Produces promotional copy referencing a provided plan.",
            temperature=0.4,
        )

    def run(
        self,
        *,
        objective: str,
        audience: str = "existing customers",
        channel: str = "email",
        tone: str = "enthusiastic",
        time_horizon: str = "two weeks",
        deliverables: Optional[str] = None,
    ) -> Dict[str, str]:
        """Execute both agents and return their outputs."""

        plan = self.planner.run(
            objective=objective,
            time_horizon=time_horizon,
            deliverables=deliverables or "",
        )
        self.runtime.context["latest_plan"] = plan

        promotion = self.promoter.run(
            plan_summary=plan,
            audience=audience,
            channel=channel,
            tone=tone,
        )
        self.runtime.context["latest_promotion"] = promotion

        return {"plan": plan, "promotion": promotion}


__all__ = [
    "BaseAgent",
    "PlanningAgent",
    "PromotionsAgent",
    "PlanAndPromotionsOrchestrator",
]
