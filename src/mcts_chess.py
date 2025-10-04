"""
Monte Carlo Tree Search implementation for chess with configurable depth and breadth parameters.
"""

import chess
import random
import math
import time
from typing import List, Optional, Dict, Tuple
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
    # Maximum depth for simulation (number of moves per side)
    max_simulation_depth: int = 5

    # Number of simulations to run for each node
    num_simulations: int = 1000    # UCB1 exploration parameter
    exploration_constant: float = 1.414  # sqrt(2)


class MCTSNode:
    """
    A node in the Monte Carlo Tree Search tree.

    Parameters
    ----------
    board : chess.Board
        The chess position at this node.
    move : chess.Move, optional
        The move that led to this position.
    parent : MCTSNode, optional
        The parent node in the tree.

    Attributes
    ----------
    board : chess.Board
        Copy of the chess position.
    move : chess.Move or None
        The move that led to this position.
    parent : MCTSNode or None
        The parent node.
    children : List[MCTSNode]
        List of child nodes.
    visits : int
        Number of times this node has been visited.
    wins : float
        Cumulative win score for this node.
    legal_moves : List[chess.Move]
        All legal moves from this position.
    unexplored_moves : List[chess.Move]
        Legal moves that haven't been expanded yet.
    """

    def __init__(self, board: chess.Board, move: Optional[chess.Move] = None, parent: Optional['MCTSNode'] = None):
        self.board = board.copy()
        self.move = move  # The move that led to this position
        self.parent = parent
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.wins = 0.0
        self.legal_moves = list(board.legal_moves)
        random.shuffle(self.legal_moves)  # Randomize move order
        self.unexplored_moves = self.legal_moves.copy()

        # Calculate depth from root
        self.depth = 0 if parent is None else parent.depth + 1

    def is_fully_expanded(self) -> bool:
        """
        Check if all legal moves have been explored.

        Returns
        -------
        bool
            True if all legal moves have been expanded, False otherwise.
        """
        return len(self.unexplored_moves) == 0

    def is_terminal(self) -> bool:
        """
        Check if this is a terminal position (game over).

        Returns
        -------
        bool
            True if the game is over at this position, False otherwise.
        """
        return self.board.is_game_over()

    def ucb1_value(self, exploration_constant: float) -> float:
        """
        Calculate UCB1 value for this node.

        The UCB1 formula balances exploitation (win rate) with exploration
        (uncertainty based on visit count).

        Parameters
        ----------
        exploration_constant : float
            The exploration parameter (typically sqrt(2)).

        Returns
        -------
        float
            UCB1 value for node selection. Returns infinity for unvisited nodes.
        """
        # if no children have been visited yet, return infinity to ensure they get explored
        # NOTE: this is kind of a brute-force breadth search, forcing to go through all legal moves,
        # while AlphaZero uses a neural net prior so the tree tends to expand selectively into the
        # most promising variations
        if self.visits == 0:
            return float('inf')

        exploitation = self.wins / self.visits

        # exploration term penalizes frequently visited nodes in order to favor less explored ones
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def select_best_child(self, exploration_constant: float) -> 'MCTSNode':
        """
        Select the child with the highest UCB1 value (Upper Confidence Bound 1 applied to trees).

        Parameters
        ----------
        exploration_constant : float
            The exploration parameter for UCB1 calculation.

        Returns
        -------
        MCTSNode
            The child node with the highest UCB1 value.

        Notes
        -----
        The first component of the formula above corresponds to exploitation; it is high for moves
        with high average win ratio. The second component corresponds to exploration; it is high for
        moves with few simulations.
        """
        return max(self.children, key=lambda child: child.ucb1_value(exploration_constant))

    def expand(self, max_depth: int) -> 'MCTSNode':
        """
        Expand this node by adding a new child.

        Creates a new child node for the next unexplored legal move.
        All legal moves are considered, but expansion stops at max_depth.

        Parameters
        ----------
        max_depth : int
            Maximum depth for expansion (moves from root).

        Returns
        -------
        MCTSNode
            The newly created child node, or self if no moves to expand
            or max depth reached.
        """
        if not self.unexplored_moves:
            return self

        # Don't expand beyond max depth
        if self.depth >= max_depth:
            return self

        # Take the next unexplored move (all legal moves are considered)
        move = self.unexplored_moves.pop(0)  # Create new board with the move applied
        new_board = self.board.copy()
        new_board.push(move)

        # Create new child node
        child = MCTSNode(board=new_board, move=move, parent=self)
        self.children.append(child)

        return child

    def simulate(self, board_turn: bool, child_board: chess.Board) -> float:
        """
        Run a random simulation from this position.

        Uses the chess library's built-in draw detection for proper rule enforcement.
        Plays random moves until the game ends naturally.

        Parameters
        ----------
        board_turn : bool
            The turn of the player to evaluate (True for White, False for Black).
        child_board : chess.Board
            The board position to simulate from.

        Returns
        -------
        float
            Evaluation score from current player's perspective (0.0 to 1.0).
            1.0 means current player wins, 0.0 means current player loses,
            0.5 indicates a draw or neutral position.
        """
        simulation_board = child_board.copy()

        # Play until game ends - the chess library handles all draw conditions automatically
        while not simulation_board.is_game_over():
            # The chess library's is_game_over() method automatically checks:
            # - Checkmate and stalemate
            # - Fivefold repetition (via is_fivefold_repetition)
            # - 75-move rule (via is_seventyfive_moves)
            # - Insufficient material

            legal_moves = list(simulation_board.legal_moves)
            if not legal_moves:
                break

            # Choose random move
            move = random.choice(legal_moves)
            simulation_board.push(move)

        # Evaluate the final position
        return self._evaluate_position(board_turn, simulation_board)

    def _evaluate_position(self, board_turn: bool, simulation_board: chess.Board) -> float:
        """
        Evaluate the final position and return a score from current player's perspective.

        Parameters
        ----------
        board_turn : bool
            The turn of the player to evaluate (True for White, False for Black).
        simulation_board : chess.Board
            The board position to evaluate.

        Returns
        -------
        float
            Score from 0.0 to 1.0 where:
            - 1.0: Current player wins
            - 0.0: Current player loses
            - 0.5: Draw or neutral position
        """
        if simulation_board.is_checkmate():
            # If it's checkmate, the player to move (in the simulated game) has lost
            return 0.0 if simulation_board.turn == board_turn else 1.0
        elif simulation_board.is_stalemate() or simulation_board.is_insufficient_material():
            return 0.5  # Draw
        else:
            return 0.5  # Neutral for unfinished games

    def backpropagate(self, result: float):
        """
        Backpropagate the simulation result up the tree.

        Updates visit count and win score for this node and all ancestors.
        The result is flipped for each level since players alternate.

        Parameters
        ----------
        result : float
            Simulation result from current node's perspective (0.0 to 1.0).
        """
        self.visits += 1
        self.wins += result

        if self.parent:
            # Flip the result for the parent (opponent's perspective)
            self.parent.backpropagate(result=1.0 - result)


