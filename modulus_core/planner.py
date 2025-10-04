from __future__ import annotations

from typing import Dict, Any

from .spec import PatProgram, PlanGraph


class Planner:
    def plan(self, program: PatProgram) -> PlanGraph:
        stages = ["bpr"]
        metadata: Dict[str, Any] = {
            "assumptions": program.spec.metadata.get("assumptions", []),
            "domains": program.spec.metadata.get("domains", []),
        }

        hints = program.spec.metadata.get("solver_hints", {})
        if hints.get("structure") == "circulant":
            stages.append("ntt")
            metadata["solver"] = "ntt"
        elif hints.get("structure") == "sparse":
            stages.append("finite_field_lu")
            metadata["solver"] = "lu"
        elif hints.get("type") == "nonlinear":
            stages.append("newton_symbolic")
            metadata["solver"] = "newton"
        else:
            stages.append("residue_gaussian")
            metadata["solver"] = "gaussian"

        stages.append("crt")
        stages.append("hensel")
        return PlanGraph(stages=stages, metadata=metadata)


def plan(program: PatProgram) -> PlanGraph:
    return Planner().plan(program)

