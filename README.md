# Battleship 

## Overview

The Battleship game is a strategic guessing game typically played by two players. In the traditional board game, each player has a board with a grid of squares, typically 10x10, where they can place a fleet of ships without the opponent's knowledge. The objective is to sink your opponent's fleet before they sink yours. Each player takes turns to declare coordinates for their strike and the opponent replies whether that is a hit or miss until one player has no battleships remaining. 

## Features
- Game Setup: Arrange ships on a 10x10 grid (Aircraft Carrier, Battleship, Cruiser, Submarine, Destroyer).
- Gameplay: Players take turns calling grid coordinates to attack the opponent's grid, responses include "Hit" for a ship hit and "Miss" for an empty space.
- Strategy: Requires a mix of luck and strategic deduction, players deduce ship positions based on hits and misses.
- Winning Condition: The game ends when one player sinks the entire opponent's fleet.
- Components: initialise_board, create_battleships, place_battleships, attack.
- Single-Player command-line Interface: Allow players to attack on their own ships via command-line interface
- Multiple-Player command-line Interface: A battleships game against AI via command-line interface
- Multiplayer components: Manages multiple players' boards and battleships, AI opponent generates attacks based on board state.

Graphical Interface with Flask:
- Web interface with two main pages: Placement and Gameplay
- Placement Page: Allows players to place their ships
- Gameplay Page: Players can generate attacks on AI's board and check AI's attack on their own board
- Two difficulty levels: 'hard' and 'easy'
- Easy level: Simple AI's board placement, and random attacks
- Hard level: Advanced AI's board placement, and advanced attacks
+ Advanced placement: Strategically cluster ships to occupy certain sections of the board, mimicking human behavior. For instance, position larger ships near the center and smaller ships towards the periphery. Advanced algorithms can avoid easily identifiable patterns (e.g., perfect grid alignment), making it harder for opponents to guess ship placements based on a single hit. It also chooses ship orientations intelligently. For larger ships, consider both horizontal and vertical placements to minimize predictability.
+ Advanced attacks: Improved generate_attack function that is able to learn from previous attacks, and perform attacks with advanced algorithms: shooting in the same pattern, changing direction if previous attack missed, and handling consecutive attacks

## Requirements

This project utilizes several Python libraries. To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```

<i>Libraries Used:</i>
- importlib: Used for dynamically importing modules.
- inspect: Provides functions for examining the runtime Python environment.
- random: Used for generating random numbers and choices.
- json: Handles JSON data serialization and deserialization.
- pytest: Used for testing purposes.

<strong>Make sure to have Python installed as well.</strong>


## Usage

First, clone the repository:

```bash
    git clone https://github.com/duc-minh-droid/battleships
```

Install the required dependencies:

```bash
    pip install -r requirements.txt
```

Navigate to the project directory:

```bash
    cd your-repo
```

Run the main script:

```bash
    python main.py
```

## Contributors

- Nguyen Duc Minh (Thomas)

## License

This project is licensed under the [MIT License].

## Metadata

- **Author:** Thomas
- **Version:** 1.0.0
- **Release Date:** [14/12/2023]
