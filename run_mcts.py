#!/usr/bin/env python3
"""
Simple runner for Chess MCTS with easy parameter configuration.
Edit the configuration section below to customize search parameters.
"""

import sys
import os

# Add src directory to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import chess
from mcts_chess import ChessMCTS, MCTSConfig
from config import SearchConfig, get_config_by_strength, create_custom_config


def display_win_rate_chart(win_rates_history):
    """Display a simple text chart showing win rate evolution by round."""
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

        print(f"{round_num:5d} | {white_rate*100:10.1f} | {black_rate*100:10.1f} | {chart}")

    print("-" * 60)
    print("W = White advantage, B = Black advantage, Space = Draw tendency")
    print("=" * 60)


# ===============================================
# CONFIGURATION SECTION - EDIT THESE VALUES
# ===============================================

# Option 1: Use a preset configuration
USE_PRESET = True
PRESET_STRENGTH = "alphazero"  # Options: "fast", "balanced", "deep", "tournament", "alphazero"

# Option 2: Custom configuration (only used if USE_PRESET is False)
CUSTOM_DEPTH = 5      # How many moves deep to simulate (per side)
CUSTOM_SIMULATIONS = 1000  # Number of simulations to run

# Additional options
SHOW_DETAILED_ANALYSIS = True  # Show detailed move analysis

# Interactive play options
PLAYER_COLOR = "white"  # Options: "white", "black"
OPPONENT_TYPE = "random"  # Options: "random", "mcts"


def convert_config(search_config: SearchConfig) -> MCTSConfig:
    """Convert SearchConfig to MCTSConfig format."""
    return MCTSConfig(
        max_simulation_depth=search_config.MAX_SIMULATION_DEPTH,
        num_simulations=search_config.NUM_SIMULATIONS,
        exploration_constant=search_config.EXPLORATION_CONSTANT
    )


def interactive_play(color="white", opponent="random"):
    """Play mode where player (MCTS) plays against opponent (MCTS or random)."""
    import random

    print("Chess Play Mode: MCTS vs Opponent")
    print("=" * 40)
    print()

    # Parse color argument
    if color.lower() in ["white", "w"]:
        player_color = chess.WHITE
        player_color_name = "White"
    elif color.lower() in ["black", "b"]:
        player_color = chess.BLACK
        player_color_name = "Black"

    # Parse opponent type
    if opponent.lower() in ["mcts", "engine"]:
        opponent_type = "mcts"
        opponent_name = "MCTS Engine"
    elif opponent.lower() in ["random", "rand"]:
        opponent_type = "random"
        opponent_name = "Random"

    print(f"Player (You): {player_color_name} - MCTS Engine")
    print(f"Opponent: {'Black' if player_color == chess.WHITE else 'White'} - {opponent_name}")
    print()

    # Get MCTS configuration for player
    if USE_PRESET:
        player_config = get_config_by_strength(PRESET_STRENGTH)
    else:
        player_config = create_custom_config(
            CUSTOM_DEPTH,
            CUSTOM_SIMULATIONS,
        )
    player_mcts_config = convert_config(player_config)
    player_mcts = ChessMCTS(player_mcts_config)
    print(f"Player MCTS Config: Depth={player_config.MAX_SIMULATION_DEPTH}, Sims={player_config.NUM_SIMULATIONS}")

    # Get MCTS configuration for opponent if needed
    opponent_mcts = None
    if opponent_type == "mcts":
        # Use same config as player for fair comparison
        opponent_mcts_config = convert_config(player_config)
        opponent_mcts = ChessMCTS(opponent_mcts_config)
        print("Opponent MCTS Config: Same as player")
    print()

    # Create chess board
    board = chess.Board()
    move_count = 0

    # Win rate tracking
    win_rates_history = []  # Store (white_win_rate, black_win_rate) for each round

    print("Game starting...")
    print("Press Enter after each move to continue")
    print()

    while not board.is_game_over():
        current_player = "White" if board.turn else "Black"
        is_player_turn = (board.turn == player_color)

        print(f"\n{'='*50}")
        print(f"MOVE {move_count + 1} - {current_player.upper()} TO MOVE")
        print(f"{'='*50}")
        print(board)
        print()

        if is_player_turn:
            # Player's turn (always MCTS)
            print(f"Your turn ({player_color_name}) - MCTS thinking...")
            move, stats = player_mcts.search(board)

            # Use the selected move's win rate from MCTS stats
            if 'selected_move_win_rate' in stats:
                current_player_win_rate = stats['selected_move_win_rate']
                # Convert to white/black perspective
                if board.turn:  # White to move
                    white_win_rate = current_player_win_rate
                    black_win_rate = 1.0 - current_player_win_rate
                else:  # Black to move
                    black_win_rate = current_player_win_rate
                    white_win_rate = 1.0 - current_player_win_rate

                win_rates_history.append((white_win_rate, black_win_rate))
                print(f"Move win probability: White {white_win_rate*100:.1f}%, Black {black_win_rate*100:.1f}%")

            print(f"You (MCTS) play: {move}")
            print(f"Search stats: {stats['simulations_run']} sims in {stats['total_time']:.2f}s")

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
                if 'selected_move_win_rate' in stats:
                    current_player_win_rate = stats['selected_move_win_rate']
                    # Convert to white/black perspective
                    if board.turn == chess.WHITE:  # White to move
                        white_win_rate = current_player_win_rate
                        black_win_rate = 1.0 - current_player_win_rate
                    else:  # Black to move
                        black_win_rate = current_player_win_rate
                        white_win_rate = 1.0 - current_player_win_rate

                    win_rates_history.append((white_win_rate, black_win_rate))
                    print(f"Move win probability: White {white_win_rate*100:.1f}%, Black {black_win_rate*100:.1f}%")

                print(f"Opponent (MCTS) plays: {move}")
                print(f"Search stats: {stats['simulations_run']} sims in {stats['total_time']:.2f}s")

                board.push(move)

        move_count += 1

        # Check for game end
        if board.is_game_over():
            break

        # Pause between moves
        # input("\nPress Enter to continue...")

    # Game over
    print(f"\n{'='*50}")
    print("GAME OVER")
    print(f"{'='*50}")
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
            player_won = (outcome.winner == player_color)
            if player_won:
                print("\n🎉 You (MCTS) won! 🎉")
            else:
                print(f"\n😞 You lost to the {opponent_name} opponent!")
    else:
        print(f"Game ended after {move_count} moves (move limit reached)")

    # Display win rate evolution chart
    if win_rates_history:
        display_win_rate_chart(win_rates_history)


