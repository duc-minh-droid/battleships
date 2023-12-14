from flask import Flask, request, render_template, jsonify
from components import *
from game_engine import *
from mp_game_engine import *
from game_engine import attack as process_attack

app = Flask(__name__)

@app.route('/placement', methods=['GET', 'POST'])
def placement_interface():
    if request.method == 'GET':
        # Handle GET request
        data = create_battleships()
        size = 10
        return render_template('placement.html', ships=data, board_size=size)
    elif request.method == 'POST':
        # Handle POST request
        data = request.get_json()
        with open('placement.json', 'w') as f:
            f.write(json.dumps(data)) 
        # Access form data
        return jsonify({'message': 'Received'}), 200
    
@app.route('/')
def root():
    # 2 modes: hard and easy
    global difficulty
    difficulty = 'hard'
    
    # Initializing two players' board
    global player_board
    global ai_board
    player_board = place_battleships(initialise_board(), algorithm='custom')
    if difficulty == 'easy':
        ai_board = place_battleships(initialise_board(), algorithm='random')
    elif difficulty == 'hard':
        ai_board = place_battleships(initialise_board(), algorithm='advanced')
    
    # Initializing two players' ships
    global player_ships
    global ai_ships
    player_ships = count_ships(player_board)
    ai_ships = count_ships(ai_board)
    
    # Initializing AI's attack history and probable positions
    global ai_attacks_history
    global probable_positions
    ai_attacks_history = []
    probable_positions = [(x, y) for x in range(10) for y in range(10)]
    
    return render_template('main.html', player_board=player_board)

def no_ships_remaining(ships):
    return all(value == 0 for value in ships.values())
    
@app.route('/attack')
def attack():
    # Get player's coordinates
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    
    # Retrieving global variables
    global player_board
    global ai_board
    global player_ships
    global ai_ships
    global ai_attacks_history
    global probable_positions
    global difficulty
    
    # Process player's attack
    is_hit = process_attack((x,y), ai_board, ai_ships)
    
    # AI does random attacks if difficulty is set to easy
    if difficulty == 'easy':
        ai_attack = generate_attack(player_board)
    # AI does advanced attacks if difficulty is set to hard
    elif difficulty == 'hard':
        ai_attack = generate_advanced_attack(player_board, ai_attacks_history, probable_positions)
    # Process AI's attack
    process_attack(ai_attack, player_board, player_ships)
    
    
    # Handle the End of the game
    is_finished_player_wins = no_ships_remaining(ai_ships)
    is_finished_ai_wins = no_ships_remaining(player_ships)
    
    if is_finished_player_wins:
        return jsonify({'hit': is_hit, 'AI_Turn': ai_attack, 'finished': 'You Win!'})
    elif is_finished_ai_wins:
        return jsonify({'hit': is_hit, 'AI_Turn': ai_attack, 'finished': 'Game Over!'})
    else:
        return jsonify({'hit': is_hit, 'AI_Turn': ai_attack})
    
if __name__ == '__main__':
    app.run()
