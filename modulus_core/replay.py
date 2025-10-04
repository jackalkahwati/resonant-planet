from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional

from .ir import Graph
from .executor import GraphExecutor, ExecutionContext


class ReplayConfig:
    def __init__(self, seed: int, config_hash: str, graph_dict: Dict[str, Any]) -> None:
        self.seed = seed
        self.config_hash = config_hash
        self.graph_dict = graph_dict

    @classmethod
    def from_file(cls, path: Path) -> "ReplayConfig":
        with open(path, "r") as f:
            data = json.load(f)
        return cls(
            seed=data["seed"],
            config_hash=data["config_hash"],
            graph_dict=data["graph"],
        )

    def to_file(self, path: Path) -> None:
        with open(path, "w") as f:
            json.dump(
                {
                    "seed": self.seed,
                    "config_hash": self.config_hash,
                    "graph": self.graph_dict,
                },
                f,
                indent=2,
            )


def replay_execution(
    config: ReplayConfig,
    executor: GraphExecutor,
    inputs: Optional[Dict[str, Any]] = None,
) -> ExecutionContext:
    graph = Graph.from_dict(config.graph_dict)
    computed_hash = graph.signature()
    if computed_hash != config.config_hash:
        raise ValueError(
            f"Config hash mismatch: expected {config.config_hash}, got {computed_hash}"
        )
    return executor.execute(graph, seed=config.seed, deterministic=True, inputs=inputs)


def save_execution_config(
    graph: Graph,
    seed: int,
    output_path: Path,
) -> None:
    config = ReplayConfig(
        seed=seed,
        config_hash=graph.signature(),
        graph_dict=graph.to_dict(),
    )
    config.to_file(output_path)


