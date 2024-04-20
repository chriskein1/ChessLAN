# Chess board class
class Board:
    def __init__(self):
        # Place the each piece object on the board
        self.board = [[Rook('WHITE', (0, 0)), Knight('WHITE', (1, 0)), 
                       Bishop('WHITE', (2, 0)), Queen('WHITE', (3, 0)), 
                       King('WHITE', (4, 0)), Bishop('WHITE', (5, 0)), 
                       Knight('WHITE', (6, 0)), Rook('WHITE', (7, 0))],
                      [Pawn('WHITE', (i, 1)) for i in range(8)],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [Pawn('BLACK', (i, 6)) for i in range(8)],
                      [Rook('BLACK', (0, 7)), Knight('BLACK', (1, 7)), 
                       Bishop('BLACK', (2, 7)), Queen('BLACK', (3, 7)), 
                       King('BLACK', (4, 7)), Bishop('BLACK', (5, 7)), 
                       Knight('BLACK', (6, 7)), Rook('BLACK', (7, 7))]]
        
    def __str__(self):
        boardStr = ""
        for i in range(8):
            for j in range (8):
                boardStr += str(self.board[i][j])
            boardStr += '\n'

        return boardStr
    
    def getBoard(self):
        return self.board        
     
    def printBoard(self):
        # Print column labels
        print("  ", end="")  # Offset for row numbers
        for col in range(8):
            print(chr(col + ord('A')), end=" ")
        print()  # Newline after printing column labels
    
        # Print row numbers and board contents
        for i in range(8):
            print(i + 1, end=" ")  # Row number
            for j in range(8):
                print(str(self.board[i][j]), end=' ')
            print()  # Newline after printing row contents
        
    def movePiece(self, oldPos, newPos):
        # Get piece at oldPos
        piece = self.board[oldPos[1]][oldPos[0]]
        
        # Castling
        if isinstance(piece, King):
            # Short castle
            if newPos == (oldPos[0] - 2, oldPos[1]):
                rook = self.board[oldPos[1]][0]
                self.board[oldPos[1]][3] = rook
                rook.move((oldPos[0] - 1, oldPos[1]))
                self.board[oldPos[1]][0] = ' '
            # Long castle
            elif newPos == (oldPos[0] + 2, oldPos[1]):
                rook = self.board[oldPos[1]][7]
                self.board[oldPos[1]][5] = rook
                rook.move((oldPos[0] + 1, oldPos[1]))
                self.board[oldPos[1]][7] = ' '
            
        
        # Move piece to newPos
        self.board[newPos[1]][newPos[0]] = piece

        piece.move(newPos)

        # Clear old position
        self.board[oldPos[1]][oldPos[0]] = ' '
        
    def findKing(self, color):
        for row in self.board:
            for piece in row:
                if isinstance(piece, King) and piece.getColor() == color:
                    return piece.getPos()
        
    def isCheck(self, color):
            # Find the king of the specified color
            kingPos = self.findKing(color)
            
            # Check if a piece is attacking the king
            for row in self.board:
                for piece in row:
                    if isinstance(piece, Piece) and piece.getColor() != color:
                        # print(f"Checking if {piece} can attack the {color} king at {kingPos}")
                        if piece.canAttack(self, kingPos):
                            # print(f"{piece} can attack the {color} king at {kingPos}")
                            return True                    
            return False
        
    def isCheckmate(self, color):
        # Find the king of the specified color
        kingPos = self.findKing(color)
        
        # Check if the king is in check
        if not self.isCheck(color):
            return False
        
        # Check if the king can move to a safe square
        king = self.board[kingPos[1]][kingPos[0]]
        if king.poll(self):
            return False
        
        # Check if any piece can capture the attacking piece
        for row in self.board:
            for piece in row:
                if isinstance(piece, Piece) and piece.getColor() == color:
                    for move in piece.poll(self):
                        if self.isMoveCheck(piece, move):
                            return False
        
        return True
    
    # Function to simulate a move
    def __simulateMove(self, piece, newPos):
        originalPos = piece.getPos()
        tempPiece = self.board[newPos[1]][newPos[0]]
        
        # Move the piece to the new position
        self.board[newPos[1]][newPos[0]] = piece
        piece.changePos(newPos)
        
        # Clear the old position
        self.board[originalPos[1]][originalPos[0]] = ' '
        
        return tempPiece


    def __undoMove(self, piece, originalPos, newPos, tempPiece):
        # Move the piece back to its original position
        self.board[originalPos[1]][originalPos[0]] = piece
        
        # Update the piece's position
        piece.changePos(originalPos)
        
        # Restore the piece that was replaced at the new position
        self.board[newPos[1]][newPos[0]] = tempPiece

        
    # Function to check if a potential move will put the king in check
    def isMoveCheck(self, piece, newPos):
        originalPos = piece.getPos()
        # Simulate the move
        # print("BEFORE SIMULATED MOVE")
        self.printBoard()
        # print("PIECE IS AT", piece.getPos())
        tempPiece = self.__simulateMove(piece, newPos)
        # print("SIMULATED MOVE TO", piece.getPos())
        
        self.printBoard()

        # Check if the king of this color is in check
        isCheck = self.isCheck(piece.getColor())
        
        # Undo the move
        self.__undoMove(piece, originalPos, newPos, tempPiece)
        
        # print("UNDO MOVE TO", piece.getPos())
        
        return isCheck
    
    def pollPiece(self, pos):
        piece = self.board[pos[1]][pos[0]]
        if isinstance(piece, Piece):
            return piece.poll(self)
        return []

