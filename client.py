import socket
import threading
import pygame

HOST = "localhost"
PORT = 4747

color = None

DARKBROWN = (120, 69, 34)
LIGHTBROWN = (222, 184, 135)
BLUE = (0, 127, 255)
RED = (224, 60, 49)

SQUARE_SIZE = 100
BORDER_SIZE = 5

board = None
message = None
moveMade = False
myTurn = False
gameOver = None

polledMoves = None

pieces = {
    "p": "BLACK",
    "r": "BLACK",
    "n": "BLACK",
    "b": "BLACK",
    "q": "BLACK",
    "k": "BLACK",
    "P": "WHITE",
    "R": "WHITE",
    "N": "WHITE",
    "B": "WHITE",
    "Q": "WHITE",
    "K": "WHITE",
}

images = {
    "p": pygame.image.load("ChessSprites/black_pawn.png"),
    "r": pygame.image.load("ChessSprites/black_rook.png"),
    "n": pygame.image.load("ChessSprites/black_knight.png"),
    "b": pygame.image.load("ChessSprites/black_bishop.png"),
    "q": pygame.image.load("ChessSprites/black_queen.png"),
    "k": pygame.image.load("ChessSprites/black_king.png"),
    "P": pygame.image.load("ChessSprites/white_pawn.png"),
    "R": pygame.image.load("ChessSprites/white_rook.png"),
    "N": pygame.image.load("ChessSprites/white_knight.png"),
    "B": pygame.image.load("ChessSprites/white_bishop.png"),
    "Q": pygame.image.load("ChessSprites/white_queen.png"),
    "K": pygame.image.load("ChessSprites/white_king.png"),
}

for piece in images:
    images[piece] = pygame.transform.scale(images[piece], (SQUARE_SIZE, SQUARE_SIZE))


