from player import Player

# Todo: Get basic AI working

class AIPlayer(Player):
    def __init__(self) -> None:
        super().__init__("AI Name")
    def make_a_move(self, board: [[str]], dies: [int], color: str, hits: int) -> [{ int: int }]:
        moves = []
        while self.has_valid_moves(board, dies, color, hits):
            for i in range(len(dies) - 1, -1, -1):
                move = self.all_valid_moves(board, dies[i], color, hits)
                if len(move) != 0:
                    moves.append(move[0])
                    for start, dice in move[0].items():
                        
                        if start > -1 and start < 24:
                            board[start].pop()
                        else:
                            hits -= 1
                        end_pos = start + dice * (1 if color == 'black' else -1)
                        if end_pos >= 0 and end_pos < 24:
                            board[end_pos].append(color)

                    dies.pop(i)
        return moves
