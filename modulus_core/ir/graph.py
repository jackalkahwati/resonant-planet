from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import hashlib


@dataclass
class Tensor:
    name: str
    shape: Tuple[int, ...]
    dtype: str = "float64"
    location: str = "auto"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_signature(self) -> str:
        return f"{self.name}:{self.dtype}:{','.join(map(str, self.shape))}:{self.location}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "shape": list(self.shape),
            "dtype": self.dtype,
            "location": self.location,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tensor":
        return cls(
            name=data["name"],
            shape=tuple(data.get("shape", [])),
            dtype=data.get("dtype", "float64"),
            location=data.get("location", "auto"),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class Node:
    op_type: str
    inputs: List[str]
    outputs: List[str]
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_signature(self) -> str:
        attrs = ",".join(f"{k}={self.attributes[k]}" for k in sorted(self.attributes))
        return f"{self.op_type}|inputs={','.join(self.inputs)}|outputs={','.join(self.outputs)}|attrs={attrs}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op_type": self.op_type,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "attributes": self.attributes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        return cls(
            op_type=data["op_type"],
            inputs=list(data.get("inputs", [])),
            outputs=list(data.get("outputs", [])),
            attributes=dict(data.get("attributes", {})),
        )


@dataclass
class Graph:
    name: str
    inputs: List[Tensor]
    outputs: List[Tensor]
    nodes: List[Node]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def find_tensor(self, name: str) -> Optional[Tensor]:
        tensor_map = {tensor.name: tensor for tensor in self.inputs + self.outputs}
        tensor_map.update({tensor.name: tensor for tensor in self.metadata.get("intermediates", [])})
        return tensor_map.get(name)

    def add_intermediate(self, tensor: Tensor) -> None:
        intermediates: List[Tensor] = self.metadata.setdefault("intermediates", [])
        intermediates.append(tensor)

    def signature(self) -> str:
        tensor_signatures = [tensor.to_signature() for tensor in self.inputs + self.outputs]
        intermediates = self.metadata.get("intermediates", [])
        tensor_signatures.extend(tensor.to_signature() for tensor in intermediates)
        node_signatures = [node.to_signature() for node in self.nodes]
        meta_items = sorted((k, self.metadata[k]) for k in self.metadata if k != "intermediates")
        meta_signature = ",".join(f"{k}={v}" for k, v in meta_items)
        payload = "|".join(tensor_signatures + node_signatures + [meta_signature])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inputs": [tensor.to_dict() for tensor in self.inputs],
            "outputs": [tensor.to_dict() for tensor in self.outputs],
            "nodes": [node.to_dict() for node in self.nodes],
            "metadata": {
                **{k: v for k, v in self.metadata.items() if k != "intermediates"},
                "intermediates": [tensor.to_dict() for tensor in self.metadata.get("intermediates", [])],
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        metadata = dict(data.get("metadata", {}))
        intermediates_data = metadata.pop("intermediates", [])
        graph = cls(
            name=data.get("name", "graph"),
            inputs=[Tensor.from_dict(item) for item in data.get("inputs", [])],
            outputs=[Tensor.from_dict(item) for item in data.get("outputs", [])],
            nodes=[Node.from_dict(item) for item in data.get("nodes", [])],
            metadata=metadata,
        )
        for tensor_dict in intermediates_data:
            graph.add_intermediate(Tensor.from_dict(tensor_dict))
        return graph
