"""
--> main driver file
--> handle input data
--> display current GameState object
"""
import pygame as p
from MyChess import ChessEngine
from MyChess import SmartMoves

WIDTH = HEIGHT = 480  # can use 400
DIMENSION = 8  # 8x8 board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animation
IMAGES = {}
COLORS = [p.Color('light gray'), p.Color('dark gray')]
'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
'''
main driver for our code. This will handle user input and updating the graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()  # store all current valid moves
    moveMade = False  # flag for move made
    loadImages()  # only once
    light = "light gray"
    dark = "dark gray"
    running = True
    animate = False
    gameOver = False
    playerOne = True  # if white is human this is True
    playerTwo = True  # if black is human this is True
    sqSelected = ()  # no square selected initially (row, col)
    playerClicks = []  # [(xi, yi), (xf, yf)]
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x, y) location of mouse click
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # selecting same square twice
                        sqSelected = ()  # ignore double clicks
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:  # two clicks done
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        print(move.getChessNotations())
                        print(move.moveID)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if validMoves[i].isPawnPromotion:
                                    print("Enter choice\nRook : R\nBishop : B\nKnight : N\nQueen : Any else key")
                                    pieceInput = True
                                    while pieceInput:
                                        promoteEvent = p.event.wait()
                                        if promoteEvent.type == p.QUIT:
                                            pieceInput = False
                                        elif promoteEvent.type == p.KEYDOWN:
                                            pieceInput = False
                                            if promoteEvent.key == p.K_r:
                                                print("you chose Rook")
                                                validMoves[i].promoteTo = 'R'
                                            elif promoteEvent.key == p.K_b:
                                                print("you chose Bishop")
                                                validMoves[i].promoteTo = 'B'
                                            elif promoteEvent.key == p.K_n:
                                                print("you chose Knight")
                                                validMoves[i].promoteTo = 'N'
                                            else:
                                                print("you chose Queen")
                                                validMoves[i].promoteTo = 'Q'
                                else:
                                    pass
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if not gameOver:
                        gs.undoMove()
                        gs.getValidMoves()
                        moveMade = True
                        animate = False
                        gameOver = False
                elif e.key == p.K_0:
                    light = "light gray"
                    dark = "dark gray"
                elif e.key == p.K_1:
                    light = "#E9D298"
                    dark = "#9B7655"
                elif e.key == p.K_2:
                    light = "#77B5FE"
                    dark = "blue"
                elif e.key == p.K_3:
                    light = "pink"
                    dark = "brown"
                elif e.key == p.K_r:  # reset board
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    playerOne = False  # if white is human this is True
                    playerTwo = False  # if black is human this is True
                    moveMade = False
                    animate = False
                    gameOver = False
        if not humanTurn and not gameOver:
            move = SmartMoves.findBestMoveMinMax(gs, validMoves)
            # move = None
            if move is None:
                move = SmartMoves.randomAI(validMoves)
            gs.makeMove(move)
            moveMade = True
            animate = True
        if moveMade:
            if animate:
                animateMove(screen, gs.moveLog[-1], gs.board, clock)
            validMoves = gs.getValidMoves()
            if len(validMoves) == 0 and gs.inCheck:
                gs.checkMate = True
                gameOver = True
            elif len(validMoves) == 0 and not gs.inCheck:
                gs.staleMate = True
                gameOver = True
            print("white to move" if gs.whiteToMove else "black to move")
            moveMade = False
            animate = False

        drawGameSate(screen, gs, validMoves, sqSelected, light, dark)

        if gs.checkMate:
            gameOver = True
            print(gs.whiteKingLocation)
            print(gs.blackKingLocation)
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Draw by stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Highlighting selected piece and possible moves of it
'''


def highlightSquares(screen, gs, validMoves, sqSelected):
    lastStart = p.Surface((SQ_SIZE, SQ_SIZE))
    lastEnd = p.Surface((SQ_SIZE, SQ_SIZE))

    lastStart.set_alpha(100)
    lastEnd.set_alpha(100)

    lastStart.fill(p.Color('green'))
    lastEnd.fill(p.Color('light green'))
    captureAble = []
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # selected square can be moved
            # highlight selected square
            select = p.Surface((SQ_SIZE, SQ_SIZE))
            capture = p.Surface((SQ_SIZE, SQ_SIZE))
            possible = p.Surface((SQ_SIZE, SQ_SIZE))

            select.set_alpha(100)  # transparency value
            capture.set_alpha(100)
            possible.set_alpha(100)

            select.fill(p.Color('#6699cc'))  # fill color
            capture.fill(p.Color('red'))
            possible.fill(p.Color('yellow'))

            # highlight selected square
            screen.blit(select, (c * SQ_SIZE, r * SQ_SIZE))


            # highlight possible moves
            for move in validMoves:
                if (move.startRow == r and move.startCol == c) and (move.isEnpassantMove or move.pieceCaptured != "--"):
                    screen.blit(capture, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                    captureAble.append((move.endRow, move.endCol))
                elif move.startRow == r and move.startCol == c:
                    screen.blit(possible, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

    # highlight last move
    if len(gs.moveLog) != 0:
            lastStartRow, lastStartCol = gs.moveLog[-1].startRow, gs.moveLog[-1].startCol
            lastEndRow, lastEndCol = gs.moveLog[-1].endRow, gs.moveLog[-1].endCol
            screen.blit(lastStart, (lastStartCol * SQ_SIZE, lastStartRow * SQ_SIZE))
            if (lastEndRow, lastEndCol) not in captureAble:
                screen.blit(lastEnd, (lastEndCol * SQ_SIZE, lastEndRow * SQ_SIZE))


'''
responsible for all the graphics within a current game state
'''


def drawGameSate(screen, gs, validMoves, sqSelected, light, dark):
    drawBoard(screen, light, dark)  # draw squares on board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


'''
Draw the squares on the board
'''


def drawBoard(screen, light, dark):
    colors = [p.Color(light), p.Color(dark)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the pieces on the board using the current GameState.board
'''


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(screen, move, board, clock):
    coordinates = []  # list of co-ordinates the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 1  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen, 'light gray', 'dark gray')
        drawPieces(screen, board)
        # erase piece moved from its ending square
        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enpassantRow = (move.endRow + 1) if move.pieceMoved[0] == 'w' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, enpassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        if not move.isEnpassantMove and move.pieceMoved != "--":
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Open Sans", 32, True, False)
    textShadow = font.render(text, 0, p.Color('Dark Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textShadow.get_width() / 2,
                                                    HEIGHT / 2 - textShadow.get_height() / 2)
    screen.blit(textShadow, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(-2, -2))


if __name__ == "__main__":
    main()
