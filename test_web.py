"""Tests for the Flask game flow and the AI opponents (added after the coursework)."""
import random

import pytest

import main
from components import initialise_board, create_battleships, place_battleships
from game_engine import attack, count_ships
from mp_game_engine import generate_hunt_target_attack, generate_advanced_attack

PLACEMENT = {"Aircraft_Carrier": ["1", "2", "h"], "Battleship": ["1", "5", "v"], "Cruiser": ["8", "2", "v"],
             "Submarine": ["5", "6", "v"], "Destroyer": ["7", "6", "v"]}


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    with main.app.test_client() as c:
        yield c


def test_attack_uses_x_column_y_row():
    board = initialise_board(10)
    board[2][5] = 'Destroyer'
    ships = {'Destroyer': 2}
    assert attack((5, 2), board, ships) is True
    assert board[2][5] == 'X' and ships['Destroyer'] == 1
    assert attack((2, 5), board, ships) is False
    assert board[5][2] == 'O'


def test_advanced_placement_always_places_every_ship():
    for _ in range(200):
        board = place_battleships(initialise_board(10), create_battleships(), algorithm='advanced')
        assert count_ships(board) == create_battleships()


def test_custom_placement_from_dict():
    board = place_battleships(initialise_board(10), algorithm='custom', placement=PLACEMENT)
    assert count_ships(board) == create_battleships()
    assert board[2][1:6] == ['Aircraft_Carrier'] * 5


def test_placement_rejects_overlap(client):
    bad = dict(PLACEMENT, Destroyer=["1", "2", "h"])
    assert client.post('/placement', json=bad).status_code == 400
    assert client.post('/placement', json={'placement': PLACEMENT, 'difficulty': 'expert'}).status_code == 200


@pytest.mark.parametrize('difficulty', ['easy', 'hard', 'expert'])
def test_full_game_over_http(client, difficulty):
    random.seed(difficulty)
    client.post('/placement', json={'placement': PLACEMENT, 'difficulty': difficulty})
    assert client.get('/').status_code == 200
    cells = [(x, y) for x in range(10) for y in range(10)]
    random.shuffle(cells)
    ai_shots = set()
    finished = None
    for x, y in cells:
        data = client.get(f'/attack?x={x}&y={y}').get_json()
        if 'AI_Turn' in data:
            shot = tuple(data['AI_Turn'])
            assert 0 <= shot[0] < 10 and 0 <= shot[1] < 10
            if difficulty != 'easy':
                assert shot not in ai_shots, 'AI fired twice at the same cell'
            ai_shots.add(shot)
        if 'finished' in data:
            finished = data['finished']
            break
    assert finished in ('You Win!', 'Game Over!')
    # Firing after the game is over is refused
    assert client.get('/attack?x=0&y=0').status_code in (400, 409)


def test_repeat_shot_is_refused(client):
    client.post('/placement', json=PLACEMENT)
    client.get('/')
    assert client.get('/attack?x=3&y=3').status_code == 200
    assert client.get('/attack?x=3&y=3').status_code == 400


def _play_ai(ai, games=30):
    turns = []
    for g in range(games):
        random.seed(g)
        board = place_battleships(initialise_board(10), create_battleships(), algorithm='random')
        layout = [row[:] for row in board]
        ships = count_ships(board)
        state = {'history': [], 'probable': [(x, y) for x in range(10) for y in range(10)]}
        n = 0
        while any(ships.values()):
            coords = ai(board, layout, ships, state)
            assert board[coords[1]][coords[0]] not in ('X', 'O')
            attack(coords, board, ships)
            n += 1
            assert n <= 100
        turns.append(n)
    return sum(turns) / len(turns)


def _hunt_target(board, layout, ships, state):
    full = create_battleships()
    sunk = [(x, y) for y in range(10) for x in range(10) if layout[y][x] in ships and ships[layout[y][x]] == 0]
    sizes = [full[s] for s, n in ships.items() if n > 0]
    return generate_hunt_target_attack(board, sizes, sunk)


def _advanced(board, layout, ships, state):
    return generate_advanced_attack(board, state['history'], state['probable'])


def test_hunt_target_beats_random_by_a_mile():
    # Random play needs ~96 shots on average; hunt/target should be far better
    assert _play_ai(_hunt_target) < 65


def test_original_advanced_ai_never_crashes_or_repeats():
    assert _play_ai(_advanced) <= 100
