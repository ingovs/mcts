#!/usr/bin/env python3
"""
Chess MCTS Interactive Runner.

This module provides an easy-to-use interface for running Monte Carlo Tree Search
(MCTS) on chess positions. It includes interactive gameplay modes and configuration
options for testing different MCTS parameters.

The module supports:
- Interactive play against random opponents
- Interactive play between MCTS engines
- Configurable number of simulations
- Real-time estimated win probability tracking after each move
- Move analysis and principal variation display
- Visual win rate evolution charts

Configuration
-------------
Modify the CONFIGURATION SECTION below to customize:
- Number of simulations per move
- Display of detailed analysis

The default configuration uses 800 simulations per move (AlphaZero standard)
with detailed analysis enabled.
"""

# import os
import random
# import sys
from typing import List, Tuple, Optional

import chess

# sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


from src.mcts_chess import ChessMCTS
from src.config import create_custom_config

# ===============================================
# CONFIGURATION SECTION - EDIT THESE VALUES
# ===============================================

# Search parameters
CUSTOM_SIMULATIONS = 800  # Number of simulations to run per move (AlphaZero standard)

# Display options
SHOW_DETAILED_ANALYSIS = True  # Show detailed move analysis and principal variation


def get_human_move(board: chess.Board, player_color_name: str) -> Optional[chess.Move]:
    """
    Get a valid move from human input with command support.

    Handles move input from a human player with support for standard algebraic
    notation (SAN), UCI notation, and special commands like help and moves list.

    Parameters
    ----------
    board : chess.Board
        The current chess board position.
    player_color_name : str
        Name of the player's color for display purposes (e.g., "White", "Black").

    Returns
    -------
    chess.Move or None
        The parsed and validated move, or None if the player quits.

    Raises
    ------
    KeyboardInterrupt
        If the player interrupts with Ctrl+C to end the game.

    Notes
    -----
    Supported move formats:
    - Standard algebraic notation: "e4", "Nf3", "Bxf7+", "O-O", "Qh5#"
    - UCI notation: "e2e4", "g1f3", "e1g1", "h7h8q" (with promotion)

    Supported commands:
    - "help": Show move format examples
    - "moves": Display all legal moves
    - "quit"/"exit": End the game
    """
    while True:
        try:
            move_input = input(f"Your move ({player_color_name}): ").strip()

            # Handle special commands
            if move_input.lower() in ["quit", "exit"]:
                print("Game ended by player.")
                return None

            if move_input.lower() == "help":
                print("\nMove format examples:")
                print("  Standard: e4, Nf3, Bxf7+, O-O, Qh5#")
                print("  UCI: e2e4, g1f3, e1g1, h7h8q (promotion)")
                print("  Commands: help, moves, quit")
                continue

            if move_input.lower() == "moves":
                legal_moves = list(board.legal_moves)
                print(f"\nLegal moves ({len(legal_moves)}):")
                move_strs = [str(move) for move in legal_moves]
                # Print in rows of 8
                for i in range(0, len(move_strs), 8):
                    print("  " + " ".join(move_strs[i : i + 8]))
                continue

            # Try to parse the move
            move = None

            # First try standard algebraic notation
            try:
                move = board.parse_san(move_input)
            except (
                chess.InvalidMoveError,
                chess.IllegalMoveError,
                chess.AmbiguousMoveError,
            ):
                pass

            # If that failed, try UCI notation
            if move is None:
                try:
                    move = chess.Move.from_uci(move_input)
                    if move not in board.legal_moves:
                        move = None
                except (ValueError, chess.InvalidMoveError):
                    pass

            if move is None:
                print(
                    f"Invalid move: '{move_input}'. Type 'help' for format examples or 'moves' for legal moves."
                )
                continue

            # Valid move found
            print(f"Human plays: {move}")
            return move

        except KeyboardInterrupt:
            print("\nGame ended by player.")
            return None
        except Exception as e:
            print(f"Error parsing move: {e}")
            continue


