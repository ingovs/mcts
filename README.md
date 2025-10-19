# Monte Carlo Tree Search for Chess

A from-scratch implementation of Monte Carlo Tree Search (MCTS) algorithm for chess, designed for learning and experimentation with configurable search parameters.

## 🎯 Features

### Core MCTS Implementation
- **Pure Python MCTS**: Complete algorithm implementation with UCB1 selection
- **Chess Integration**: Built on python-chess library with full rule compliance
- **Configurable Search**: Adjustable simulation count and exploration parameters
- **Real-time Statistics**: Comprehensive search metrics and performance analysis
- **AlphaZero Configuration**: Default settings based on AlphaZero research (800 simulations per move)

### Interactive Gameplay
- **Human vs Computer**: Play against MCTS engine with intuitive text input
- **Multiple Game Modes**: Human vs MCTS, MCTS vs Random, MCTS vs MCTS
- **Move Format Support**: Standard algebraic notation (e4, Nf3) and UCI notation (e2e4)
- **Real-time Analysis**: Win probability tracking and move evaluation
- **Visual Win Rate Charts**: ASCII charts showing evaluation evolution throughout the game

### Advanced Features
- **Move Analysis**: Detailed statistics for top candidate moves
- **Game State Detection**: Proper handling of checkmate, stalemate, and draw conditions
- **Flexible Configuration**: Easy parameter tuning for different playing strengths
- **Progress Tracking**: Real-time simulation progress during search




## 🚀 Quick Start

### Interactive Play
Run the main script and select from available game modes:
```bash
python run_mcts.py
```

This will present a menu with three options:
1. **Human vs Computer** - Play as human against MCTS engine
2. **MCTS vs Random** - Watch MCTS play against random moves
3. **MCTS vs MCTS** - Watch two MCTS engines play against each other

### Example Game Session
```
Chess Monte Carlo Tree Search
========================================

Select game mode:
1. Human vs Computer (you enter moves)
2. MCTS vs Random opponent
3. MCTS vs MCTS

Enter your choice (1-3): 1

Human vs Computer mode selected
Play as (w)hite or (b)lack? [w]: w

Chess Play Mode: Human vs MCTS Engine
========================================
Player: White - Human
Opponent: Black - MCTS Engine

Move format: Standard notation (e4, Nf3, O-O) or UCI (e2e4, g1f3)
Commands: 'help' for examples, 'moves' for legal moves, 'quit' to exit
```

## ⚙️ Configuration

### Basic Configuration
Edit the configuration section in `run_mcts.py`:

```python
# ===============================================
# CONFIGURATION SECTION - EDIT THESE VALUES
# ===============================================

# Search parameters
CUSTOM_SIMULATIONS = 800  # Number of simulations per move

# Display options
SHOW_DETAILED_ANALYSIS = True  # Show move analysis
```

### Advanced Configuration
The MCTS engine is configured through the `MCTSConfig` class in `src/config.py`:

```python
@dataclass
class MCTSConfig:
    num_simulations: int = 800          # Simulations per move
    exploration_constant: float = 1.414 # UCB1 exploration parameter
```

### Parameter Guidelines

| Parameter | Range | Effect | Recommended |
|-----------|-------|--------|-------------|
| `num_simulations` | 100-5000 | Search strength vs speed | 800 (AlphaZero) |
| `exploration_constant` | 0.5-2.0 | Exploration vs exploitation | 1.414 (√2) |

## 🏗️ Project Structure

```
mcts/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── mcts_chess.py         # Core MCTS implementation
│   │   ├── MCTSNode          # Tree node with chess state
│   │   └── ChessMCTS         # Main MCTS search engine
│   └── config.py             # Configuration classes and presets
├── run_mcts.py               # Interactive runner and game modes
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
└── README.md                 # This documentation
```

## 🧠 Algorithm Implementation

### MCTS Four Phases
The implementation follows the standard MCTS algorithm with four phases:

#### 1. Selection (`_select`)
Navigate the tree using UCB1 formula until reaching a leaf node:
```python
UCB1 = win_rate + exploration_constant * sqrt(ln(parent_visits) / node_visits)
```

#### 2. Expansion (`expand`)
Add a new child node for an unexplored legal move:
```python
# Create new child for next unexplored move
move = self.unexplored_moves.pop(0)
child = MCTSNode(board=new_board, move=move, parent=self)
```

#### 3. Simulation (`simulate`)
Play random moves until the game ends naturally for the random child node:
```python
while not simulation_board.is_game_over():
    legal_moves = list(simulation_board.legal_moves)
    move = random.choice(legal_moves)
    simulation_board.push(move)
```

#### 4. Backpropagation (`backpropagate`)
Update statistics up the tree, flipping results for alternating players:
```python
self.visits += 1
self.wins += result
if self.parent:
    self.parent.backpropagate(1.0 - result)
```

