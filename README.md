# Phase 10 - Python Implementation

A complete console-based implementation of the popular Phase 10 card game, built entirely in Python.

## Overview

Phase 10 is a rummy-style card game where players compete to complete 10 different phases in order. This implementation includes all official rules, intelligent card sorting, and a user-friendly text interface.

## Features

### ✅ Complete Game Implementation
- **All 10 official phases** with proper validation
- **2-6 player support** as per official rules
- **Wild and Skip cards** with correct point values
- **"Hitting on" mechanics** for playing cards on completed phases
- **Proper scoring system**: 1-9 = 5pts, 10-12 = 10pts, Wild = 25pts, Skip = 15pts

### ✅ Smart Card Sorting
- **Phase-aware sorting**: Cards automatically organize based on current phase needs
- **Set phases** (1,7,9,10): Groups cards by rank, most frequent first
- **Run phases** (4,5,6): Sorts numerically to highlight sequences  
- **Color phase** (8): Groups by color, most common first
- **Wild/Skip placement**: Always at bottom for easy identification

### ✅ Enhanced User Experience
- **Clear console** at start of each turn for clean interface
- **Phase hints** explaining what each phase requires
- **Hand shown before and after drawing** for better decision making
- **Sorted display** with original card numbers for easy selection
- **Comprehensive game state** showing all players' progress

## The 10 Phases

1. **2 sets of 3** - Two groups of 3 cards with the same number
2. **1 set of 3 + 1 run of 4** - 3 of a kind and 4 consecutive numbers
3. **1 set of 4 + 1 run of 4** - 4 of a kind and 4 consecutive numbers  
4. **1 run of 7** - 7 consecutive numbers
5. **1 run of 8** - 8 consecutive numbers
6. **1 run of 9** - 9 consecutive numbers
7. **2 sets of 4** - Two groups of 4 cards with the same number
8. **7 cards of one color** - 7 cards all red, blue, green, or yellow
9. **1 set of 5 + 1 set of 2** - 5 of a kind and 2 of a kind
10. **1 set of 5 + 1 set of 3** - 5 of a kind and 3 of a kind

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Quick Start
1. **Clone or download** this repository
2. **Navigate** to the project directory
3. **Run the game**:
   - **Windows**: Double-click `run_game.bat`
   - **Command line**: `python main.py`

### Running Tests
- **Windows**: Double-click `run_tests.bat`  
- **Command line**: `python test_phase10.py`

## How to Play

### Game Flow
1. **Setup**: Enter 2-6 player names
2. **Each turn**:
   - View your sorted hand
   - Draw from deck or discard pile
   - Complete your phase (if possible)
   - "Hit on" other players' completed phases
   - Discard one card
3. **Win conditions**: First to complete Phase 10 wins!

### Special Cards
- **Wild Cards**: Can substitute for any number in sets or runs (25 points)
- **Skip Cards**: Skip opponent's turn (15 points, extra turn in 2-player games)

### Strategy Tips
- **Focus on your current phase** - the sorting helps identify opportunities
- **Use wilds wisely** - they're worth 25 points if left in hand
- **Hit on phases** after completing yours to empty your hand faster
- **Watch opponents' progress** - they might complete phases before you!

## File Structure

```
phase_ten/
├── main.py           # Game interface and user interaction
├── game.py           # Core game logic and flow control  
├── player.py         # Player class with smart sorting
├── phases.py         # Phase definitions and validation
├── cards.py          # Card, deck, and discard pile classes
├── test_phase10.py   # Comprehensive test suite (35 tests)
├── run_game.bat      # Windows game launcher
├── run_tests.bat     # Windows test runner
├── rules.txt         # Official Phase 10 rules reference
└── README.md         # This file
```

## Technical Details

### Architecture
- **Modular design** with separate concerns for cards, phases, players, and game flow
- **Comprehensive validation** for all phase requirements
- **Smart sorting algorithms** optimized for each phase type
- **Full test coverage** with 35 unit tests

### Card Sorting Intelligence
- **Set phases**: Frequency-based grouping with rank priority
- **Run phases**: Numerical sequencing for easy consecutive identification
- **Color phase**: Color grouping with count-based priority
- **Mixed phases**: Hybrid approach combining set and run strategies

### Game Rules Compliance
- Follows all official Phase 10 rules from Mattel
- Proper deck composition (108 cards total)
- Accurate point values and scoring
- Complete turn sequence implementation

## Testing

The implementation includes **35 comprehensive tests** covering:
- Card creation and properties
- Deck composition and shuffling  
- Phase validation logic
- Player hand management
- Game flow and scoring
- Smart sorting algorithms

**Run tests**: `python test_phase10.py` - All tests should pass ✅

## Contributing

This is a complete implementation, but improvements are welcome:
- Additional card sorting strategies
- AI opponents
- Network multiplayer
- GUI interface
- Game statistics tracking

## License

This project is for educational and personal use. Phase 10 is a trademark of Mattel, Inc.

---

**Enjoy playing Phase 10!** 🎮

*Created with Python 3.12 • Fully tested • Console-based fun*