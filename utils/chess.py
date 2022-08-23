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
        self.location = {'x': x, 'y': y}
        self.moved = False
        self.enPassantWarning = False

    @abstractmethod
    def getMoveList(self, board):
        pass

class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.PAWN

    def getMoveList(self, board):
        ret = get88List()
        x, y = self.location['x'], self.location['y']

        one_step_x = x + (1 if self.color == COLOR.BLACK else -1)
        two_step_x = x + (2 if self.color == COLOR.BLACK else -2)

        if isValidLocation(one_step_x) and board[one_step_x][y] is None:
            ret[one_step_x][y] = MOVE.PROMOTION if one_step_x == (0 if self.color == COLOR.WHITE else 7) else MOVE.NORMAL
        if isValidLocation(two_step_x) and board[one_step_x][y] is None and board[two_step_x][y] is None and self.moved == False:
            ret[two_step_x][y] = MOVE.NORMAL
        if isValidLocation(one_step_x, y - 1) and \
            board[one_step_x][y - 1] is not None and board[one_step_x][y - 1].color != self.color:
            ret[one_step_x][y - 1] = MOVE.PROMOTION if one_step_x == (0 if self.color == COLOR.WHITE else 7) else MOVE.NORMAL
        if isValidLocation(one_step_x, y + 1) and \
            board[one_step_x][y + 1] is not None and board[one_step_x][y + 1].color != self.color:
            ret[one_step_x][y + 1] = MOVE.PROMOTION if one_step_x == (0 if self.color == COLOR.WHITE else 7) else MOVE.NORMAL
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

    def getMoveList(self, board):
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

    def getMoveList(self, board):
        ret = get88List()
        delta_x = [1, -1, 0, 0]
        delta_y = [0, 0, 1, -1]

        for i in range(4):
            for j in range(1, 8):
                new_x = self.location['x'] + (j * delta_x[i])
                new_y = self.location['y'] + (j * delta_y[i])
                if isValidLocation(new_x, new_y):
                    if board[new_x][new_y] is None:
                        ret[new_x][new_y] = MOVE.NORMAL
                    elif board[new_x][new_y].color != self.color:
                        ret[new_x][new_y] = MOVE.NORMAL
                        break
                    else:
                        break
                else:
                    break

        return ret

class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.BISHOP

    def getMoveList(self, board):
        ret = get88List()
        delta_x = [1, 1, -1, -1]
        delta_y = [1, -1, 1, -1]

        for i in range(4):
            for j in range(1, 8):
                new_x = self.location['x'] + (j * delta_x[i])
                new_y = self.location['y'] + (j * delta_y[i])
                if isValidLocation(new_x, new_y):
                    if board[new_x][new_y] is None:
                        ret[new_x][new_y] = MOVE.NORMAL
                    elif board[new_x][new_y].color != self.color:
                        ret[new_x][new_y] = MOVE.NORMAL
                        break
                    else:
                        break
                else:
                    break

        return ret

class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.QUEEN

    def getMoveList(self, board):
        ret = get88List()
        delta_x = [1, -1, 0, 0, 1, 1, -1, -1]
        delta_y = [0, 0, 1, -1, 1, -1, 1, -1]

        for i in range(8):
            for j in range(1, 8):
                new_x = self.location['x'] + (j * delta_x[i])
                new_y = self.location['y'] + (j * delta_y[i])
                if isValidLocation(new_x, new_y):
                    if board[new_x][new_y] is None:
                        ret[new_x][new_y] = MOVE.NORMAL
                    elif board[new_x][new_y].color != self.color:
                        ret[new_x][new_y] = MOVE.NORMAL
                        break
                    else:
                        break
                else:
                    break

        return ret

