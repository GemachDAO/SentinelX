from __future__ import annotations
from graphviz import Digraph
from .model import ThreatModel, Asset


def render(model: ThreatModel, path: str = "threat_model.svg") -> None:
    dot = Digraph()
    for asset in model.assets:
        dot.node(asset.name)
        for thr in asset.threats:
            dot.edge(asset.name, thr.value)
    dot.render(path, format="svg", cleanup=True)
