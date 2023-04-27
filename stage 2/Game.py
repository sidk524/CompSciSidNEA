from itertools import product
from enum import auto

class GameError(Exception):
    pass

class Game:

    P1 = 'o'
    P2 = 'x'
    DRAW = auto()
    _EMPTY = ' '
    _DIM = 3

    def __init__(self):
        self._board = [[Game._EMPTY for _ in range(Game._DIM)] for _ in range(Game._DIM)]
        self._player = Game.P1

    def __repr__(self):
        result = "  " + " ".join(str(i+1) for i in range(Game._DIM))
        for row in range(Game._DIM):
            result += f"\n{row+1} " + "|".join(self._board[row])
            if row != Game._DIM - 1:
                dashes = "-" * (2 * Game._DIM - 1)
                result += f"\n  {dashes}"
        result += f"\n\n{self._player} turn to play"
        return result

    def _validate(self,row,col):
        if not (0 < row <= Game._DIM):
            raise GameError(f"Row {row} not in range")
        if not (0 < col <= Game._DIM):
            raise GameError(f"Column {col} not in range")
        row -= 1
        col -= 1
        return row,col

    def play(self,row,col):
        row,col = self._validate(row,col)
        if self._board[row][col] is not Game._EMPTY:
            raise GameError("You must play in an empty space")
        self._board[row][col] = self._player
        self._player = Game.P2 if self._player is Game.P1 else Game.P1
    
    @property
    def winner(self):
        if all(self._board[r][c] is not Game._EMPTY for (r,c) in product(range(Game._DIM),range(Game._DIM))):
            return Game.DRAW
            
        for p in [Game.P1,Game.P2]:
            for row in range(Game._DIM):
                if all(self._board[row][col] is p for col in range(Game._DIM)):
                    return p
            for col in range(Game._DIM):
                if all(self._board[row][col] is p for row in range(Game._DIM)):
                    return p
            if all(self._board[i][i] is p for i in range(Game._DIM)):
                return p
            if all(self._board[i][Game._DIM - 1 - i] is p for i in range(Game._DIM)):
                return p
        return None

    @property
    def player(self):
        return self._player

if __name__ == "__main__":
    g = Game()
    print(g)

