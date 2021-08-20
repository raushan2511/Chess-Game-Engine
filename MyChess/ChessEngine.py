"""
--> store all info about current state
--> determine valid moves at current state
--> keep a move log
"""


class GameState():
    def __init__(self):
        # board is a 8x8 2D list, each element has 2 characters
        # first represents denotes color, second character represents piece
        # "--" represents no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.pins = []
        self.checks = []
        self.inCheck = False
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # co-ordinates for the square
        self.currentCastleRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                             self.currentCastleRight.wqs, self.currentCastleRight.bqs)]
        self.whitePieces = ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp",
                            "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        self.blackPieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR",
                            "bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"]

    '''
    executes a move
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so that we can undo them later
        self.whiteToMove = not self.whiteToMove

        # promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promoteTo
            #if move.pieceMoved[0] == "w":
            #    self.whitePieces.append("w" + move.promoteTo)
            #    self.whitePieces.remove("wp")
            #else:
            #    self.blackPieces.append("b" + move.promoteTo)
            #    self.blackPieces.remove("bp")
            move.promoteTo = 'Q'
        # En Passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        # updating enpassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
            move.enpassantPossible = self.enpassantPossible
        else:
            self.enpassantPossible = ()
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle
                if 1 <= move.endCol <= 6:
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # rook moves
                    self.board[move.endRow][move.endCol + 1] = "--"  # remove rook
            else:  # queen side castle
                if 2 <= move.endCol <= 6:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # rook moves
                    self.board[move.endRow][move.endCol - 2] = "--"  # remove rook
        # updating castling rights whenever rook or king moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                                 self.currentCastleRight.wqs, self.currentCastleRight.bqs))
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
    '''
    undo the last move
    '''

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
                # print(self.enpassantPossible)
            else:
                self.board[move.startRow][move.startCol] = move.pieceMoved
                self.board[move.endRow][move.endCol] = move.pieceCaptured

            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # undo castling rights
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastleRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs,
                                                   newRights.bqs)  # set the castle rights to the last right in the log
            # undo castle
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side castle
                    if 1 <= move.endCol <= 6:
                        self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                        self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queen side castle
                    if 2 <= move.endCol <= 6:
                        self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                        self.board[move.endRow][move.endCol + 1] = "--"
                if self.whiteToMove:
                    self.whiteKingLocation = (7, 4)
                else:
                    self.blackKingLocation = (0, 4)
            else:
                if move.pieceMoved == "wK":
                    self.whiteKingLocation = (move.endRow, move.endCol)
                if move.pieceMoved == "bK":
                    self.blackKingLocation = (move.endRow, move.endCol)
            self.checkMate = False
            self.staleMate = False

    '''
    updating castle rights
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastleRight.wks = False
            self.currentCastleRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastleRight.bks = False
            self.currentCastleRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7 and move.startCol == 0:  # left rook
                self.currentCastleRight.wqs = False
            elif move.startRow == 7 and move.startCol == 7:  # right rook
                self.currentCastleRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0 and move.startCol == 0:  # left rook
                self.currentCastleRight.bqs = False
            elif move.startRow == 0 and move.startCol == 7:  # right rook
                self.currentCastleRight.bks = False
        if move.pieceCaptured[1] == 'R':
            if move.pieceCaptured[0] == 'w':
                if move.endRow == 7 and move.endCol == 0:
                    self.currentCastleRight.wqs = False
                elif move.endRow == 7 and move.endCol == 7:
                    self.currentCastleRight.wks = False
            elif move.pieceCaptured[0] == 'b':
                if move.endRow == 0 and move.endCol == 0:
                    self.currentCastleRight.bqs = False
                elif move.endRow == 0 and move.endCol == 7:
                    self.currentCastleRight.bks = False

    '''
    moves considering checks
    '''

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        kingRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        kingCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece checking
                validSquares = []  # squares where pieces can move
                # if Knight, must capture Knight or move King, no blocks possible
                if pieceChecking[1] == 'N':
                    validSquares.append((checkRow, checkCol))
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2], check[3] are
                        # check directions
                        validSquares.append(validSquare)
                        if validSquare == (checkRow, checkCol):
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # go through the list in reverse
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
            self.getCastleMoves(kingRow, kingCol, moves)
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    '''
    if current player is in check
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    determine if opponent can attack (r, c)
    '''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch player
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch it back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # rows
            for c in range(len(self.board[r])):  # cols
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    '''
    all pawn moves
    '''

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if len(self.moveLog) != 0:
            lastMove = self.moveLog[-1]
            if self.enpassantPossible == () and not lastMove.enpassantPossible == ():
                self.enpassantPossible = lastMove.enpassantPossible
        if self.whiteToMove:
            if r > 0 and self.board[r - 1][c] == "--":  # one square move
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # two square move
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # left capture
                if self.board[r - 1][c - 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # right capture
                if self.board[r - 1][c + 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:
            if r < 7 and self.board[r + 1][c] == "--":  # one square empty
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # left capture
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                if (r + 1, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # right capture
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                if (r + 1, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
        # add promotions

    '''
    all Rook moves
    '''

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # cannot remove queen from pin on rook moves, only remove it on
                    # Bishop moves
                    self.pins.remove(self.pins[i])
                break
        direction = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        enemyPiece = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                row = r + d[0] * i
                col = c + d[1] * i
                if 0 <= row <= 7 and 0 <= col <= 7:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):  # piece direction is
                        # towards the pin direction or away from it
                        endPiece = self.board[row][col]
                        if endPiece == "--":
                            moves.append(Move((r, c), (row, col), self.board))
                        elif endPiece[0] == enemyPiece:
                            moves.append(Move((r, c), (row, col), self.board))
                            break
                        else:
                            break
                else:  # off board
                    break

    '''
    all Knight moves
    '''

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        direction = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, -1), (2, 1), (-2, 1), (-2, -1)]
        ownPiece = "w" if self.whiteToMove else "b"
        for d in direction:
            row = r + d[0]
            col = c + d[1]
            if 0 <= row <= 7 and 0 <= col <= 7:
                if not piecePinned:
                    endPiece = self.board[row][col]
                    if endPiece[0] != ownPiece:
                        moves.append(Move((r, c), (row, col), self.board))

    '''
    all Bishop moves
    '''

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        direction = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        enemyPiece = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                row = r + d[0] * i
                col = c + d[1] * i
                if 0 <= row <= 7 and 0 <= col <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[row][col]
                        if endPiece == "--":
                            moves.append(Move((r, c), (row, col), self.board))
                        elif endPiece[0] == enemyPiece:
                            moves.append(Move((r, c), (row, col), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    all King moves
    '''

    def getKingMoves(self, r, c, moves):
        direction = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        ownPiece = "w" if self.whiteToMove else "b"
        for d in direction:
            row = r + d[0]
            col = c + d[1]
            if 0 <= row <= 7 and 0 <= col <= 7:
                endPiece = self.board[row][col]
                if endPiece[0] != ownPiece:
                    # temporarily move the King a look for checks
                    if ownPiece == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (row, col), self.board))
                    if ownPiece == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
    '''
    generate all valid castle moves and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if (self.whiteToMove and self.currentCastleRight.wks) or (not self.whiteToMove and self.currentCastleRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastleRight.wqs) or (not self.whiteToMove and self.currentCastleRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--" and (not self.squareUnderAttack(r, c+1)) and \
                (not self.squareUnderAttack(r, c+2)):
            moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--" and \
                (not self.squareUnderAttack(r, c-1)) and (not self.squareUnderAttack(r, c-2)):
            moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
    '''
    all Queen moves
    '''

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    returns if player's in check, list of pins, list of checks
    '''

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        enemyColor = "b" if self.whiteToMove else "w"
        allyColor = "w" if self.whiteToMove else "b"
        startRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        startCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endCol <= 7 and 0 <= endRow <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        # five possible case :
                        if (0 <= j <= 3 and pieceType == "R") or \
                                (4 <= j <= 7 and pieceType == "B") or \
                                (i == 1 and pieceType == 'p' and (
                                        (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (pieceType == "Q") or (i == 1 and pieceType == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # knight checks
        knightMoves = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, -1), (2, 1), (-2, 1), (-2, -1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy Knight checking King
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        # promotion
        self.promoteTo = 'Q'
        self.isPawnPromotion = (self.pieceMoved == "bp" and self.endRow == 7) or (
                    self.pieceMoved == "wp" and self.endRow == 0)
        # En Passant
        self.enpassantPossible = ()
        self.isEnpassantMove = isEnpassantMove
        self.pieceCaptured = board[self.endRow][self.endCol] if not isEnpassantMove else board[self.startRow][
            self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol * 1
        # Castle
        self.isCastleMove = isCastleMove

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotations(self):
        # can be improved
        if self.pieceMoved[1] == "p":
            if self.pieceCaptured == "--":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol)
        elif self.pieceCaptured == "--":
            return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)
        else:
            return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
