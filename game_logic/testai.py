from player import Player

# Todo: Get basic AI working

class AIPlayer(Player):
    def __init__(self) -> None:
        super().__init__("AI Name")
    def make_a_move(self, board: [[str]], dies: [int], color: str, hits: int) -> [{ int: int }]:
        moves = []
        direction = -1 if color == 'white' else 1
        for dice in dies:
            for j in range(len(board)):
                if len(board[j]) != 0 and board[j][0] == color:
                    if self.move_is_valid(start=j, board=board, dice=dice, color=color, hits=hits):
                        end = j + (dice * direction)
                        a_move = {j: end}
                        moves.append(a_move)
                        break
        return moves