def renderBoard(screen):
    global board

    # Render 8x8 checkerboard in pygame
    for i in range(8):
        for j in range(8):
            pygame.draw.rect(
                screen,
                DARKBROWN if (i + j) % 2 == 0 else LIGHTBROWN,
                (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )

    # Render pieces on the board
    if board is not None:
        for i in range(8):
            for j in range(8):
                piece = board[j][i]
                if piece in images:
                    screen.blit(images[piece], (i * SQUARE_SIZE, j * SQUARE_SIZE))
                    
    if polledMoves is not None and len(polledMoves) > 0:
        # Draw border around polled moves
        for move in polledMoves:
            if color == "WHITE":
                move = (move[0], 7 - move[1])
            # Get piece at the position
            piece = board[move[1]][move[0]]
            # Draw red border if the piece is a capture
            if piece in pieces:
                pygame.draw.rect(screen, RED, (move[0] * SQUARE_SIZE, move[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), BORDER_SIZE)
            else:
                pygame.draw.rect(screen, BLUE, (move[0] * SQUARE_SIZE, move[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), BORDER_SIZE)
                
    if gameOver is not None:
        font = pygame.font.Font(None, 100)
        # Render blue for win, red for lose
        if gameOver == 'WIN':
            text = font.render(f"Game Over: You Win!", True, BLUE)
        else:
            text = font.render(f"Game Over: You Lose!", True, RED)
            
        textRect = text.get_rect(center=(SQUARE_SIZE * 4, SQUARE_SIZE * 4))
        screen.blit(text, textRect)


# Function to flip the board if the player is white
# White starts at (0, 0) position, which would be the top of the board
# Simple solution is to flip the board so each player sees their pieces closest to them
def flipBoard():
    global board
    for i in range(4):
        board[i], board[7 - i] = board[7 - i], board[i]
        
def convertPolledMove(polledMovesStr):
    # Convert string to list of tuples
    # polledMovesStr looks like [(0, 1), (2, 3), (4, 5)]
    
    if polledMovesStr == "[]":
        return []
    
    polledMovesStr = polledMovesStr.replace("Polled: ", "")
    
    # Remove brackets
    polledMovesStr = polledMovesStr.replace("[", "")
    polledMovesStr = polledMovesStr.replace("]", "")
    
    # Remove parenthesis
    polledMovesStr = polledMovesStr.replace("(", "")
    polledMovesStr = polledMovesStr.replace(")", "")
    
    # Remove spaces and commas
    polledMovesStr = polledMovesStr.replace(" ", "")
    polledMovesStr = polledMovesStr.split(",")
    
    polledMoves = []
    
    for i in range(0, len(polledMovesStr), 2):
        polledMoves.append((int(polledMovesStr[i]), int(polledMovesStr[i + 1])))
        
    return polledMoves

def receiveBoardState(s):
    global color
    global board
    global moveMade
    global message
    global myTurn
    global move
    global polledMoves
    global gameOver
    
    color = s.recv(4096).decode()
    if not color:
        return

    print("Color is", color)

    # Write to server "Color received"
    s.sendall("Color received".encode())

    # Receive the initial board state
    data = s.recv(4096).decode()
    if not data:
        return

    print("Received data\n", data, sep="")

    board = [list(row) for row in data.split("\n")]

    # Flip the board if the player is white
    if color == "WHITE":
        flipBoard()

    # Write to server "Color received"
    s.sendall("Board received".encode())

    while True:
        # Get message
        if not moveMade:
            data = s.recv(4096).decode()
            if not data:
                break  # Break if the server terminates
            
        print("Data is:\n", data, sep="")
            
        if "Checkmate" in data:
            print("Checkmate")
            gameOver = 'LOSE'
            break
        elif "You win" in data:
            print("You win")
            gameOver = 'WIN'
            break

        if "Your turn" in data or myTurn:
            print("My turn")
            myTurn = True
            
            if "Check!" in data:
                print("Check!")
            
            # Wait for the player to make a move or poll
            while not moveMade or not message:
                continue
            
            s.sendall(message.encode())
            print("Sent message", message)
            
            # Get confirmation the move was valid
            data = s.recv(4096).decode()
            if not data:
                break  # Break if the server terminates
            
            print("Received data\n", data, sep="")
 
            if data == "Valid move":
                moveMade = False
                myTurn = False
                
                # Send confirmation
                s.sendall("Move received".encode())
                
            elif "Polled" in data:
                # Get the polled moves
                data = data.replace("Polled: ", "")
                polledMoves = convertPolledMove(data)
                print(len(polledMoves), polledMoves)
                moveMade = False
                
                # Send confirmation
                s.sendall("Client polled".encode())
                                
            else:
                print("Invalid move, try again")
                move = [None, None]
                message = None
                moveMade = False
                continue

        # Otherwise, just print the chess board
        else:
            # Parse the board string
            board = [list(row) for row in data.split("\n")]
            # Flip the board if the player is white
            if color == "WHITE":
                flipBoard()


def connectToServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    receiveBoardState(s)
    s.close()


def pygameMain():
    pygame.init()

    window_size = (SQUARE_SIZE * 8, SQUARE_SIZE * 8)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Chess")

    move = [None, None]

    global message
    global moveMade
    global board
    global color
    global myTurn
    global polledMoves

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and myTurn:
                # Get the click position
                pos = pygame.mouse.get_pos()
                pos = (pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE)
                    
                # Get the piece selected
                piece = board[pos[1]][pos[0]]
                
                # Flip if white
                if color == "WHITE":
                    pos = (pos[0], 7 - pos[1])
                
                print("Pos is", pos)
                print("Piece is", piece)
                
                # If it's your color, get the poll and note which piece was selected
                if piece in pieces and pieces[piece] == color:
                    move[0] = pos
                    print("From move", move[0])
                    message = f"Polling {move[0][0]} {move[0][1]}"
                    print("Asking to poll", move[0])
                    moveMade = True
                else:
                    if move[0] is not None and polledMoves is not None:
                        # Only allow the player to move to a polled position
                        if pos in polledMoves:
                        
                            move[1] = pos   
                                
                            message = f"{move[0][0]} {move[0][1]} {move[1][0]} {move[1][1]}"
                            moveMade = True
                            move = [None, None]
                            polledMoves = None

        renderBoard(window)

        pygame.display.flip()


pygame.quit()


def main():

    receiveThread = threading.Thread(target=connectToServer)
    receiveThread.start()

    # don't execute main loop until the board is received
    while board is None:
        continue
    print("\nBoard received, running pygame\n")
    pygameMain()


if __name__ == "__main__":
    main()
