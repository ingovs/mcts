"""
Monte Carlo Tree Search for Chess

A configurable implementation of MCTS with adjustable depth and breadth parameters.
"""

from .mcts_chess import ChessMCTS, MCTSConfig, MCTSNode
from .config import (
    SearchConfig,
    get_config_by_strength,
    create_custom_config,
    FAST_CONFIG,
    BALANCED_CONFIG,
    DEEP_CONFIG,
    TOURNAMENT_CONFIG,
    ALPHAZERO_CONFIG,
)

__version__ = "1.0.0"
__all__ = [
    "ChessMCTS",
    "MCTSConfig",
    "MCTSNode",
    "SearchConfig",
    "get_config_by_strength",
    "create_custom_config",
    "FAST_CONFIG",
    "BALANCED_CONFIG",
    "DEEP_CONFIG",
    "TOURNAMENT_CONFIG",
    "ALPHAZERO_CONFIG",
]