def display_win_rate_chart(win_rates_history: List[Tuple[float, float]]) -> None:
    """
    Display a simple text chart showing win rate evolution by round.

    Creates a visual representation of how win rates for both colors
    change throughout the game using ASCII characters.

    Parameters
    ----------
    win_rates_history : list of tuple
        List of (white_win_rate, black_win_rate) tuples for each round.
        Each win rate should be a float between 0.0 and 1.0.

    Notes
    -----
    The chart uses the following symbols:
    - 'W': White advantage regions
    - 'B': Black advantage regions
    - ' ': Draw tendency regions
    """
    if not win_rates_history:
        return

    print("\n" + "=" * 60)
    print("WIN RATE EVOLUTION CHART")
    print("=" * 60)
    print("Round | White Win % | Black Win % | Chart (W=White, B=Black)")
    print("-" * 60)

    for round_num, (white_rate, black_rate) in enumerate(win_rates_history, 1):
        # Create a simple bar chart (50 characters wide)
        chart_width = 50
        white_bars = int(white_rate * chart_width)
        black_bars = int(black_rate * chart_width)

        # Build the chart string
        chart = ""
        for i in range(chart_width):
            if i < white_bars:
                chart += "W"
            elif i < white_bars + black_bars:
                chart += "B"
            else:
                chart += " "

        print(
            f"{round_num:5d} | {white_rate * 100:10.1f} | {black_rate * 100:10.1f} | {chart}"
        )

    print("-" * 60)
    print("W = White advantage, B = Black advantage, Space = Draw tendency")
    print("=" * 60)


