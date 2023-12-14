from components import *

def count_ships(board):
    # Initialize a dictionary to count the occurrences of each ship
    ship_count = {}

    # Iterate through each row in the board
    for row in board:
        # Iterate through each cell in the row
        for cell in row:
            # Check if the cell represents a ship ('X' means hit, 'O' means miss, None is empty cell)
            if cell not in ['X', 'O', None]:
                # Increment the count for the current ship if it's already in the dictionary
                if cell in ship_count:
                    ship_count[cell] += 1
                # If the ship isn't in the dictionary, add it and set the count to 1
                else:
                    ship_count[cell] = 1

    return ship_count

def attack(coordinates, board, battleships):
    # Extract the x and y coordinates
    x, y = coordinates
    
    # Loop through each row of the board
    for i in range(len(board)):
        # Loop through each cell in the row
        for j in range(len(board[i])):
            # Check if the current cell matches the attack coordinates
            if i == x and j == y:
                # If the cell is empty, mark it as a miss ('O')
                if board[i][j] is None:
                    board[x][y] = 'O'
                    return False  # Indicate a miss
                # If the cell is already marked as hit ('X') or miss ('O'), return False
                elif board[i][j] == 'O' or board[i][j] == 'X':
                    return False  # Indicate a previously attacked cell
                else:
                    # A ship is hit, decrement its count in battleships
                    ship = board[i][j]
                    battleships[ship] -= 1
                    # Mark the cell as hit ('X')
                    board[x][y] = 'X'
                    return True  # Indicate a successful hit

def cli_coordinates_input():
    while True:
        try:
            # Ask the user to input x and y coordinates separately
            x = int(input("Enter x coordinate for attack: "))
            y = int(input("Enter y coordinate for attack: "))
            print('\n')
            # Return the coordinates as a tuple
            return (x, y)
        
        except ValueError:
            print("Please enter valid integer coordinates.")

def all_ships_sunk(battleships):
    # Check if all ship counts are zero
    return all(count == 0 for count in battleships.values())

def simple_game_loop():
    # Welcome message
    print("Welcome to Battleship!")
    # Initialize player's ships and board
    ships = create_battleships()
    player_board = place_battleships(initialise_board(10) , ships, algorithm='advanced')
    print(player_board)
    return
    while True:
        # Player wins if all ships are sunk
        if all_ships_sunk(ships):
            print("Game Over!")
            break
        # Get player's input
        coordinates = cli_coordinates_input()
        # Process the attack
        is_hit = attack(coordinates, player_board, ships)
        if is_hit:
            print("You attacked at",coordinates, ' and hit')
        else:
            print("You attacked at",coordinates, ' and missed')
        print("Player's board: ",player_board)

if __name__ == "__main__":
    simple_game_loop()