def main():
    """Main function to run the MCTS chess demo."""

    print("Chess Monte Carlo Tree Search")
    print("=" * 40)
    print()

    # Get configuration
    if USE_PRESET:
        search_config = get_config_by_strength(PRESET_STRENGTH)
        print(f"Using preset configuration: {PRESET_STRENGTH.upper()}")
    else:
        search_config = create_custom_config(
            CUSTOM_DEPTH,
            CUSTOM_SIMULATIONS,
        )
        print("Using custom configuration")

    # Display configuration
    print("Configuration:")
    print(f"  - Simulation depth: {search_config.MAX_SIMULATION_DEPTH} moves per side")
    print("  - Considering ALL legal moves")
    print(f"  - Simulations: {search_config.NUM_SIMULATIONS}")
    print()

    # Convert to MCTS config
    mcts_config = convert_config(search_config)

    # Create chess board and MCTS engine
    board = chess.Board()
    mcts = ChessMCTS(mcts_config)

    move_count = 0

    while not board.is_game_over():
        current_player = "White" if board.turn else "Black"
        print(f"\n{'='*50}")
        print(f"MOVE {move_count + 1} - {current_player.upper()} TO MOVE")
        print(f"{'='*50}")
        print(f"Position: {board.fen()}")
        print()
        print(board)
        print()

        # Run MCTS search
        print(f"{current_player} is thinking...")
        best_move, stats = mcts.search(board)

        if best_move is None:
            print("No legal moves available!")
            break

        # Display results
        print(f"Selected move: {best_move}")
        print(f"Search stats: {stats['simulations_run']} simulations in {stats['total_time']:.2f}s")
        print(f"Speed: {stats['simulations_per_second']:.0f} simulations/second")
        print(f"Tree explored: {stats['tree_size']} positions")

        if SHOW_DETAILED_ANALYSIS:
            mcts.print_move_analysis(5)

            # Show principal variation
            pv = mcts.get_principal_variation(3)
            if pv:
                pv_str = " ".join(str(move) for move in pv)
                print(f"Principal variation: {pv_str}")

        # Make the move
        board.push(best_move)
        move_count += 1

        # Pause for readability
        # input("\nPress Enter to continue...")

    print(f"\nGame ended after {move_count} moves")
    print("Final position:")
    print(board)

    if board.is_game_over():
        outcome = board.outcome()
        if outcome.winner is None:
            print("Game result: Draw")
        else:
            winner = "White" if outcome.winner else "Black"
            print(f"Game result: {winner} wins")
            print(f"Termination: {outcome.termination.name}")


if __name__ == "__main__":
    print("Chess Monte Carlo Tree Search")
    print("=" * 40)
    print()

    mode = "play"

    if mode == "demo":
        print("Mode: Demo (MCTS vs MCTS)")
        main()
    elif mode == "play":
        interactive_play(color="white", opponent="random")