def interactive_play(
    player_color: str = "white", opponent: str = "random", player_type: str = "mcts"
) -> None:
    """
    Play mode with configurable player and opponent types.

    Sets up and runs an interactive chess game with support for human players
    and different opponent types (MCTS engines and random moves).

    Parameters
    ----------
    player_color : str, default="white"
        The color for the player.
        Valid values: "white", "w", "black", "b"
    opponent : str, default="random"
        The type of opponent to play against.
        Valid values: "random", "rand", "mcts", "engine"
    player_type : str, default="mcts"
        The type of player.
        Valid values: "human", "mcts"

    Notes
    -----
    Player types:
    - "human": Player enters moves manually via text input
    - "mcts": Player uses MCTS engine

    Opponent types:
    - "random"/"rand": Computer makes random legal moves
    - "mcts"/"engine": Computer uses MCTS engine

    For human input mode:
    - Standard algebraic notation: "e4", "Nf3", "Bxf7+", "O-O", "Qh5#"
    - UCI notation: "e2e4", "g1f3", "e1g1" (castling)
    - Commands: "help", "moves", "quit"
    """

    # Parse player type
    is_human_player = player_type.lower() in ["human", "h"]

    # Parse opponent type
    if opponent.lower() in ["mcts", "engine"]:
        opponent_type = "mcts"
        opponent_name = "MCTS Engine"
    elif opponent.lower() in ["random", "rand"]:
        opponent_type = "random"
        opponent_name = "Random"

    player_name = "Human" if is_human_player else "MCTS Engine"

    print(f"Chess Play Mode: {player_name} vs {opponent_name}")
    print("=" * 40)
    print()

    # Parse color argument
    if player_color.lower() in ["white", "w"]:
        player_color = chess.WHITE
        player_color_name = "White"
    elif player_color.lower() in ["black", "b"]:
        player_color = chess.BLACK
        player_color_name = "Black"

    print(f"Player: {player_color_name} - {player_name}")
    print(
        f"Opponent: {'Black' if player_color == chess.WHITE else 'White'} - {opponent_name}"
    )

    if is_human_player:
        print()
        print("Move format: Standard notation (e4, Nf3, O-O) or UCI (e2e4, g1f3)")
        print("Commands: 'help' for examples, 'moves' for legal moves, 'quit' to exit")
    print()

    # Get MCTS configuration
    mcts_config = create_custom_config(CUSTOM_SIMULATIONS)

    # Setup MCTS engines based on player and opponent types
    player_mcts = None
    opponent_mcts = None

    if not is_human_player:
        # Player uses MCTS
        player_mcts = ChessMCTS(mcts_config)
        print(f"Player MCTS Config: Sims={mcts_config.num_simulations}")

    if opponent_type == "mcts":
        # Opponent uses MCTS
        opponent_mcts = ChessMCTS(mcts_config)
        print(f"Opponent MCTS Config: Sims={mcts_config.num_simulations}")
    print()

    # Create chess board
    board = chess.Board()
    move_count = 0

    # Win rate tracking
    win_rates_history = []  # Store (white_win_rate, black_win_rate) for each round

    print("Game starting")

    # Game begins
    while not board.is_game_over():
        current_player = "White" if board.turn else "Black"
        is_player_turn = board.turn == player_color

        print(f"\n{'=' * 50}")
        print(f"MOVE {move_count + 1} - {current_player.upper()} TO MOVE")
        print(f"{'=' * 50}")
        print(board)
        print()

        if is_player_turn:
            # player's turn - handle human input vs MCTS
            if is_human_player:
                # Human player enters moves
                move = get_human_move(board, player_color_name)
                if move is None:
                    return  # Player quit
                board.push(move)
            else:
                # MCTS player
                print(f"Your turn ({player_color_name}) - MCTS thinking")
                move, stats = player_mcts.search(board)

                # Use the selected move's win rate from MCTS stats
                if "selected_move_win_rate" in stats:
                    current_player_win_rate = stats["selected_move_win_rate"]
                    # Convert to white/black perspective
                    if board.turn:  # White to move
                        white_win_rate = current_player_win_rate
                        black_win_rate = 1.0 - current_player_win_rate
                    else:  # Black to move
                        black_win_rate = current_player_win_rate
                        white_win_rate = 1.0 - current_player_win_rate

                    win_rates_history.append((white_win_rate, black_win_rate))
                    print(
                        f"Move win probability: White {white_win_rate * 100:.1f}%, Black {black_win_rate * 100:.1f}%"
                    )

                print(f"You (MCTS) play: {move}")
                print(
                    f"Search stats: {stats['simulations_run']} sims in {stats['total_time']:.2f}s"
                )

                if SHOW_DETAILED_ANALYSIS:
                    player_mcts.print_move_analysis(3)

                board.push(move)
        else:
            # Opponent's turn
            if opponent_type == "random":
                # Random opponent
                legal_moves = list(board.legal_moves)
                move = random.choice(legal_moves)
                print(f"Opponent (Random) plays: {move}")
                board.push(move)
            else:
                # MCTS opponent
                print("Opponent (MCTS) thinking...")
                move, stats = opponent_mcts.search(board)

                # Use the selected move's win rate from MCTS stats
                if "selected_move_win_rate" in stats:
                    current_player_win_rate = stats["selected_move_win_rate"]
                    # Convert to white/black perspective
                    if board.turn == chess.WHITE:  # White to move
                        white_win_rate = current_player_win_rate
                        black_win_rate = 1.0 - current_player_win_rate
                    else:  # Black to move
                        black_win_rate = current_player_win_rate
                        white_win_rate = 1.0 - current_player_win_rate

                    win_rates_history.append((white_win_rate, black_win_rate))
                    print(
                        f"Move win probability: White {white_win_rate * 100:.1f}%, Black {black_win_rate * 100:.1f}%"
                    )

        move_count += 1

        # Check for game end
        if board.is_game_over():
            break

        # Pause between moves
        # input("\nPress Enter to continue...")

    # Game over
    print(f"\n{'=' * 50}")
    print("GAME OVER")
    print(f"{'=' * 50}")
    print("Final position:")
    print(board)
    print()

    outcome = board.outcome()
    if outcome:
        if outcome.winner is None:
            print("Result: DRAW")
            if outcome.termination == chess.Termination.STALEMATE:
                print("Reason: Stalemate")
            elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
                print("Reason: Insufficient material")
            elif outcome.termination == chess.Termination.THREEFOLD_REPETITION:
                print("Reason: Threefold repetition")
            elif outcome.termination == chess.Termination.FIFTY_MOVES:
                print("Reason: Fifty-move rule")
        else:
            winner = "White" if outcome.winner else "Black"
            print(f"Result: {winner} WINS!")
            if outcome.termination == chess.Termination.CHECKMATE:
                print("Reason: Checkmate")

            # Determine if player won
            player_won = outcome.winner == player_color
            if player_won:
                print("\n🎉 You (MCTS) won! 🎉")
            else:
                print(f"\n😞 You lost to the {opponent_name} opponent!")
    else:
        print(f"Game ended after {move_count} moves (move limit reached)")

    # Display win rate evolution chart
    if win_rates_history:
        display_win_rate_chart(win_rates_history)


if __name__ == "__main__":
    print("Chess Monte Carlo Tree Search")
    print("=" * 40)
    print()
    print("Select game mode:")
    print("1. Human vs Computer (you enter moves)")
    print("2. MCTS vs Random opponent")
    print("3. MCTS vs MCTS")
    print()

    choice = input("Enter your choice (1-3): ").strip()
    print()

    if choice == "1":
        # Human vs Computer mode
        print("Human vs Computer mode selected")
        color_choice = input("Play as (w)hite or (b)lack? [w]: ").strip().lower()
        player_color = "black" if color_choice in ["b", "black"] else "white"
        interactive_play(
            player_type="human", player_color=player_color, opponent="mcts"
        )

    elif choice == "2":
        # MCTS vs Random mode
        print("MCTS vs Random mode selected")
        color_choice = input("MCTS plays as (w)hite or (b)lack? [w]: ").strip().lower()
        player_color = "black" if color_choice in ["b", "black"] else "white"
        interactive_play(
            player_type="mcts", player_color=player_color, opponent="random"
        )

    elif choice == "3":
        # MCTS vs MCTS mode
        print("MCTS vs MCTS mode selected")
        interactive_play(player_type="mcts", player_color="white", opponent="mcts")
