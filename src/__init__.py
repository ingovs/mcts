"""
Monte Carlo Tree Search for Chess

A configurable implementation of MCTS with adjustable depth and breadth parameters.
"""

from .mcts_chess import ChessMCTS, MCTSConfig, MCTSNode

__version__ = "1.0.0"
__all__ = [
    "ChessMCTS",
    "MCTSConfig",
    "MCTSNode",
]
