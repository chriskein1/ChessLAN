import socket
import threading
from Board import Board, Piece

HOST = 'localhost'
PORT = 4747

# Chess board object
board = Board()

# Current turn
turn = 'WHITE'

# Global clients
clientWhite = None
clientBlack = None

gameOver = False

def clientMove(fromX, fromY, toX, toY):
    # Check if the coordinates are within the board range
    if 0 <= fromX < 8 and 0 <= fromY < 8 and 0 <= toX < 8 and 0 <= toY < 8:
        # Get the piece at the source position
        piece = board.board[fromY][fromX]
        
        # Check if the position contains a piece
        if isinstance(piece, Piece):
            # Check if the move is valid
            # if piece.isValidMove((toX, toY), board, piece):
            # Move the piece
            board.movePiece((fromX, fromY), (toX, toY)) 
            return True          
    return False


def broadcastBoard():
    global clientWhite, clientBlack
    clientWhite.sendall(str(board).encode())
    clientBlack.sendall(str(board).encode())

def clientThread(client, color):
    # Sent the color to the client
    client.sendall(color.encode())
    
    # Make sure the client is ready to receive the board
    data = client.recv(4096).decode()
    if data != "Color received":
        return

    # Send initial board to all clients
    broadcastBoard()
    
    data = client.recv(4096).decode()
    if data != "Board received":
        return

    global turn
    global gameOver

    while True:
        if color == turn:
            if board.isCheckmate(color):
                print(f"{color} is in checkmate!")
                gameOver = True
                client.sendall("Checkmate! You lose".encode())
                break
            elif board.isCheck(color):
                print(f"{color} is in check!")
                client.sendall("Check! Your turn".encode())
            else:
                print(f"Sending {color} 'Your turn'")
                client.sendall(f"Your turn".encode())

            # Receive message from the client
            data = client.recv(4096).decode()
            if not data:
                break
                    
            data = data.replace(" ", "")
            
            if "Polling" in data:
                data = data.replace("Polling", "")
                print("Received Polling for ", color, data[0], data[1])
                polledMoves = board.pollPiece((int(data[0]), int(data[1])))
                message = "Polled: " + str(polledMoves)
                print("Sending", message)
                client.sendall(message.encode())
                
                # Receive confirmation
                data = client.recv(4096).decode()
                if data != "Client polled":
                    return
                print("Client polled")
                
                continue
            
            fromX = int(data[0])
            fromY = int(data[1])
            toX = int(data[2])
            toY = int(data[3])

            print(f"Received move for {color}:", fromX, fromY, toX, toY)

            # Perform move and update the board
            validMove = clientMove(fromX, fromY, toX, toY)

            if not validMove:
                client.sendall("Invalid move".encode())
                continue
            else:
                client.sendall("Valid move".encode())
                
            # Get confirmation
            data = client.recv(4096).decode()
            if data != "Move received":
                return

            # Broadcast the updated board to all clients
            broadcastBoard()
            
            # Switch turn
            turn = 'BLACK' if turn == 'WHITE' else 'WHITE'
        elif gameOver:
            print(f"{color} wins!")
            client.sendall("You win!".encode())
            break

def main():
    global clientWhite, clientBlack

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        clients = 0
        while clients < 2:
            client, addr = s.accept()
            print(f'Connected by {addr}')
            if clients == 0:
                clientWhite = client
                whiteThread = threading.Thread(target=clientThread, args=(client,'WHITE',))
            else:
                clientBlack = client
                blackThread = threading.Thread(target=clientThread, args=(client,'BLACK',))
            clients += 1

        whiteThread.start()
        blackThread.start()


if __name__ == '__main__':
    main()