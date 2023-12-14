import random
from components import *
from game_engine import *

# Generate attack with advanced algorithms for difficulty: Hard
def generate_advanced_attack(board, history, probable_positions):
    # Update history after modifying
    def update_history(coords, direction=None):
        if not coords:
            rd_coords = process_random_attack()
            is_hit = False
            if board[rd_coords[1]][rd_coords[0]] not in [None, 'O', 'X']:
                is_hit = True
            history.append({'coords': rd_coords, 'is_hit': is_hit, 'direction': None})
        is_hit = False
        if board[coords[1]][coords[0]] not in [None, 'O', 'X']:
            is_hit = True
        history.append({'coords': coords, 'is_hit': is_hit, 'direction': direction})
    # Generate random coordinates
    def random_attack():
        while True:
            attack_coords = random.choice(probable_positions)
            if attack_coords not in [attack['coords'] for attack in history]:
                probable_positions.remove(attack_coords)
                return attack_coords
    # Get coordinates based on direction
    def get_next_coords(prev_hit_coords, direction):
        if direction == 'up':
            return prev_hit_coords[0], prev_hit_coords[1] - 1
        elif direction == 'down':
            return prev_hit_coords[0], prev_hit_coords[1] + 1
        elif direction == 'left':
            return prev_hit_coords[0] - 1, prev_hit_coords[1]
        elif direction == 'right':
            return prev_hit_coords[0] + 1, prev_hit_coords[1]
    # Check the next potential attack coordinates based on the direction of the last hit if those coordinates haven't been previously targeted
    def check_previous_hits():
    # Check if the last attack was a hit
        if history[-1]['is_hit']:
            # Get the coordinates and direction of the last attack
            last_coords = history[-1]['coords']
            last_direction = history[-1]['direction']
            
            # Get the coordinates for the next potential attack based on the last direction
            next_coords = get_next_coords(last_coords, last_direction)
            
            # Check if the next potential attack coordinates are not in the history
            if next_coords not in [attack['coords'] for attack in history]:
                return next_coords  # Return the coordinates for the next potential attack
    # Logging function for debugging
    def log(coords, message):
        new_history = history.copy()
        print("\nAI TURN: ")
        print(f"AI's previous attacks ({len(new_history)}): ", new_history)
        print('\n')
        print(message, "at coords: ", coords)
        print('\n')
    # Get a filtered history which only contains consecutive attacks
    def filter_history(history):
        new_history = history.copy()
        direction = history[-1]['direction']
        
        if direction in ['up', 'down']:
            x_value = history[-1]['coords'][0]
            new_history = [attack for attack in new_history if attack['coords'][0] == x_value]
            n_hist = [new_history[-1]]
            for idx, attack in enumerate(new_history[::-1]):
                if idx == len(new_history)-1: break
                if (new_history[len(new_history) - idx - 2]['coords'][1] + 1 == new_history[len(new_history) - idx - 1]['coords'][1]) or (new_history[len(new_history) - idx - 2]['coords'][1] - 1 == new_history[len(new_history) - idx - 1]['coords'][1]):
                    n_hist.append(new_history[len(new_history) - idx - 2])
                elif (new_history[len(new_history) - idx - 2]['coords'][1] + 1 == n_hist[-1]['coords'][1]) or (new_history[len(new_history) - idx - 2]['coords'][1] - 1 == n_hist[-1]['coords'][1]):
                    n_hist.append(new_history[len(new_history) - idx - 2])
        else:
            y_value = history[-1]['coords'][1]
            new_history = [attack for attack in new_history if attack['coords'][1] == y_value]
            n_hist = [new_history[-1]]
            for idx, attack in enumerate(new_history[::-1]):
                if idx == len(new_history)-1: break
                if (new_history[len(new_history) - idx - 2]['coords'][0] + 1 == new_history[len(new_history) - idx - 1]['coords'][0]) or (new_history[len(new_history) - idx - 2]['coords'][0] - 1 == new_history[len(new_history) - idx - 1]['coords'][0]):
                    n_hist.append(new_history[len(new_history) - idx - 2])
                elif (new_history[len(new_history) - idx - 2]['coords'][0] + 1 == n_hist[-1]['coords'][0]) or (new_history[len(new_history) - idx - 2]['coords'][0] - 1 == n_hist[-1]['coords'][0]):
                    n_hist.append(new_history[len(new_history) - idx - 2])
        return n_hist[::-1] 
    # Process the attack for random attacks
    def process_random_attack():
        attack_coords = random_attack()
        update_history(attack_coords)
        log(attack_coords, "Random attack")
        return attack_coords
    # Process the attack for attacks in opposite direction if there are multiple consecutive attacks
    def check_and_return(coords):
        for attack in history:
            if attack['coords'] == coords:
                log(coords, "Random attack")
                return process_random_attack()
        log(coords, "Shooting at opposite direction")
        update_history(coords, history[-1]['direction'])
        return coords
    # Attack logic
    while True:
            
        # First attack so shoots at random
        if len(history) == 0:
            return process_random_attack()
        # Shoot in opposite direction if there are 5 consecutive attacks
        elif len(history) >= 5 and (not history[-1]['is_hit']) and len(filter_history(history))==5:
            consecutive_attacks = filter_history(history)
            coords1 = consecutive_attacks[-5]['coords']
            coords2 = consecutive_attacks[-4]['coords']
            coords3 = consecutive_attacks[-3]['coords']
            coords4 = consecutive_attacks[-2]['coords']
            coords5 = consecutive_attacks[-1]['coords']
            # Return the coordinates of the spot behind history[-4] on the same line
            if coords1[0] == coords2[0] == coords3[0] == coords4[0] == coords5[0]:
                # Same row, shooting to the left
                if coords5[1] < coords4[1]:
                    new_coords = coords1[0], coords1[1] + 1
                # Same row, shooting to the right
                else:
                    new_coords = coords1[0], coords1[1] - 1
            else:
                # Same column, shooting upwards
                if coords5[0] < coords4[0]:
                    new_coords = coords1[0] - 1, coords1[1]
                # Same column, shooting downwards
                else:
                    new_coords = coords1[0] + 1, coords1[1]

            return check_and_return(new_coords)
        # Shoot in opposite direction if there are 4 consecutive attacks
        elif len(history) >= 4 and (not history[-1]['is_hit']) and len(filter_history(history))==4:
            consecutive_attacks = filter_history(history)
            coords1 = consecutive_attacks[-4]['coords']
            coords2 = consecutive_attacks[-3]['coords']
            coords3 = consecutive_attacks[-2]['coords']
            coords4 = consecutive_attacks[-1]['coords']
            # Return the coordinates of the spot behind history[-3] on the same line
            if coords1[0] == coords2[0] == coords3[0] == coords4[0]:
                # Same row, shooting to the left
                if coords4[1] < coords3[1]:
                    new_coords = coords1[0], coords1[1] + 1
                # Same row, shooting to the right
                else:
                    new_coords = coords1[0], coords1[1] - 1
            else:
                # Same column, shooting upwards
                if coords4[0] < coords3[0]:
                    new_coords = coords1[0] - 1, coords1[1]
                # Same column, shooting downwards
                else:
                    new_coords = coords1[0] + 1, coords1[1]

            return check_and_return(new_coords)

         # If the last three attacks follow a pattern and the recent one was a miss
        # Shoot in opposite direction if there are 3 consecutive attacks
        elif len(history) >= 3 and (not history[-1]['is_hit']) and len(filter_history(history))==3:
            consecutive_attacks = filter_history(history)
            coords1 = consecutive_attacks[-3]['coords']
            coords2 = consecutive_attacks[-2]['coords']
            coords3 = consecutive_attacks[-1]['coords']
            # Return the coordinates of the spot behind history[-3] on the same line
            if coords1[0] == coords2[0] == coords3[0]:
                # Same row, shooting to the left
                if coords3[1] < coords2[1]:
                    new_coords = coords1[0], coords1[1] + 1
                # Same row, shooting to the right
                else:
                    new_coords = coords1[0], coords1[1] - 1
            else:
                # Same column, shooting upwards
                if coords3[0] < coords2[0]:
                    new_coords = coords1[0] - 1, coords1[1]
                # Same column, shooting downwards
                else:
                    new_coords = coords1[0] + 1, coords1[1]
            return check_and_return(new_coords)

        # Last direction was wrong so picking a random one
        elif (not history[-1]['is_hit']) and history[-1]['direction'] != None:
            # Choose another direction other than the recent ones
            recent_directions = [attack['direction'] for attack in history[-3:] if attack['direction'] is not None and not attack['is_hit']]
            recent_attacks = [attack for attack in history[-3:] if attack['is_hit']]
            directions = ['up', 'down', 'left', 'right']
            for recent_dir in recent_directions:
                directions.remove(recent_dir) if recent_dir in directions else None  # Remove recent directions from available choices
            direction = random.choice(directions)
            if not recent_attacks:
                return process_random_attack()
            next_coords = get_next_coords(recent_attacks[-1]['coords'], direction)
            if next_coords in [attack['coords'] for attack in history]:
                return process_random_attack()
            update_history(next_coords, direction)
            log(next_coords, "Last direction was wrong so picking another one, shooting")
            return next_coords
        # Continues shooting at same pattern
        elif history[-1]['is_hit'] and history[-1]['direction']!=None:
            next_coords = check_previous_hits()
            update_history(next_coords,history[-1]['direction'])
            log(next_coords, "Noticed a pattern, continues to shoot")
            return next_coords
        # Chose a random direction
        elif history[-1]['is_hit'] and history[-1]['direction']==None:
            directions = ['up', 'down', 'left', 'right']
            direction = random.choice(directions)
            next_coords = get_next_coords(history[-1]['coords'], direction)
            if next_coords in [attack['coords'] for attack in history]:
                return process_random_attack()
            update_history(next_coords, direction)
            log(next_coords, "Chose a random direction, shooting")
            return next_coords 
        # Attack at random position
        else:
            return process_random_attack()
          
