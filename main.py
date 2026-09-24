import os

from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from components import *
from game_engine import *
from mp_game_engine import *
from game_engine import attack

app = Flask(__name__)
# The whole game lives in Flask's signed session cookie instead of module
# globals, so it works with several players at once and on serverless hosts
# (e.g. Vercel) where each request may hit a different process.
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-battleships-secret')

BOARD_SIZE = 10
DIFFICULTIES = ['easy', 'hard', 'expert']
DIRECTIONS = [None, 'up', 'down', 'left', 'right']


# ---------------------------------------------------------------------------
# Compact board encoding for the session cookie.
# '.' empty, '0'-'9' ship index (order of battleships.txt), 'X' hit, 'O' miss
# ---------------------------------------------------------------------------
def ship_names():
    return list(create_battleships().keys())

def encode_board(board):
    names = ship_names()
    out = []
    for row in board:
        for cell in row:
            if cell is None:
                out.append('.')
            elif cell in ['X', 'O']:
                out.append(cell)
            else:
                out.append(str(names.index(cell)))
    return ''.join(out)

def decode_board(code, size=BOARD_SIZE):
    names = ship_names()
    board = initialise_board(size)
    for i, ch in enumerate(code):
        if ch == '.':
            value = None
        elif ch in 'XO':
            value = ch
        else:
            value = names[int(ch)]
        board[i // size][i % size] = value
    return board

def ship_cells(layout_board, ship):
    return [[x, y] for y, row in enumerate(layout_board) for x, cell in enumerate(row) if cell == ship]

def sunk_cells(layout_board, ships):
    cells = []
    for ship, count in ships.items():
        if count == 0:
            cells += ship_cells(layout_board, ship)
    return cells

def remaining_ships(layout_board, live_board):
    """Ship counts keyed by name, including ships that are already sunk (0)."""
    ships = {name: 0 for name in set(c for row in layout_board for c in row if c is not None)}
    ships.update(count_ships(live_board))
    return ships

def encode_history(history):
    return [[h['coords'][0], h['coords'][1], int(h['is_hit']), DIRECTIONS.index(h['direction'])] for h in history]

def decode_history(rows):
    return [{'coords': (r[0], r[1]), 'is_hit': bool(r[2]), 'direction': DIRECTIONS[r[3]]} for r in rows]


def load_placement():
    placement = session.get('placement')
    if placement is None:
        with open(os.path.join(BASE_DIR, 'placement.json')) as f:
            placement = json.load(f)
    return placement

def validate_placement(placement):
    """Returns the board for a placement, or None if it breaks the rules."""
    ships = create_battleships()
    if not isinstance(placement, dict) or set(placement.keys()) != set(ships.keys()):
        return None
    try:
        board = place_battleships(initialise_board(BOARD_SIZE), algorithm='custom', placement=placement)
    except (ValueError, TypeError, IndexError, KeyError):
        return None
    return board if count_ships(board) == ships else None


@app.route('/placement', methods=['GET', 'POST'])
def placement_interface():
    if request.method == 'GET':
        # Handle GET request
        data = create_battleships()
        size = BOARD_SIZE
        return render_template('placement.html', ships=data, board_size=size,
                               placement=session.get('placement'),
                               difficulty=session.get('difficulty', 'hard'))
    elif request.method == 'POST':
        # Handle POST request. Accepts the original coursework format
        # ({ship: [x, y, 'h'|'v']}) or {placement: {...}, difficulty: '...'}
        data = request.get_json(silent=True) or {}
        placement = data.get('placement', data)
        if validate_placement(placement) is None:
            return jsonify({'message': 'Invalid placement'}), 400
        session['placement'] = placement
        if data.get('difficulty') in DIFFICULTIES:
            session['difficulty'] = data['difficulty']
        return jsonify({'message': 'Received'}), 200


@app.route('/')
def root():
    # 3 modes: easy (random), hard (original pattern-following AI) and
    # expert (hunt/target AI)
    difficulty = request.args.get('difficulty', session.get('difficulty', 'hard'))
    if difficulty not in DIFFICULTIES:
        difficulty = 'hard'
    session['difficulty'] = difficulty

    # Initializing two players' board
    player_board = validate_placement(load_placement())
    if player_board is None:
        session.pop('placement', None)
        return redirect(url_for('placement_interface'))
    if difficulty == 'easy':
        ai_board = place_battleships(initialise_board(), algorithm='random')
    else:
        ai_board = place_battleships(initialise_board(), algorithm='advanced')

    session['game'] = {
        'difficulty': difficulty,
        'player_layout': encode_board(player_board),
        'ai_layout': encode_board(ai_board),
        'player_live': encode_board(player_board),
        'ai_live': encode_board(ai_board),
        # AI's attack history (only used by the 'hard' algorithm)
        'history': [],
        'shots': 0,
        'hits': 0,
    }
    return render_template('main.html', player_board=player_board,
                           ships=create_battleships(), difficulty=difficulty)


def no_ships_remaining(ships):
    return all(value == 0 for value in ships.values())


def ai_turn(game, player_layout, player_board, player_ships):
    difficulty = game['difficulty']
    if difficulty == 'easy':
        # AI does random attacks if difficulty is set to easy
        return generate_attack(player_board)
    if difficulty == 'expert':
        # Hunt/target AI, only sees hit/miss marks and which ships are sunk
        sizes = [len(ship_cells(player_layout, s)) for s, n in player_ships.items() if n > 0]
        return generate_hunt_target_attack(player_board, sizes, sunk_cells(player_layout, player_ships))
    # AI does advanced attacks if difficulty is set to hard
    history = decode_history(game['history'])
    attacked = {h['coords'] for h in history}
    probable_positions = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE) if (x, y) not in attacked]
    coords = generate_advanced_attack(player_board, history, probable_positions)
    game['history'] = encode_history(history)
    return tuple(coords)


