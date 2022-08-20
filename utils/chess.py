import random, json
from abc import *
from enum import IntEnum

class COLOR(IntEnum):
    WHITE = 0
    BLACK = 1
class PIECE(IntEnum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5
class MOVE(IntEnum):
    NORMAL = 0
    CASTLING = 1
    PROMOTION = 2
    ENPASSANT = 3

def get88List():
    return [[None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]]
def isValidLocation(a, b=0):
    return 0 <= a < 8 and 0 <= b < 8

class Piece(metaclass=ABCMeta):
    def __init__(self, color, x, y):
        self.color = color
        self.moved = False
        self.location = {'x': x, 'y': y}

    @abstractmethod
    def getMoveableList(self, board):
        pass

class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.PAWN
        self.enPassantWarning = False

    def getMoveableList(self, board):
        ret = get88List()
        x, y = self.location['x'], self.location['y']

        one_step_x = x + (1 if self.color == COLOR.BLACK else -1)
        two_step_x = x + (2 if self.color == COLOR.BLACK else -2)

        if isValidLocation(one_step_x) and board[one_step_x][y] is None:
            ret[one_step_x][y] = MOVE.PROMOTION if y == (7 if self.color == COLOR.BLACK else 0) else MOVE.NORMAL
        if isValidLocation(two_step_x) and board[one_step_x][y] is None and board[two_step_x][y] is None and self.moved == False:
            ret[two_step_x][y] = MOVE.NORMAL
        if isValidLocation(one_step_x, y - 1) and \
            board[one_step_x][y - 1] is not None and board[one_step_x][y - 1].color != self.color:
            ret[one_step_x][y - 1] = MOVE.NORMAL
        if isValidLocation(one_step_x, y + 1) and \
            board[one_step_x][y + 1] is not None and board[one_step_x][y + 1].color != self.color:
            ret[one_step_x][y + 1] = MOVE.NORMAL
        if isValidLocation(y - 1) and board[x][y - 1] is not None and \
            board[x][y - 1].piece == PIECE.PAWN and board[x][y - 1].color != self.color and \
                board[x][y - 1].enPassantWarning:
            ret[one_step_x][y - 1] = MOVE.ENPASSANT
        if isValidLocation(y + 1) and board[x][y + 1] is not None and \
            board[x][y + 1].piece == PIECE.PAWN and board[x][y + 1].color != self.color and \
                board[x][y + 1].enPassantWarning:
            ret[one_step_x][y + 1] = MOVE.ENPASSANT

        return ret

class Knight(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.KNIGHT

    def getMoveableList(self, board):
        ret = get88List()
        dx = [1, 2, 2, 1, -1, -2, -2, -1]
        dy = [2, 1, -1, -2, -2, -1, 1, 2]

        for i in range(8):
            new_x = self.location['x'] + dx[i]
            new_y = self.location['y'] + dy[i]
            if isValidLocation(new_x, new_y) and (board[new_x][new_y] is None or board[new_x][new_y].color != self.color):
                ret[new_x][new_y] = MOVE.NORMAL

        return ret

class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.ROOK

    def getMoveableList(self, board):
        ret = get88List()
        delta_x = [1, -1, 0, 0]
        delta_y = [0, 0, 1, -1]

        for i in range(4):
            for j in range(1, 8):
                new_x = self.location['x'] + (j * delta_x[i])
                new_y = self.location['y'] + (j * delta_y[i])
                if isValidLocation(new_x, new_y) and (board[new_x][new_y] is None or board[new_x][new_y].color != self.color):
                    ret[new_x][new_y] = MOVE.NORMAL
                else:
                    break

        return ret

class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.BISHOP

    def getMoveableList(self, board):
        ret = get88List()
        delta_x = [1, 1, -1, -1]
        delta_y = [1, -1, 1, -1]

        for i in range(4):
            for j in range(1, 8):
                new_x = self.location['x'] + (j * delta_x[i])
                new_y = self.location['y'] + (j * delta_y[i])
                if isValidLocation(new_x, new_y) and (board[new_x][new_y] is None or board[new_x][new_y].color != self.color):
                    ret[new_x][new_y] = MOVE.NORMAL
                else:
                    break

        return ret

class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.QUEEN

    def getMoveableList(self, board):
        ret = get88List()
        delta_x = [1, -1, 0, 0, 1, 1, -1, -1]
        delta_y = [0, 0, 1, -1, 1, -1, 1, -1]

        for i in range(8):
            for j in range(1, 8):
                new_x = self.location['x'] + (j * delta_x[i])
                new_y = self.location['y'] + (j * delta_y[i])
                if isValidLocation(new_x, new_y) and (board[new_x][new_y] is None or board[new_x][new_y].color != self.color):
                    ret[new_x][new_y] = MOVE.NORMAL
                else:
                    break

        return ret

class King(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.KING

    def getMoveableList(self, board):
        ret = get88List()
        delta_x = [1, -1, 0, 0, 1, 1, -1, -1]
        delta_y = [0, 0, 1, -1, 1, -1, 1, -1]

        for i in range(8):
            new_x = self.location['x'] + delta_x[i]
            new_y = self.location['y'] + delta_y[i]
            if isValidLocation(new_x, new_y) and (
                board[new_x][new_y] is None or board[new_x][new_y].color != self.color):
                ret[new_x][new_y] = MOVE.NORMAL
            else:
                break
        # 캐슬링...

        return ret

class ChessBoard:
    def __init__(self, username1, username2):
        dice = random.randrange(0, 2)
        self.white = username1 if dice == 0 else username2
        self.black = username2 if dice == 0 else username1
        self.turn = COLOR.WHITE
        self.board = [
            [Rook(COLOR.BLACK, 0, 0), Knight(COLOR.BLACK, 0, 1),
             Bishop(COLOR.BLACK, 0, 2), Queen(COLOR.BLACK, 0, 3),
             King(COLOR.BLACK, 0, 4), Bishop(COLOR.BLACK, 0, 5),
             Knight(COLOR.BLACK, 0, 6), Rook(COLOR.BLACK, 0, 7)],
            [Pawn(COLOR.BLACK, 1, 0), Pawn(COLOR.BLACK, 1, 1),
             Pawn(COLOR.BLACK, 1, 2), Pawn(COLOR.BLACK, 1, 3),
             Pawn(COLOR.BLACK, 1, 4), Pawn(COLOR.BLACK, 1, 5),
             Pawn(COLOR.BLACK, 1, 6), Pawn(COLOR.BLACK, 1, 7)],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [Pawn(COLOR.WHITE, 6, 0), Pawn(COLOR.WHITE, 6, 1),
             Pawn(COLOR.WHITE, 6, 2), Pawn(COLOR.WHITE, 6, 3),
             Pawn(COLOR.WHITE, 6, 4), Pawn(COLOR.WHITE, 6, 5),
             Pawn(COLOR.WHITE, 6, 6), Pawn(COLOR.WHITE, 6, 7)],
            [Rook(COLOR.WHITE, 7, 0), Knight(COLOR.WHITE, 7, 1),
             Bishop(COLOR.WHITE, 7, 2), Queen(COLOR.WHITE, 7, 3),
             King(COLOR.WHITE, 7, 4), Bishop(COLOR.WHITE, 7, 5),
             Knight(COLOR.WHITE, 7, 6), Rook(COLOR.WHITE, 7, 7)]
        ]
        self.record = []

    def getBoard(self):
        ret = get88List()
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                ret[i][j] = ({'color': p.color, 'piece': p.piece} if p else None)
        return ret

    def getMoveable(self):
        ret = get88List()
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                ret[i][j] = (p.getMoveableList(self.board) if p else get88List())
        return ret

    def getData(self):
        return {
            'white': self.white,
            'black': self.black,
            'turn': self.turn,
            'board': self.getBoard(),
            'moveable': self.getMoveable(),
            'whiteDead': [0,1,2,3,4],
            'blackDead': [0,0,0,0,0,1,1,2,2,3,3,4]
            
        }

    # def action(self):
    #     print(self.turn, '액션 실행')

print (json.dumps(ChessBoard('seuha516', '익명fdkW2c').getData(), ensure_ascii=False))