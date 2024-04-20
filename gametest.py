import pygame
from Board import Board, Piece

myBoard = Board()
DARKBROWN = (120,69,34)
LIGHTBROWN = (222, 184, 135)

SQUARE_SIZE = 100

images = {
    'p': pygame.image.load('ChessSprites/black_pawn.png'),
    'r': pygame.image.load('ChessSprites/black_rook.png'),
    'n': pygame.image.load('ChessSprites/black_knight.png'),
    'b': pygame.image.load('ChessSprites/black_bishop.png'),
    'q': pygame.image.load('ChessSprites/black_queen.png'),
    'k': pygame.image.load('ChessSprites/black_king.png'),
    'P': pygame.image.load('ChessSprites/white_pawn.png'),
    'R': pygame.image.load('ChessSprites/white_rook.png'),
    'N': pygame.image.load('ChessSprites/white_knight.png'),
    'B': pygame.image.load('ChessSprites/white_bishop.png'),
    'Q': pygame.image.load('ChessSprites/white_queen.png'),
    'K': pygame.image.load('ChessSprites/white_king.png')
}

for piece in images:
    images[piece] = pygame.transform.scale(images[piece], (SQUARE_SIZE, SQUARE_SIZE))

def renderBoard(board, screen):

    # Parse the board string
    board = board.split('\n')
    board = [list(row) for row in board]
    
    # Render 8x8 checkerboard in pygame
    for i in range(8):
        for j in range(8):
            pygame.draw.rect(screen, DARKBROWN if (i + j) % 2 == 0 else LIGHTBROWN, (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Render pieces on the board
    for i in range(8):
        for j in range(8):
            piece = board[j][i]
            if piece in images:
                screen.blit(images[piece], (i * SQUARE_SIZE, j * SQUARE_SIZE))

def clientMove(fromX, fromY, toX, toY):
    # Check if the coordinates are within the board range
    if 0 <= fromX < 8 and 0 <= fromY < 8 and 0 <= toX < 8 and 0 <= toY < 8:
        # Get the piece at the source position
        piece = myBoard.getBoard()[fromY][fromX]
        
        # Check if the position contains a piece
        if isinstance(piece, Piece):
            # Check if the move is valid
            if piece.isValidMove((toX, toY), myBoard, piece):
                # Move the piece
                myBoard.movePiece((fromX, fromY), (toX, toY))  
            
def main():
    pygame.init()

    window_size = (SQUARE_SIZE * 8, SQUARE_SIZE * 8)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Chess")

    print(str(myBoard))

    move = [None, None]

    color = 'WHITE'

    running = True
    while running:
    # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if move[0] is None:
                    move[0] = (pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE)
                    # check if the position contains a piece of the current player's color
                    piece = myBoard.getBoard()[move[0][1]][move[0][0]]
                    if isinstance(piece, Piece) and piece.color == color:
                        print("Piece selected", move[0])
                        print("Polling")
                        print(piece.poll(myBoard))
                    else:
                        move[0] = None

                else:
                    move[1] = (pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE)
                    clientMove(move[0][0], move[0][1], move[1][0], move[1][1])
                    move = [None, None]
                    color = 'BLACK' if color == 'WHITE' else 'WHITE'
                    if myBoard.isCheck(color):
                        print(f"{color} is in check!")
        
    
        renderBoard(str(myBoard), window)
        
        pygame.display.flip()
pygame.quit()

if __name__ == '__main__':
    main()