def generate_attack():
    board_size = 10
    prev_attacks = []

    x_max = board_size - 1
    y_max = board_size - 1
    
    # Generate random coordinates for the attack
    while True:
        x = random.randint(0, x_max)
        y = random.randint(0, y_max)
        
        # Ensure the generated coordinates hasn't existed
        if (x, y) not in prev_attacks:
            prev_attacks.append((x, y))
            return (x, y)

def all_ships_sunk(battleships):
    # Check if all ship counts are zero
    return all(count == 0 for count in battleships.values())

def ai_opponent_game_loop():
    # Welcome message
    print('Welcome to Battleships!')
    # Initialize two players' board and ships
    global players
    player_board = place_battleships(initialise_board(10), create_battleships())
    ai_board = place_battleships(initialise_board(10), create_battleships(), algorithm='random')
    players = {
        'player': {
            'board': player_board,
            'battleships': create_battleships()
        },
        'AI': {
            'board': ai_board,
            'battleships': create_battleships()
        },
    }
    
    while True:
        # Player wins if all ships are sunk and lose if AI sank all ships first
        if all_ships_sunk(players['AI']['battleships']):
            print('You win!')
            break
        elif all_ships_sunk(players['player']['battleships']):
            print('You lose!')
            break
        
        # Player's turn
        print('Your turn: ')
        # Get player's input
        coordinates = cli_coordinates_input()
        # Process the attack
        is_hit_player_attack = attack(coordinates, players['AI']['board'], players['AI']['battleships'])
        if is_hit_player_attack:
            print("You attacked at", coordinates, " and hit!\n")
        else:
            print("You attacked at", coordinates, " and missed!\n")
        print("AI's board: ",ai_board,'\n')
            
        # AI's turn
        print("AI turn: ")
        # Generate the attack and process it
        ai_attack = generate_attack()
        is_hit_ai_attack = attack(ai_attack, players['player']['board'], players['player']['battleships'])
        if is_hit_ai_attack:
            print("AI attacked at", ai_attack, " and hit!\n")
        else:
            print("AI attacked at", ai_attack, " and missed!\n")
        print("Player's board: ",player_board,'\n')
            
if __name__ == '__main__':
    global players
    players = {
        'player': {
            'board': [],
            'battleships': {}
        },
        'AI': {
            'board': [],
            'battleships': {}
        },
    }
    ai_opponent_game_loop()
    