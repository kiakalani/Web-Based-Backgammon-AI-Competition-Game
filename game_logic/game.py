from testai import AIPlayer
from random import randint
class Game:
    def __init__(self, p1, p2) -> None:
        self.__player1 = AIPlayer()
        self.__player2 = AIPlayer()
        self.__turn = False
        self.__round = 1
        self.__board = []
        self.__board = [[] for i in range(24)]
        self.__hits = {'white': 0, 'black': 0}
        self.__board[21], self.__board[22] = ['black'], ['black']
        self.__reset_board()
    
    def __reset_board(self):
        """
        A helper function to reset the board before starting
        the round
        """
        empty_board = [[] for i in range(24)]
        for _ in range(2):
            empty_board[0].append('black')
            empty_board[23].append('white')
        for _ in range(5):
            empty_board[5].append('white')
            empty_board[11].append('black')
            empty_board[12].append('white')
            empty_board[18].append('black')
        for _ in range(3):
            empty_board[7].append('white')
            empty_board[16].append('black')
        self.__board = empty_board

    def __is_finishing(self, color: str, board: [[str]]) -> bool:
        """
        Check to see if the player is finishing up with their pieces
        """
        for i in range(18):
            index = i if color == 'black' else 23 - i
            if len(board[index]) != 0 and color == board[index][0]:
                return False
        return True

    def get_winner(self) -> str:
        """
        Returns the winner of the game
        """
        num_pieces = {'white': 0, 'black': 0}
        for i in range(24):
            cur_len = len(self.__board[i])

            if cur_len != 0:
                num_pieces[self.__board[i][0]] += cur_len
        if num_pieces['white'] == 0:
            return 'white'
        elif num_pieces['black'] == 0:
            return 'black'
        return None
                
    def move_is_valid(self, start: int, finish: int, color: str, board: [[str]], dice) -> bool:
        # This takes care of verifying whether the piece has been hit
        if self.__hits[color] != 0:
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
            if start + dice * direction == finish:
                return True
            # Checking to make sure there are no other valid moves from before
            for i in range(start - direction, 6 if direction == -1 else 17, -direction):
                if len(board[i]) != 0 and board[i][0] == color:
                    return False
            return True
        return False

    def has_valid_moves(self, color: str, dice: int, board=None) -> bool:
        """
        This function returns true if there is a valid move
        with the given dice for the player otherwise false
        """
        if board == None:
            board = self.__board
        direction = 1 if color == 'black' else -1
        if self.__hits[color] != 0:
            pos = (dice * direction) + (-1 if color == 'black' else 24)
            if len(board[pos]) != 0 and board[pos][0] != color:
                return False
            return True
        else:
            for i in range(24):
                if len(board[i]) != 0 and board[i][0] == color:
                    if self.move_is_valid(i, i + dice * direction, color, board, dice):
                        return True
            return False
            
                
    def make_move(self, move:{int:int}, color: str, dice: int, board=None, hits=None) -> None:
        """
        This function is responsible for making a move by the given parameters
        """
        if board == None:
            board = self.__board
        if hits == None:
            hits = self.__hits
        if len(move) != 1:
            # this means the input is invalid
            return
        for start, d in move.items():
            finish = start + d * (1 if color == 'black' else -1)
            finish = max(-1, min(24, finish))
            if self.move_is_valid(start, finish, color, board, dice):
                # if the player is finishing up, we don't want to add the piece
                # back to the board
                # hitting a piece takes place here
                if finish != -1 and finish != 24:
                    if len(board[finish]) != 0 and board[finish][0] != color and len(board[finish]) == 1:
                        hits['black' if color != 'black' else 'white'] += 1
                        board[finish].pop()
                # The scenarios where the piece is not being removed
                if not (self.__is_finishing(color, board) and (finish == -1 or finish == 24)):
                    board[finish].append(color)
                # Determining whether we should pop the item or decrement the count
                # of hit pieces
                if start != -1 and start != 24:
                    # Making sure the piece is not hit
                    board[start].pop()
                elif hits[color] > 0:
                    # putting the hit piece back
                    hits[color] -= 1

                



    def get_board(self) -> [[str]]:
        """
        This function returns a copy of the board
        """
        return [[b for b in i] for i in self.__board]

    def debug_board(self) -> None:
        """
        A printing function for giving perspective about what is going on in
        the game.
        """
        down, up = '', ''
        for i in range(12):
            u_i = 12 + i
            if len(self.__board[i]) == 0:
                down = '|   ' + down
            else:
                down = str(len(self.__board[i])) + self.__board[i][0][0]  + '  ' + down
            if len(self.__board[u_i]) == 0:
                up += '|   '
            else:
                up += str(len(self.__board[u_i])) + self.__board[u_i][0][0] + '  '
        print(up)
        print(down)
        print('Black: ', self.__hits['black'], 'White:', self.__hits['white'])
    def make_move_player(self, player, color, dies, hits):
        # TODO: Figure out how to consider looking for the hits
        # the rest seems to be considered
        if self.has_valid_moves(color, dies[0]) or self.has_valid_moves(color, dies[1]):
            moves = player.make_a_move(self.get_board(), [d for d in dies], color, hits)
            print(moves)
            count_dies = {}
            for d in dies:
                if not count_dies.get(d):
                    count_dies[d] = 1
                else:
                    count_dies[d] += 1
            for m in moves:
                for k, v in m.items():
                    if v not in dies:
                        print(f'Invalid dice detected. Quitting\n{k} is not in {dies}')
                        exit(0)
                    count_dies[v] -= 1
            check_moves = False
            for k, v in count_dies.items():
                if v < 0:
                    print('Error; invalid moves detected')
                    exit(0)
                elif v > 0:
                    check_moves = True
            if check_moves:

                board_cp = self.get_board()
                hits = {k:v for k, v in self.__hits.items()}
                count_dies = {}
                for d in dies:
                    if not count_dies.get(d):
                        count_dies[d] = 1
                    else:
                        count_dies[d] += 1
                for m in moves:
                    print('helo?')
                    if len(m) > 1:
                        print("Invalid number of parameters")
                        exit(0)
                    for start, dice in m.items():
                        end = min(24, max(-1, start + dice * (1 if color=='black' else -1)))

                        if not self.move_is_valid(start, end, color, board_cp, v):
                            print(f'Error; invalid move {k} and {v}')
                            exit(0)
                        # end = start + max(24, min(-1, dice * (1 if color=='black' else -1)))
                        print('gets here')
                        self.make_move({start: end}, color, dice, board_cp, hits)
                        count_dies[dice] -= 1
                # getting the remaining dies
                arr = []
                for k, v in count_dies.items():
                    for i in range(v):
                        arr.append(k)
                for d in arr:
                    if self.has_valid_moves(color, d, board_cp):
                        print(f'Missing moves; {color} is disqualified')
                        print(count_dies)
                        exit(0)
            for m in moves:
                dice_val = 0
                for k, v in m.items():
                    dice_val = v
                self.make_move(m, color, dice_val)

    def roll_dies(self) -> [int]:
        dies = [randint(1, 6), randint(1, 6)]
        if dies[1] == dies[0]:
            dies += [dies[0], dies[0]]
        return dies
    def run(self):
        current_color = 'white'
        winner = None
        self.debug_board()
        # for i in range(10):
        while winner == None:
            dies = self.roll_dies()
            print(f'P1 ROLLED {dies}')
            self.make_move_player(self.__player1, 'white', dies, self.__hits['white'])
            dies = self.roll_dies()
            self.make_move_player(self.__player2, 'black', dies, self.__hits['black'])
            print(f'P2 ROLLED {dies}')
            self.debug_board()

            winner = self.get_winner()
        self.debug_board()
        print('winner is', winner)

            
             
    

# strategy to get all valid moves:
# 1. Create a copy of the board for the client side
# 2. Implement the checking for there as well with their choices
if __name__ == '__main__':
    g = Game('', '')
    # g.make_move({0: 6}, 'black', 6)
    # g.make_move({0: 6}, 'black', 6)
    # g.make_move({6: 9}, 'black', 3)
    # g.make_move({6:9}, 'black', 3)

    # g.debug_board()
    g.run()