class ChessMCTS:
    """
    Monte Carlo Tree Search for chess.

    Implements the MCTS algorithm with UCB1 selection, random simulation,
    and configurable search parameters.

    Parameters
    ----------
    config : MCTSConfig, optional
        Configuration parameters for the search. If None, default config is used.

    Attributes
    ----------
    config : MCTSConfig
        Configuration parameters for the search.
    root : MCTSNode or None
        Root node of the current search tree.
    """

    def __init__(self, config: MCTSConfig = None):
        """
        Initialize MCTS engine.

        Parameters
        ----------
        config : MCTSConfig, optional
            Configuration parameters. If None, default config is used.
        """
        self.config = config or MCTSConfig()
        self.root: Optional[MCTSNode] = None

    def search(self, board: chess.Board) -> Tuple[chess.Move, Dict]:
        """
        Perform MCTS search and return the best move along with search statistics.

        Runs the four phases of MCTS (Selection, Expansion, Simulation, Backpropagation)
        for the configured number of iterations.

        Parameters
        ----------
        board : chess.Board
            Current chess position to search from.

        Returns
        -------
        tuple of (chess.Move, dict)
            Best move found and dictionary containing search statistics:
            - 'simulations_run': Number of simulations completed
            - 'total_time': Total search time in seconds
            - 'simulations_per_second': Search speed
            - 'tree_size': Total nodes in search tree
            - 'root_visits': Number of visits to root node
            - 'best_move_visits': Visits to the selected move
            - 'children_count': Number of children expanded from root
        """
        self.root = MCTSNode(board)
        start_time = time.time()
        simulations_run = 0

        print("Starting MCTS search with config:")
        print(f"  Max simulation depth: {self.config.max_simulation_depth} moves per side")
        print("  Considering ALL legal moves")
        print(f"  Target simulations: {self.config.num_simulations}")
        print()

        while simulations_run < self.config.num_simulations:

            # Selection: traverse tree using UCB1
            # NOTE: at the first move, no children exist yet (Expansion will handle this)
            node = self._select(self.root)

            # Expansion: add a new child if possible (respect max depth)
            # node returned here is the child node
            child_node = node.expand(self.config.max_simulation_depth)

            # Simulation: run random playout
            result = child_node.simulate(board_turn=board.turn, child_board=child_node.board)

            # Backpropagation: update statistics
            child_node.backpropagate(result)

            simulations_run += 1

            # Print progress every 100 simulations
            if simulations_run % 100 == 0:
                elapsed = time.time() - start_time
                print(f"Simulations: {simulations_run}, Elapsed: {elapsed:.2f}s")

        # Select best move based on visit count (most robust)
        best_child = max(self.root.children, key=lambda child: child.visits)
        best_move = best_child.move

        # Calculate the win rate for the selected move
        selected_move_win_rate = best_child.wins / best_child.visits

        # Gather statistics
        total_time = time.time() - start_time
        stats = {
            'simulations_run': simulations_run,
            'total_time': total_time,
            'simulations_per_second': simulations_run / total_time if total_time > 0 else 0,
            'tree_size': self._count_nodes(self.root),
            'root_visits': self.root.visits,
            'best_move_visits': max((child.visits for child in self.root.children), default=0),
            'children_count': len(self.root.children),
            'selected_move_win_rate': selected_move_win_rate
        }

        return best_move, stats

    def _select(self, node: MCTSNode) -> MCTSNode:
        """
        Select a leaf node using UCB1.

        Traverses the tree from the given node down to a leaf,
        selecting children with highest UCB1 values.

        Parameters
        ----------
        node : MCTSNode
            Starting node for selection.

        Returns
        -------
        MCTSNode
            A leaf node (either terminal or not fully expanded).
        """
        # NOTE: this will go down until a leaf node is found. After that, Expansion will handle adding a new child.
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.select_best_child(self.config.exploration_constant)
        return node

    def _count_nodes(self, node: MCTSNode) -> int:
        """
        Count total nodes in the tree.

        Recursively counts all nodes in the subtree rooted at the given node.

        Parameters
        ----------
        node : MCTSNode
            Root node of the subtree to count.

        Returns
        -------
        int
            Total number of nodes in the subtree.
        """
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count

    def get_principal_variation(self, depth: int = 5) -> List[chess.Move]:
        """
        Get the principal variation (most visited path) from the root.

        Follows the path of most visited children to construct the
        principal variation line.

        Parameters
        ----------
        depth : int, default=5
            Maximum depth of variation to return.

        Returns
        -------
        List[chess.Move]
            Sequence of moves representing the principal variation.
        """
        pv = []
        node = self.root

        for _ in range(depth):
            if not node.children:
                break

            # Select most visited child
            best_child = max(node.children, key=lambda child: child.visits)
            pv.append(best_child.move)
            node = best_child

        return pv

    def print_move_analysis(self, top_moves: int = 5):
        """
        Print analysis of top moves considered.

        Displays a table showing the most visited moves with their
        statistics including visit count, win rate, and UCB1 value.

        Parameters
        ----------
        top_moves : int, default=5
            Number of top moves to display in the analysis.
        """
        if not self.root or not self.root.children:
            print("No moves analyzed yet.")
            return

        print(f"\nTop {top_moves} moves analyzed:")
        print("Move                 Visits    Win Rate    UCB1")
        print("-" * 50)

        # Sort children by visit count
        sorted_children = sorted(self.root.children, key=lambda child: child.visits, reverse=True)

        for i, child in enumerate(sorted_children[:top_moves]):
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            ucb1 = child.ucb1_value(self.config.exploration_constant)
            ucb1_str = f"{ucb1:.3f}" if ucb1 != float('inf') else "inf"

            print(f"{str(child.move):<15} {child.visits:>8} {win_rate:>10.3f} {ucb1_str:>8}")