class King(Piece):
    def __init__(self, color, x, y):
        super().__init__(color, x, y)
        self.piece = PIECE.KING

    def getMoveList(self, board):
        ret = get88List()
        delta_x = [1, -1, 0, 0, 1, 1, -1, -1]
        delta_y = [0, 0, 1, -1, 1, -1, 1, -1]

        for i in range(8):
            new_x = self.location['x'] + delta_x[i]
            new_y = self.location['y'] + delta_y[i]
            if isValidLocation(new_x, new_y) and (board[new_x][new_y] is None or board[new_x][new_y].color != self.color):
                ret[new_x][new_y] = MOVE.NORMAL

        if not self.moved:
            # 킹사이드 캐슬링 (움직임 X, 가운데 기물 X)
            p = board[self.location['x']][7]
            if p is not None and p.color == self.color and p.piece == PIECE.ROOK and p.moved == False \
                and board[self.location['x']][5] is None and board[self.location['x']][6] is None:
                ret[self.location['x']][6] = MOVE.CASTLING
            # 퀸사이드 캐슬링 (움직임 X, 가운데 기물 X)
            p = board[self.location['x']][0]
            if p is not None and p.color == self.color and p.piece == PIECE.ROOK and p.moved == False \
                and board[self.location['x']][1] is None and board[self.location['x']][2] is None \
                    and board[self.location['x']][3] is None:
                ret[self.location['x']][2] = MOVE.CASTLING

        return ret


