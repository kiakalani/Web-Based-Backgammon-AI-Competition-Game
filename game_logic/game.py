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
                
    def move_is_valid(self, start: int, finish: int, color: str, board: [[str]], dice, hits=None) -> bool:
        if hits == None:
            hits = self.__hits
        # This takes care of verifying whether the piece has been hit
        if hits[color] != 0:
            if color == 'black':
                if start != -1:
                    return False
            elif color == 'white':
                if start != 24:
                    return False
            # This means the hit piece can be reloacted to correct position
            if len(board[finish]) == 0 or board[finish][0] == color:
                return True
            elif len(board[finish]) == 1 and board[finish][0] != color:
                return True
            return False
        if finish >= 0 and finish < 24 and start != 24 and start != -1:
        # This means a valid piece has been selected
            if len(board[start]) != 0 and board[start][0] == color:
                if len(board[finish]) == 0 or board[finish][0] == color:
                    return True
                elif len(board[finish]) == 1 and board[finish][0] != color:
                    # This would be a hit
                    return True
                # else:
                #     return False
            else:
                return False
        if self.__is_finishing(color, board):
            direction = (1 if color == 'black' else -1)
            # This means the move is exact
            if start + dice * direction == finish:
                return True
            if color == 'black':
                for i in range(18, start):
                    if len(board[i]) != 0 and board[i][0] == color:
                        return False
            else:
                for i in range(start + 1, 6):
                    if len(board[i]) != 0 and board[i][0] == color:
                        return False
            return True
        return False

    def has_valid_moves(self, color: str, dice: int, board=None, hits=None) -> bool:
        """
        This function returns true if there is a valid move
        with the given dice for the player otherwise false
        """
        if board == None:
            board = self.__board
        if hits == None:
            hits = self.__hits
        direction = 1 if color == 'black' else -1
        if hits[color] != 0:
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
            if self.move_is_valid(start, finish, color, board, dice, hits=hits):
                # if the player is finishing up, we don't want to add the piece
                # back to the board
                # hitting a piece takes place here
                if finish != -1 and finish != 24:
                    if len(board[finish]) == 1 and board[finish][0] != color:
                        hits['black' if color != 'black' else 'white'] += 1
                        board[finish].pop()
                # The scenarios where the piece is not being removed
                if (finish >= 0 and finish < 24):
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

    def __dies_valid(self, dies: [int], moves: [{int:int}]):
        if len(moves) > len(dies):
            return False
        for m in moves:
            for move, dice in m.items():
                if not dice in dies:
                    return False
        return True
    
    def __valid_moves_made(self, moves, dies, color, hits):
        board_cp = self.get_board()
        dies_cp = [d for d in dies]
        for m in moves:
            if len(m) != 1:
                return False
            for move, dice in m.items():
                finish = move + (dice * (1 if color == 'black' else -1))
                if not self.move_is_valid(move, finish, color, board_cp, dice, hits):
                    return False
                self.make_move(m, color, dice, board_cp, hits)
                dies_cp.remove(dice)
        for d in dies_cp:
            if self.has_valid_moves(color, d, board_cp, hits):
                return False
        return True


    def make_player_move(self, player, color: str, dies: [int], hits: int):
        # Getting the moves of the player
        moves = player.make_a_move(self.get_board(), [d for d in dies], color, hits)
        print(f'Player chose {moves}')
        if not self.__dies_valid(dies, moves):
            print(f"Invalid dies detected for color {color}. Quitting!")
            self.debug_board()
            exit(0)
        if not self.__valid_moves_made(moves, dies, color, {k: v for k, v in self.__hits.items()}):
            print(f"Invalid moves made for color {color}. Quitting")
            self.debug_board()
            exit(0)
        for m in moves:
            for move, dice, in m.items():
                finish = move + max(-1,min(24,(dice * (1 if color == 'black' else -1))))
                self.make_move(m, color, dice)
        self.debug_board()

    def roll_dies(self) -> [int]:
        dies = [randint(1, 6), randint(1, 6)]
        if dies[1] == dies[0]:
            dies += [dies[0], dies[0]]
        return dies
    def run(self):
        winner = None
        self.debug_board()
        # for i in range(10):
        for i in range(500):
            while winner == None:
                dies = self.roll_dies()
                print('-------')
                print(f'Dies {dies} for White')
                self.make_player_move(self.__player1, 'white', dies, {k : v for k, v in self.__hits.items()})
                dies = self.roll_dies()
                print('-------')
                print(f'Dies {dies} for black')
                self.make_player_move(self.__player2, 'black', dies, {k : v for k, v in self.__hits.items()})
                self.debug_board()

                winner = self.get_winner()
            self.debug_board()
            print('winner is', winner)
            winner = None
            self.__reset_board()
        print('Tests passed!')

            
             
# TODO: get player.py and game.py into a container.
# You can also save the moves they make into the db.
# With that you can have a match endpoint and show the
# players how their AI behaves against other AIs

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