# Generic Piece class
class Piece():
    # Constructor, color is either white or black, pos is (x, y)
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos

    # Generic move function
    def move(self, newPos):
        self.pos = newPos
    
    # To be used when simulating moves
    # subclasses may have a first move attribute   
    def changePos(self, newPos):
        self.pos = newPos

    def isValidMove(self, newPos, board, piece):                
        # Check if move is in poll
        return newPos in piece.poll(board)
    
    # Poll will return all the valid moves for the piece
    # Implemented by subclasses
    def poll(self, board):
        pass
    
    def addPotentialMove(self, validMoves, potentialMove, board):
        chessBoard = board.getBoard()
        if (potentialMove[0] < 8 and potentialMove[0] >= 0 
            and potentialMove[1] < 8 and potentialMove[1] >= 0):
            piece = chessBoard[potentialMove[1]][potentialMove[0]] 
            if ((not isinstance(piece, Piece) or piece.getColor() != self.color)
                and not self.pieceBetween(chessBoard, potentialMove)):
                if not board.isMoveCheck(self, potentialMove):
                    # print("Move", potentialMove, "is valid")
                    validMoves.append(potentialMove)            
                    
    def addKnightMove(self, validMoves, potentialMove, board):
        chessBoard = board.getBoard()
        if (potentialMove[0] < 8 and potentialMove[0] >= 0 
            and potentialMove[1] < 8 and potentialMove[1] >= 0):
            piece = chessBoard[potentialMove[1]][potentialMove[0]] 
            if ((not isinstance(piece, Piece) or piece.getColor() != self.color)
                and not board.isMoveCheck(self, potentialMove)):
                validMoves.append(potentialMove)
                
    def canAttack(self, board, pos):
        pass
    
    # Getters
    def getColor(self):
        return self.color
    
    def getPos(self):
        return self.pos
    
    def __str__(self):
        return self.char
    
    # Check the vertical/horizontal axis
    def checkAxis(self, board, pos):
        x, y = self.getPos()
        pos_x, pos_y = pos
        
        # Check horizontal direction
        if y == pos_y:
            step = 1 if x < pos_x else -1
            for i in range(x + step, pos_x, step):
                piece = board[y][i]
                if isinstance(piece, Piece):
                    # print("Piece in horizontal direction")
                    return False

        # Check vertical direction
        elif x == pos_x:
            step = 1 if y < pos_y else -1
            for j in range(y + step, pos_y, step):
                piece = board[j][x]
                if isinstance(piece, Piece):
                    # print("Piece in vertical direction")
                    return False

        return True

        
        
    # Check the diagonals 
    def checkDiagonal(self, board, pos):
        x, y = self.getPos()
        pos_x, pos_y = pos

        dx = pos_x - x
        dy = pos_y - y
        if abs(dx) != abs(dy):
            return True  # Not diagonal

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1

        for i in range(1, abs(dx)):
            check_x = x + step_x * i
            check_y = y + step_y * i
            piece = board[check_y][check_x]
            if isinstance(piece, Piece):
                # print("Piece on diagonal")
                return False

        return True

        
        
    def pieceBetween(self, board, pos):
        x, y = self.getPos()
        pos_x, pos_y = pos

        if (x, y) == pos:
            return False

        if x == pos_x or y == pos_y:
            return not self.checkAxis(board, pos)
        elif abs(pos_x - x) == abs(pos_y - y):
            return not self.checkDiagonal(board, pos)