class ChessBoard:
    def __init__(self, players=None):
        if players is None:
            return
        dice = random.randrange(0, 2)
        players[0]['color'] = dice
        players[1]['color'] = 1 - dice
        players[0]['kill'] = []
        players[1]['kill'] = []
        del players[0]['ready']
        del players[1]['ready']

        self.players = players
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
        self.lastMove = [{'x': -1, 'y': -1}, {'x': -1, 'y': -1}]
        self.log = []

    # King의 위치를 튜플로 리턴
    def searchKing(self, color):
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                if p is not None and p.color == color and p.piece == PIECE.KING:
                    return i, j

    # 이 move를 수행할 수 있는가?
    def isMoveLegal(self, move, myColor):
        ox, oy, tx, ty, moveType = move

        if moveType == MOVE.CASTLING:
            canCastling = True
            for i in range(min(oy, ty), max(oy, ty) + 1):
                canCastling = canCastling and (not self.isDanger((ox, i), 1 - myColor))
            return canCastling
        elif moveType == MOVE.ENPASSANT:
            ghost = self.board[ox][ty]
            self.board[ox][ty] = None
        else:
            ghost = self.board[tx][ty]
        self.board[tx][ty] = self.board[ox][oy]
        self.board[ox][oy] = None

        ret = not self.isDanger(self.searchKing(myColor), 1 - myColor)

        self.board[ox][oy] = self.board[tx][ty]
        self.board[tx][ty] = None
        if moveType == MOVE.ENPASSANT:
            self.board[ox][ty] = ghost
        else:
            self.board[tx][ty] = ghost

        return ret

    # 이 위치가 공격당하는가?
    def isDanger(self, location, attacker):
        x, y = location
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                if p is not None and p.color == attacker and p.getMoveList(self.board)[x][y] is not None:
                    return True
        return False

    # 정말 이동 가능한 위치들만 리턴
    def getLegalMoveList(self, p):
        if p and p.color == self.turn:
            moveList = p.getMoveList(self.board)
            for i in range(8):
                for j in range(8):
                    moveType = moveList[i][j]
                    if moveType is not None and not self.isMoveLegal((p.location['x'], p.location['y'], i, j, moveType), p.color):
                        moveList[i][j] = None
            return moveList
        else:
            return get88List()

    # 현재 턴인 유저가 할 수 있는 행동이 없는가?
    def isNothingToDo(self):
        ret = True
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                moveList = self.getLegalMoveList(p)
                for ii in range(8):
                    for jj in range(8):
                        if moveList[ii][jj] is not None:
                            ret = False
        return ret

    # 기물 부족인가?
    def isNotEnoughToGame(self):
        white = []
        whiteBishop = None
        black = []
        blackBishop = None

        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                if not p:
                    pass
                elif p.color == COLOR.WHITE:
                    white.append(p.piece)
                    if p.piece == PIECE.BISHOP:
                        whiteBishop = p
                else:
                    black.append(p.piece)
                    if p.piece == PIECE.BISHOP:
                        blackBishop = p

        white.sort()
        black.sort()

        if len(white) == 1 and len(black) == 1:
            return True
        elif len(white) == 1 and len(black) == 2 and black[0] == PIECE.BISHOP:
            return True
        elif len(black) == 1 and len(white) == 2 and white[0] == PIECE.BISHOP:
            return True
        elif len(white) == 1 and len(black) == 2 and black[0] == PIECE.KNIGHT:
            return True
        elif len(black) == 1 and len(white) == 2 and white[0] == PIECE.KNIGHT:
            return True
        elif len(white) == 2 and len(black) == 2 and white[0] == PIECE.BISHOP and black[0] == PIECE.BISHOP:
            if (whiteBishop.location['x'] + whiteBishop.location['y']) % 2 \
                == (blackBishop.location['x'] + blackBishop.location['y']) % 2:
                return True

        return False


    # 서버로부터 로드
    def setting(self, data):
        self.players = data['players']
        self.turn = data['turn']
        self.lastMove = data['lastMove']
        self.log = data['log']
        self.board = get88List()
        for i in range(8):
            for j in range(8):
                p = data['board'][i][j]
                if p:
                    if p['piece'] == PIECE.PAWN:
                        self.board[i][j] = Pawn(p['color'], p['location']['x'], p['location']['y'])
                    elif p['piece'] == PIECE.KNIGHT:
                        self.board[i][j] = Knight(p['color'], p['location']['x'], p['location']['y'])
                    elif p['piece'] == PIECE.ROOK:
                        self.board[i][j] = Rook(p['color'], p['location']['x'], p['location']['y'])
                    elif p['piece'] == PIECE.BISHOP:
                        self.board[i][j] = Bishop(p['color'], p['location']['x'], p['location']['y'])
                    elif p['piece'] == PIECE.QUEEN:
                        self.board[i][j] = Queen(p['color'], p['location']['x'], p['location']['y'])
                    elif p['piece'] == PIECE.KING:
                        self.board[i][j] = King(p['color'], p['location']['x'], p['location']['y'])
                    self.board[i][j].moved = p['moved']
                    self.board[i][j].enPassantWarning = p['enPassantWarning']

    # 클라이언트용 데이터
    def getData(self):
        # board, moveable 계산
        board = get88List()
        moveable = get88List()
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                board[i][j] = ({'color': p.color, 'piece': p.piece} if p else None)
                moveable[i][j] = self.getLegalMoveList(p)

        # 게임 중간 체크
        finish = False
        if self.isNothingToDo():
            if self.isDanger(self.searchKing(self.turn), 1 - self.turn):
                finish = True
                winner = self.players[1 if self.players[0]['color'] == self.turn else 0]
                recordResult = {'type': '1on1', 'winner': winner['username']}
                message = {
                    'type': 'CHATTING',
                    'value': {
                        'type': 'GAME',
                        'info': 'RESULT',
                        'content': '체크메이트! %s님이 승리했습니다.' % winner['nickname']
                    }
                }
            else:
                finish = True
                winner = None
                recordResult = {'type': '1on1', 'winner': None}
                message = {
                    'type': 'CHATTING',
                    'value': {
                        'type': 'GAME',
                        'info': 'RESULT',
                        'content': '스테일메이트(무승부)로 게임이 종료됐습니다.'
                    }
                }
        else:
            if self.isNotEnoughToGame():
                finish = True
                winner = None
                recordResult = {'type': '1on1', 'winner': None}
                message = {
                    'type': 'CHATTING',
                    'value': {
                        'type': 'GAME',
                        'info': 'RESULT',
                        'content': '기물 부족(무승부)으로 게임이 종료됐습니다.'
                    }
                }
            elif self.isDanger(self.searchKing(self.turn), 1 - self.turn):
                message = {
                    'type': 'CHATTING',
                    'value': {
                        'type': 'GAME',
                        'info': 'WARNING',
                        'content': '%s(%d수) - 체크'\
                            % (self.players[1 if self.players[0]['color'] == self.turn else 0]['nickname'], len(self.log))
                    }
                }
            else:
                message = None

        return {
            'players': self.players,
            'turn': self.turn,
            'board': board,
            'moveable': moveable,
            'lastMove': self.lastMove,
            'log': self.log,

            'message': message,
            'result': {
                'winner': winner,
                'recordResult': recordResult
            } if finish else None
        }

    # 서버 저장용 데이터
    def getSave(self):
        board = get88List()
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                board[i][j] = ({'color': p.color,
                                'piece': p.piece,
                                'location': {'x': p.location['x'], 'y': p.location['y']},
                                'moved': p.moved,
                                'enPassantWarning': p.enPassantWarning
                                } if p else None)

        return {
            'players': self.players,
            'turn': self.turn,
            'board': board,
            'lastMove': self.lastMove,
            'log': self.log
        }

    # 이동
    def move(self, data):
        # data 읽기
        ox = data['originalLocation']['x']
        oy = data['originalLocation']['y']
        tx = data['targetLocation']['x']
        ty = data['targetLocation']['y']
        moveType = data['moveType']
        if self.turn == COLOR.BLACK:
            ox = 7 - ox
            tx = 7 - tx

        # (임시) 로그 적기
        self.log.append('%d,%d->%d,%d(%d)' % (ox, oy, tx, ty, moveType))

        # moved, enPassantWarning 적용
        for i in range(8):
            for j in range(8):
                if self.board[i][j]:
                    self.board[i][j].enPassantWarning = False
        self.board[ox][oy].moved = True
        if self.board[ox][oy].piece == PIECE.PAWN and (abs(ox - tx) == 2):
            self.board[ox][oy].enPassantWarning = True

        # kill 계산
        if moveType == MOVE.ENPASSANT:
            ghost = self.board[ox][ty]
            self.board[ox][ty] = None
        else:
            ghost = self.board[tx][ty]
        if ghost:
            self.players[0 if self.players[0]['color'] == self.turn else 1]['kill'].append(ghost.piece)

        # 이동
        self.board[tx][ty] = self.board[ox][oy]
        self.board[tx][ty].location = {'x': tx, 'y': ty}
        self.board[ox][oy] = None
        self.lastMove = [{'x': ox, 'y': oy}, {'x': tx, 'y': ty}]

        # 프로모션
        if moveType == MOVE.PROMOTION:
            newPiece = data['piece']
            if newPiece == PIECE.PAWN:
                self.board[tx][ty] = Pawn(self.turn, tx, ty)
            elif newPiece == PIECE.KNIGHT:
                self.board[tx][ty] = Knight(self.turn, tx, ty)
            elif newPiece == PIECE.ROOK:
                self.board[tx][ty] = Rook(self.turn, tx, ty)
            elif newPiece == PIECE.BISHOP:
                self.board[tx][ty] = Bishop(self.turn, tx, ty)
            elif newPiece == PIECE.QUEEN:
                self.board[tx][ty] = Queen(self.turn, tx, ty)
            elif newPiece == PIECE.KING:
                self.board[tx][ty] = King(self.turn, tx, ty)
            self.board[tx][ty].moved = False
            self.board[tx][ty].enPassantWarning = False

        # 캐슬링
        if moveType == MOVE.CASTLING:
            if ty == 6:
                rook = self.board[tx][7]
                self.board[tx][7] = None
                rook.location = {'x': tx, 'y': 5}
                self.board[tx][5] = rook
            else:
                rook = self.board[tx][0]
                self.board[tx][0] = None
                rook.location = {'x': tx, 'y': 3}
                self.board[tx][3] = rook