### Key Design Decisions
- **Full Rule Compliance**: Uses python-chess for move validation and game rules
- **Draw Detection**: Automatic handling of stalemate, insufficient material, repetition
- **Move Selection**: Chooses move with highest visit count
- **Proper Evaluation**: Handles checkmate, stalemate, and draw conditions correctly

## 🎮 Interactive Features

### Human Input Modes

**Standard Algebraic Notation:**
```
e4        # Pawn to e4
Nf3       # Knight to f3
Bxf7+     # Bishop captures on f7 with check
O-O       # Kingside castling
Qh5#      # Queen to h5, checkmate
```

**UCI Notation:**
```
e2e4      # Move from e2 to e4
g1f3      # Knight from g1 to f3
e1g1      # Castling (king to g1)
h7h8q     # Pawn promotion to queen
```

**Special Commands:**
- `help` - Show move format examples
- `moves` - List all legal moves
- `quit`/`exit` - End the game

### Move Analysis Output

The engine provides detailed analysis of candidate moves:

```
Top 3 moves analyzed:
Move                 Visits    Win Rate    UCB1
--------------------------------------------------
e2e4                   45       0.556      1.234
g1f3                   38       0.542      1.198
d2d4                   32       0.531      1.167
```

### Win Rate Visualization

Track how the position evaluation changes throughout the game:

```
============================================================
WIN RATE EVOLUTION CHART
============================================================
Round | White Win % | Black Win % | Chart (W=White, B=Black)
------------------------------------------------------------
    1 |       55.2 |       44.8 | WWWWWWWWWWWWWWWWWWWWWWWWWWWBBBBBBBBBBBBBBBBBBBBBBB
    2 |       48.3 |       51.7 | WWWWWWWWWWWWWWWWWWWWWWWWBBBBBBBBBBBBBBBBBBBBBBBBBB
    3 |       52.1 |       47.9 | WWWWWWWWWWWWWWWWWWWWWWWWWWBBBBBBBBBBBBBBBBBBBBBBB
============================================================
```

## � Performance Tips

### For Faster Search:
- Reduce `num_simulations` (try 200-500)
- Use fewer simulations for quick games

### For Stronger Play:
- Increase `num_simulations` (try 2000-5000)
- More simulations generally lead to better move quality

### Search Behavior Examples:

With `num_simulations=200`:
- Fast search, good for rapid games
- ~0.5-1 second per move

With `num_simulations=800` (default):
- Balanced strength and speed
- ~2-3 seconds per move


### Advanced Analysis

```python
# Get detailed move analysis
mcts.print_move_analysis(top_moves=5)

# Access search statistics
stats = {
    'simulations_run': 800,
    'total_time': 2.34,
    'simulations_per_second': 341.9,
    'tree_size': 1247,
    'root_visits': 800,
    'best_move_visits': 45,
    'children_count': 20,
    'selected_move_win_rate': 0.556,
    'tree_dict': {...}  # Complete tree structure containing each node's move, wins and visits count
}

# Analyze the search tree
tree = stats['tree_dict']
print(f"Total tree nodes explored: {stats['tree_size']}")
print(f"Most visited child has {stats['best_move_visits']} visits")

# Find the most promising moves
sorted_moves = sorted(tree['children'], key=lambda x: x['visits'], reverse=True)
for i, move in enumerate(sorted_moves[:3]):
    print(f"{i+1}. {move['move']}: {move['visits']} visits, {move['win_rate']:.1%} win rate")
```

## 🔍 Troubleshooting

### Common Issues

**Slow Performance:**
- Reduce `num_simulations` for faster play
- Check if system is under heavy load
- Ensure python-chess library is properly installed

**Input Errors:**
- Use `moves` command to see all legal moves
- Try UCI notation if algebraic notation fails
- Check for typos in move input

**Memory Usage:**
- Large simulation counts create bigger trees
- Monitor system memory with very high simulation counts

### Performance Tips

1. **Start Small**: Begin with 200-400 simulations, increase gradually
2. **Monitor Statistics**: Watch simulations/second and tree growth
3. **Balance Parameters**: More simulations = stronger but slower play
4. **Use Analysis**: Enable `SHOW_DETAILED_ANALYSIS` to understand decisions

## 🛠️ Development

### Dependencies
- `chess>=1.10.0` - Chess game logic and move validation
- `numpy>=1.21.0` - Numerical computations (future use)
- `ruff` - Code formatting and linting

### Code Quality
The project uses Ruff for code formatting and linting:
```bash
ruff check src/ run_mcts.py
ruff format src/ run_mcts.py
```

### Future Enhancements
- **Neural Network Integration**: Replace random simulations with neural network evaluation
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AlphaZero Research**: Configuration based on DeepMind's AlphaZero paper
- **python-chess Library**: Excellent chess game implementation
