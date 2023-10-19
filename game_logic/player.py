from random import randint

class Player:
    """
    An abstract class for the player instances that would be
    making the moves
    """
    def __init__(self, name: str) -> None:
        self.__name = name

    def __is_finishing(self, color: str, board: [[str]]) -> bool:
        """
        Check to see if the player is finishing up with their pieces
        """
        for i in range(18):
            index = i if color == 'black' else 23 - i
            if len(board[index]) != 0 and color == board[index][0]:
                return False
        return True

    def move_is_valid(self, start: int, board: [[str]], dice: int, color: str, hits: int) -> bool:
        """
        A function that indicates whether the given move is valid
        """
        finish = start + dice * (1 if color == 'black' else -1)
        # This takes care of verifying whether the piece has been hit
        if hits != 0:
            if color == 'black':
                if start != -1:
                    return False
            elif color == 'white':
                if start != 24:
                    return False
            # This means the hit piece can be reloacted to correct position
            if len(board[finish]) == 0 or board[finish][0] == color:
                return True
        if finish >= 0 and finish < 24 and start != 24 and start != -1:
        # This means a valid piece has been selected
            if len(board[start]) != 0 and board[start][0] == color:
                if len(board[finish]) == 0 or board[finish][0] == color:
                    return True
                elif len(board[finish]) == 1 and board[finish][0] != color:
                    # This would be a hit
                    return True
                else:
                    return False
        elif self.__is_finishing(color, board):
            direction = (1 if color == 'black' else -1)
            # This means the move is exact
            if finish == (-1 if color == 'white' else 24):
                return True
            # Checking to make sure there are no other valid moves from before
            for i in range(start - direction, 6 if direction == -1 else 17, -direction):
                if len(board[i]) != 0 and board[i][0] == color:
                    return False
            return True
        return False

    def all_valid_moves(self, board: [[str]], dice: int, color: str, hits: int) -> [{int: int}]:
        """
        Getter for all of the valid moves for a given dice
        """
        direction = 1 if color == 'black' else -1
        if hits > 0:
            start_pos = 24 if color == 'white' else -1
            if self.move_is_valid(start_pos, board, dice, color, hits):
                return [{start_pos: dice}]
            return []
        valids = []
        for i in range(24):
            if len(board[i]) != 0 and board[i][0] == color:
                if self.move_is_valid(i, board, dice, color, hits):
                    # making sure the boundaries are correct
                    valids.append({i: dice})
        
        return valids

    def has_valid_moves(self, board: [[str]], dies: [int], color: str, hits: int) -> bool:
        for d in dies:
            for i in range(-1, 25):
                if self.move_is_valid(i, board, d, color, hits):
                    return True
        return False

    def make_a_move(self, board: [[str]], dies:[int], color: str, hits: int) -> [{int: int}]:
        """
        This will be the function that would be called for
        players to make a move.
        """
        return [{} for d in dies]
    