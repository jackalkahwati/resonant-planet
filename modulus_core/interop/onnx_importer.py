"""ONNX model importer for Modulus."""
from __future__ import annotations

from typing import Dict, List, Optional, Any
import numpy as np

try:
    import onnx
    from onnx import numpy_helper
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

from ..ir import Graph, Node, Tensor


class ONNXImporter:
    """Import ONNX models into Modulus IR."""

    SUPPORTED_OPS = {
        "MatMul": "dense_matmul",
        "Gemm": "dense_matmul",
        "Conv": "conv2d",
        "Add": "add",
        "Mul": "mul",
        "Relu": "relu",
        "MaxPool": "max_pool",
        "GlobalAveragePool": "global_avg_pool",
        "Reshape": "reshape",
        "Flatten": "flatten",
        "Softmax": "softmax",
        "ReduceSum": "reduction_sum",
    }

    def __init__(self) -> None:
        if not ONNX_AVAILABLE:
            raise ImportError("ONNX is not installed. Install with: pip install onnx")
        self.tensor_map: Dict[str, Tensor] = {}
        self.nodes: List[Node] = []

    def import_model(self, onnx_path: str) -> Graph:
        """
        Import an ONNX model file into Modulus IR.
        
        Args:
            onnx_path: Path to ONNX model file
            
        Returns:
            Modulus Graph representation
        """
        model = onnx.load(onnx_path)
        return self.import_from_proto(model)

    def import_from_proto(self, model: Any) -> Graph:
        """
        Import from an ONNX ModelProto.
        
        Args:
            model: ONNX ModelProto object
            
        Returns:
            Modulus Graph representation
        """
        graph_proto = model.graph

        # Import initializers (weights/constants)
        for init in graph_proto.initializer:
            tensor_data = numpy_helper.to_array(init)
            self.tensor_map[init.name] = Tensor(
                name=init.name,
                shape=tuple(tensor_data.shape),
                dtype=str(tensor_data.dtype),
            )

        # Import inputs
        for inp in graph_proto.input:
            if inp.name not in self.tensor_map:
                shape = tuple(
                    dim.dim_value if dim.HasField("dim_value") else -1
                    for dim in inp.type.tensor_type.shape.dim
                )
                self.tensor_map[inp.name] = Tensor(
                    name=inp.name,
                    shape=shape,
                    dtype="float32",
                )

        # Import nodes
        for onnx_node in graph_proto.node:
            self._import_node(onnx_node)

        # Identify outputs
        output_names = [out.name for out in graph_proto.output]

        return Graph(
            nodes=self.nodes,
            inputs=[self.tensor_map[inp.name] for inp in graph_proto.input if inp.name in self.tensor_map],
            outputs=[self.tensor_map[name] for name in output_names if name in self.tensor_map],
        )

    def _import_node(self, onnx_node: Any) -> None:
        """Import a single ONNX node."""
        op_type = onnx_node.op_type

        if op_type not in self.SUPPORTED_OPS:
            print(f"Warning: Unsupported ONNX op '{op_type}', skipping node {onnx_node.name}")
            return

        modulus_op = self.SUPPORTED_OPS[op_type]

        # Map inputs
        input_tensors = [self.tensor_map.get(inp) for inp in onnx_node.input if inp in self.tensor_map]

        # Create output tensors
        output_tensors = []
        for out_name in onnx_node.output:
            if out_name not in self.tensor_map:
                self.tensor_map[out_name] = Tensor(
                    name=out_name,
                    shape=(-1,),  # Shape inference needed
                    dtype="float32",
                )
            output_tensors.append(self.tensor_map[out_name])

        # Extract attributes
        attributes = {}
        for attr in onnx_node.attribute:
            if attr.HasField("i"):
                attributes[attr.name] = attr.i
            elif attr.HasField("f"):
                attributes[attr.name] = attr.f
            elif attr.HasField("s"):
                attributes[attr.name] = attr.s.decode("utf-8")
            elif attr.ints:
                attributes[attr.name] = list(attr.ints)
            elif attr.floats:
                attributes[attr.name] = list(attr.floats)

        node = Node(
            op=modulus_op,
            inputs=input_tensors,
            outputs=output_tensors,
            attributes=attributes,
        )

        self.nodes.append(node)


def onnx_to_modulus_graph(onnx_path: str) -> Graph:
    """
    Convenience function to import ONNX model to Modulus IR.
    
    Args:
        onnx_path: Path to ONNX model file
        
    Returns:
        Modulus Graph
    """
    importer = ONNXImporter()
    return importer.import_model(onnx_path)


