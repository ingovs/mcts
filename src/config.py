"""
Configuration settings for Chess MCTS.
Modify these values to customize the search behavior.
"""

from dataclasses import dataclass


@dataclass
class SearchConfig:
    """
    Configuration for MCTS search parameters.

    Adjust these values to control the search behavior:
    - Higher depth = more thorough evaluation but slower
    - More simulations = better accuracy but slower
    """

    # === MAIN PARAMETERS TO ADJUST ===

    # Maximum depth for game simulation (moves per side)
    # Example: depth=5 means simulate up to 5 moves for white + 5 moves for black
    MAX_SIMULATION_DEPTH: int = 5

    # === SEARCH CONTROL ===

    # Number of simulations to run (more = better but slower)
    NUM_SIMULATIONS: int = 1000

    # === ADVANCED PARAMETERS ===

    # UCB1 exploration constant (higher = more exploration vs exploitation)
    # 1.414 (sqrt(2)) is the theoretical optimum
    EXPLORATION_CONSTANT: float = 1.414

    # Whether to use progressive widening (gradually increase breadth)
    USE_PROGRESSIVE_WIDENING: bool = False

    # Whether to shuffle legal moves for randomization
    RANDOMIZE_MOVE_ORDER: bool = True


# === PRESET CONFIGURATIONS ===

# Fast search for quick decisions
FAST_CONFIG = SearchConfig(
    MAX_SIMULATION_DEPTH=3,
    NUM_SIMULATIONS=2_000,
)

# Balanced search for normal play
BALANCED_CONFIG = SearchConfig(
    MAX_SIMULATION_DEPTH=5,
    NUM_SIMULATIONS=3_000,
)

# Deep search for critical positions
DEEP_CONFIG = SearchConfig(
    MAX_SIMULATION_DEPTH=7,
    NUM_SIMULATIONS=5_000,
)

# Tournament strength search
TOURNAMENT_CONFIG = SearchConfig(
    MAX_SIMULATION_DEPTH=8,
    NUM_SIMULATIONS=10_000,
)

# AlphaZero search
# NOTE: "During training, each MCTS used 800 simulations per move" - AlphaZero paper
ALPHAZERO_CONFIG = SearchConfig(
    MAX_SIMULATION_DEPTH=20,
    NUM_SIMULATIONS=800,
)


def get_config_by_strength(strength: str) -> SearchConfig:
    """
    Get a preset configuration by strength level.

    Args:
        strength: One of 'fast', 'balanced', 'deep', 'tournament'

    Returns:
        SearchConfig object
    """
    configs = {
        'fast': FAST_CONFIG,
        'balanced': BALANCED_CONFIG,
        'deep': DEEP_CONFIG,
        'tournament': TOURNAMENT_CONFIG,
        'alphazero': ALPHAZERO_CONFIG,
    }

    return configs.get(strength.lower(), BALANCED_CONFIG)


def create_custom_config(depth: int, simulations: int = 1000) -> SearchConfig:
    """
    Create a custom configuration with specified parameters.

    Args:
        depth: Maximum simulation depth (moves per side)
        simulations: Number of simulations to run

    Returns:
        SearchConfig object
    """
    return SearchConfig(
        MAX_SIMULATION_DEPTH=depth,
        NUM_SIMULATIONS=simulations,
    )