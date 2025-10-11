"""
Configuration settings for Chess MCTS.

This module defines configuration classes and preset configurations for the
Monte Carlo Tree Search chess engine. It provides an easy interface for
adjusting search parameters without modifying the core MCTS implementation.

The module includes:
- SearchConfig dataclass for parameter specification
- Preset configurations based on research (AlphaZero)
- Factory functions for creating custom configurations
- Documentation of parameter effects on search behavior

Examples
--------
Use AlphaZero configuration:

    >>> from config import ALPHAZERO_CONFIG
    >>> config = ALPHAZERO_CONFIG

Create a custom configuration:

    >>> from config import create_custom_config
    >>> config = create_custom_config(simulations=1500)

Notes
-----
Configuration parameters directly affect the trade-off between search quality
and computation time. Higher simulation counts generally produce stronger play
but require more time per move.
"""

from dataclasses import dataclass


@dataclass
class MCTSConfig:
    """
    Configuration parameters for MCTS search.

    Attributes
    ----------
    max_simulation_depth : int, default=5
        Maximum depth for simulation (number of moves per side).
    num_simulations : int, default=1000
        Number of simulations to run for each node.
    exploration_constant : float, default=1.414
        UCB1 exploration parameter (sqrt(2) is theoretical optimum).
    """
    # === SEARCH CONTROL ===

    # Number of simulations to run (more = better but slower)
    num_simulations: int = 800  # AlphaZero uses 800 simulations per move

    # === ADVANCED PARAMETERS ===

    # UCB1 exploration constant (higher = more exploration vs exploitation)
    # 1.414 (sqrt(2)) is the theoretical optimum
    exploration_constant: float = 1.414


# AlphaZero search configuration
# NOTE: "During training, each MCTS used 800 simulations per move" - AlphaZero paper
ALPHAZERO_CONFIG = MCTSConfig(
    num_simulations=800,
)


def create_custom_config(simulations: int = 800) -> MCTSConfig:
    """
    Create a custom configuration with specified parameters.

    Parameters
    ----------
    simulations : int, default=1000
        Number of simulations to run per move. Higher values provide
        better move quality but take longer to compute.

    Returns
    -------
    SearchConfig
        A new SearchConfig instance with the specified simulation count
        and default values for other parameters.
    """
    return MCTSConfig(
        num_simulations=simulations,
    )