@app.route('/attack')
def process_attack():
    game = session.get('game')
    if not game:
        return jsonify({'error': 'No game in progress'}), 409

    # Get player's coordinates
    try:
        x = int(request.args.get('x'))
        y = int(request.args.get('y'))
    except (TypeError, ValueError):
        return jsonify({'error': 'x and y must be integers'}), 400
    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
        return jsonify({'error': 'Coordinates out of range'}), 400

    # Rebuild both boards from the session
    player_layout = decode_board(game['player_layout'])
    ai_layout = decode_board(game['ai_layout'])
    player_board = decode_board(game['player_live'])
    ai_board = decode_board(game['ai_live'])
    player_ships = remaining_ships(player_layout, player_board)
    ai_ships = remaining_ships(ai_layout, ai_board)

    if no_ships_remaining(ai_ships) or no_ships_remaining(player_ships):
        return jsonify({'error': 'Game is already over'}), 409
    if ai_board[y][x] in ['X', 'O']:
        return jsonify({'error': 'Already fired at that cell'}), 400

    # Process player's attack
    target = ai_board[y][x]
    is_hit = attack((x, y), ai_board, ai_ships)
    game['shots'] += 1
    result = {'hit': is_hit}
    if is_hit:
        game['hits'] += 1
        if ai_ships[target] == 0:
            result['sunk'] = {'name': target, 'cells': ship_cells(ai_layout, target)}

    # AI only shoots back if the player has not just won
    if not no_ships_remaining(ai_ships):
        ai_attack = ai_turn(game, player_layout, player_board, player_ships)
        ai_target = player_board[ai_attack[1]][ai_attack[0]]
        # Process AI's attack
        ai_hit = attack(ai_attack, player_board, player_ships)
        result['AI_Turn'] = list(ai_attack)
        result['ai_hit'] = ai_hit
        if ai_hit and player_ships[ai_target] == 0:
            result['ai_sunk'] = {'name': ai_target, 'cells': ship_cells(player_layout, ai_target)}

    game['player_live'] = encode_board(player_board)
    game['ai_live'] = encode_board(ai_board)
    session['game'] = game

    # Handle the End of the game
    is_finished_player_wins = no_ships_remaining(ai_ships)
    is_finished_ai_wins = no_ships_remaining(player_ships)

    if is_finished_player_wins:
        result['finished'] = 'You Win!'
    elif is_finished_ai_wins:
        result['finished'] = 'Game Over!'
    if 'finished' in result:
        # Reveal the enemy ships that are still afloat
        result['reveal'] = [{'name': s, 'cells': ship_cells(ai_layout, s)} for s, n in ai_ships.items() if n > 0]
        result['stats'] = {'shots': game['shots'], 'hits': game['hits']}
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 5000)), debug=bool(os.environ.get('FLASK_DEBUG')))
