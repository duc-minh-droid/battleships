import random
import json

def initialise_board(size=10):
    return [[None for _ in range(size)] for _ in range(size)]

def get_ship_size(ship_name):
    with open('battleships.txt', 'r') as file:
        for line in file:
            name, size = line.strip().split(':')
            if name == ship_name:
                return int(size)
    return None

def create_battleships(filename='battleships.txt'):
    battleships = {}
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            name, size = line.split(':')
            battleships[name] = int(size)
    return battleships
        
def place_battleships(board, ships=None,algorithm='simple'):
    def place_large_ships(board, ships):
        large_ships = [{'name':ship,'size':ships[ship]} for ship in ships if ships[ship] > 3]  # Assuming ships larger than 2 as 'large'
        for large_ship in large_ships:
            place_ship(board, large_ship['size'], large_ship['name'])
    def place_small_ships(board, ships):
        small_ships = [{'name':ship,'size':ships[ship]} for ship in ships if ships[ship] <= 3]  # Assuming ships of size 2 or smaller as 'small'
        for small_ship in small_ships:
            place_ship(board, small_ship['size'], small_ship['name'])
    def check_valid_placement(board, x, y, size, orientation):
        board_size = len(board)
        if orientation == 'horizontal':
            return y + size <= board_size and all(board[x][y + i] is None for i in range(size))
        else:
            return x + size <= board_size and all(board[x + i][y] is None for i in range(size))
    def place_ship(board, size, name):
        board_size = len(board)
        orientation = random.choice(['horizontal', 'vertical'])
        attempts = 0
        while attempts < 100:  # Limiting attempts to avoid infinite loops
            x = random.randint(0, board_size - 1)
            y = random.randint(0, board_size - 1)
            if check_valid_placement(board, x, y, size, orientation):
                for i in range(size):
                    if orientation == 'horizontal':
                        board[x][y+i] = name
                    else:
                        board[x+i][y] = name
                break
            attempts += 1

    player_board = board
    board_size = len(board)
    
    ships = create_battleships()
    if algorithm == 'simple':
        if ships is not None:
            for i, (ship, size) in enumerate(ships.items()):
                for j in range(size):
                    # Place each ship on successive lines of the board
                    player_board[i][j] = ship
    if algorithm == 'random':
        for ship, size in ships.items():
            # Randomly select orientation (horizontal or vertical)
            is_horizontal = random.choice([True, False])
            
            if is_horizontal:
                while True:
                    # Randomly generate a position for the ship
                    start_x = random.randint(0, board_size - 1)
                    start_y = random.randint(0, board_size - size)
                    
                    # Check if the positions are empty
                    positions_empty = all(player_board[start_y + k][start_x] is None for k in range(size))
                    
                    if positions_empty:
                        # Place the ship horizontally
                        for k in range(size):
                            player_board[start_y + k][start_x] = ship
                        break
            else:
                while True:
                    # Randomly generate a position for the ship
                    start_x = random.randint(0, board_size - size)
                    start_y = random.randint(0, board_size - 1)
                    
                    # Check if the positions are empty
                    positions_empty = all(player_board[start_y][start_x + k] is None for k in range(size))
                    
                    if positions_empty:
                        # Place the ship vertically
                        for k in range(size):
                            player_board[start_y][start_x+k] = ship
                        break
    if algorithm == 'custom':
        with open('placement.json') as f:
                placement_data = json.load(f)
                for ship in placement_data:
                    info = placement_data[ship]
                    x = int(info[0])
                    y = int(info[1])
                    orientation = info[2]
                    size = get_ship_size(ship)

                    if orientation == 'h':
                        if x + size <= len(player_board[0]):  # Check if ship fits horizontally
                            if all(player_board[y][x + k] is None for k in range(size)):
                                for k in range(size):
                                    player_board[y][x + k] = ship
                            else:
                                print(f"Can't place {ship} horizontally at {x}, {y}.")
                        else:
                            print(f"Can't place {ship} horizontally at {x}, {y}. Out of board bounds.")
                            
                    elif orientation == 'v':
                        if y + size <= len(player_board):  # Check if ship fits vertically
                            if all(player_board[y + k][x] is None for k in range(size)):
                                for k in range(size):
                                    player_board[y + k][x] = ship
                            else:
                                print(f"Can't place {ship} vertically at {x}, {y}.")
                        else:
                            print(f"Can't place {ship} vertically at {x}, {y}. Out of board bounds.")
    if algorithm == 'advanced':
        place_large_ships(board, ships)
        place_small_ships(board, ships)

    return player_board
            
if __name__ == '__main__':
    board = initialise_board(10)
    ships = create_battleships()
    player_board = place_battleships(board, ships, algorithm='random')
    print(player_board)