# Pawn class
class Pawn(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.firstMove = True
        
        # Determine pawn direction
        self.direction = 1 if self.color == 'WHITE' else -1
        
        # Character representation of the pawn, to be sent by server
        self.char = 'P' if color == 'WHITE' else 'p'
    
    def move(self, newPos):
        # Set firstMove to false if pawn has moved
        if self.firstMove:
            self.firstMove = False
        
        # Call parent move function
        super().move(newPos)
        
    # Poll will return all the valid moves for the piece as a list
    def poll(self, board):
        validMoves = []
        x, y = self.pos
        
        chessBoard = board.getBoard()
        
        # Pawn moves forward
        if self.firstMove:
            potentialMove = (x, y + 2 * self.direction)
            # Can't capture two squares ahead
            if not isinstance(chessBoard[potentialMove[1]][potentialMove[0]], Piece):
                self.addPotentialMove(validMoves, potentialMove, board)
        
        # Prevent pawn from moving forward if there is a piece in front
        if chessBoard[y + self.direction][x] == ' ':
            potentialMove = (x, y + self.direction)
            self.addPotentialMove(validMoves, potentialMove, board)
        
        # Pawn captures diagonally
        for dx in [-1, 1]:
            potentialMove = (x + dx, y + self.direction)
            if (potentialMove[0] < 8 and potentialMove[0] >= 0 
                and potentialMove[1] < 8 and potentialMove[1] >= 0):
                piece = chessBoard[potentialMove[1]][potentialMove[0]]
            else:
                continue
            if isinstance(piece, Piece) and piece.getColor() != self.color:
                if not board.isMoveCheck(self, potentialMove):
                    validMoves.append(potentialMove)
        
        return validMoves
    
    # Check if the next capture is the pos
    def canAttack(self, board, pos):
        x, y = self.getPos()
        return (x + 1, y + self.direction) == pos or (x - 1, y + self.direction) == pos
        
class Rook(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.char = 'R' if color == 'WHITE' else 'r'
        self.firstMove = True
        
    def move(self, newPos):
        if self.firstMove:
            self.firstMove = False
            
        # Call parent move function
        super().move(newPos)
        
    # Poll will return all the valid moves for the piece as a list
    def poll(self, board):
        validMoves = []
        x, y = self.pos
                
        # Rook moves horizontally
        for dx in range(-7, 8):
            potentialMove = (x + dx, y)
            self.addPotentialMove(validMoves, potentialMove, board)
        
        # Rook moves vertically
        for dy in range(-7, 8):
            potentialMove = (x, y + dy)
            self.addPotentialMove(validMoves, potentialMove, board)
            
        return validMoves
    
    def canAttack(self, board, pos):
        x, y = self.getPos()
        if not self.pieceBetween(board.getBoard(), pos):
            return x == pos[0] or y == pos[1]
        
        # Check if the king is one square away
        if abs(x - pos[0]) + abs(y - pos[1]) == 1:
            return True
        return False
    
    # To be used by the king's poll function to castle
    def isFirstMove(self):
        return self.firstMove
    

class Knight(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.char = 'N' if color == 'WHITE' else 'n'
        
    # Poll will return all the valid moves for the piece as a list
    def poll(self, board):
        validMoves = []
        x, y = self.pos    
    
        # Knight moves in L shapes
        for dx in [-2, -1, 1, 2]:
            for dy in [-2, -1, 1, 2]:
                if abs(dx) + abs(dy) == 3:
                    potentialMove = (x + dx, y + dy)
                    self.addKnightMove(validMoves, potentialMove, board)
        
        return validMoves
    
    def canAttack(self, board, pos):
        x, y = self.getPos()
        return (abs(x - pos[0]) == 2 and abs(y - pos[1]) == 1) or (abs(x - pos[0]) == 1 and abs(y - pos[1]) == 2)
    
class Bishop(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.char = 'B' if color == 'WHITE' else 'b'
        
    def poll(self, board):
        validMoves = []
        x, y = self.pos
        
        # Bishop moves diagonally
        for dx in range(-7, 8):
            for dy in range(-7, 8):
                if abs(dx) == abs(dy):
                    potentialMove = (x + dx, y + dy)
                    self.addPotentialMove(validMoves, potentialMove, board)
            
        return validMoves
    
    def canAttack(self, board, pos):
        x, y = self.getPos()
        if not self.pieceBetween(board.getBoard(), pos):
            return abs(x - pos[0]) == abs(y - pos[1])
        
        # Check if the king is one square away
        return abs(x - pos[0]) + abs(y - pos[1]) == 1
    

class Queen(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.char = 'Q' if color == 'WHITE' else 'q'
        
    def poll(self, board):
        validMoves = []
        x, y = self.pos
        
        # Define directional increments
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        
        # Iterate through directions
        for dx, dy in directions:
            for i in range(1, 8):  # Maximum range for the board size
                potentialMove = (x + dx * i, y + dy * i)
                # Check if the potential move is valid
                if not (0 <= potentialMove[0] < 8 and 0 <= potentialMove[1] < 8):
                    break  # Out of board bounds
                piece = board.getBoard()[potentialMove[1]][potentialMove[0]]
                if not isinstance(piece, Piece) or piece.getColor() != self.color:
                    if not board.isMoveCheck(self, potentialMove):
                        validMoves.append(potentialMove)
                    if isinstance(piece, Piece):
                        break  # Stop searching in this direction if a piece is encountered
                else:
                    break  # Stop searching in this direction if a piece of the same color is encountered
        
        return validMoves
    def canAttack(self, board, pos):
        x, y = self.getPos()
        if not self.pieceBetween(board.getBoard(), pos):
            return (x == pos[0] or y == pos[1] or abs(x - pos[0]) == abs(y - pos[1]))
        
        # Check if the king is one square away
        return abs(x - pos[0]) + abs(y - pos[1]) == 1
        
class King(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.char = 'K' if color == 'WHITE' else 'k'
        self.firstMove = True
        
    def move(self, newPos):
        if self.firstMove:
            self.firstMove = False
            
        # Call parent move function
        super().move(newPos)
        
    def poll(self, board):
        validMoves = []
        x, y = self.pos
        
        # King moves one square in any direction
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                potentialMove = (x + dx, y + dy)
                self.addPotentialMove(validMoves, potentialMove, board) 
                
        # Castling
        if self.firstMove:
            # Make sure the king is not in check
            if not board.isCheck(self.color):
                # White rooks are at (0,0) and (7,0)
                # Black rooks are at (0,7) and (7,7)
                row = 0 if self.color == 'WHITE' else 7
                # Check if the rooks are at their initial positions
                rooks = [board.getBoard()[row][0], board.getBoard()[row][7]]
                # Check if the rooks have not moved
                for rook in rooks:
                    if isinstance(rook, Rook) and rook.isFirstMove():
                        # Check if there are no pieces between the king and rook
                        if not self.pieceBetween(board.getBoard(), rook.getPos()):
                            # Short castle
                            if rook.getPos()[0] == 0:
                                if not board.isMoveCheck(self, (x - 1, y)) and not board.isMoveCheck(self, (x - 2, y)):
                                    validMoves.append((x - 2, y))
                            # Long castle
                            else:
                                if not board.isMoveCheck(self, (x + 1, y)) and not board.isMoveCheck(self, (x + 2, y)):
                                    validMoves.append((x + 2, y))
                
        return validMoves
    
    def canAttack(self, board, pos):
        x, y = self.getPos()
        return abs(x - pos[0]) <= 1 and abs(y - pos[1]) <= 1