"""
Author: Kia Kalani
Student ID: 101145220
This is file is responsible for running the game
and creating the competition between two AIs
"""

from random import randint
# a better idea:
# how about having the players sending their moves in array format
# and you error check their moves

class Game:
    def __init__(self, player1, player2) -> None:
        self.__player1 = player1
        self.__player2 = player2
        self.__turn = False
        self.__round = 1
        self.__board = []
        self.__board = [[] for i in range(24)]
        self.__board[17] = ['white', 'white', 'white']
        # self.__reset_board()
    
    def __is_finishing(self, color,  board):
        """
        This function returns true if the given color
        has collected all of their pieces into their
        side otherwise false.
        :param: color: the color of the piece
        :return: true if the player is finishing up
        otherwise false
        """
        if color == 'white':
            for i in range(18):
                if len(board[i]) != 0 and board[i][0] == 'white':
                    return False
        elif color == 'black':
            for i in range(6, 24):
                if len(board[i]) != 0 and board[i][0] == 'black':
                    return False
        return True

    def __move_is_valid(self, start, end, color, board):
        """
        This function would return true if the given move for the
        given color is valid.
        :param: start: the position the piece is currently at
        :param: end: the position we want to see is valid or not.
        :return: True if move is valid otherwise false
        """
        # TODO: Moving the last piece is not currently considered in is finishing
        # TODO: Create a mock board for multiple rolls to make sure the output would be
        # correct
        
        if end > 0 and end < 24:
            # This is the scenario where the pieces are the same color or position is empty
            if len(board[end]) == 0 or board[end][0] == color:
                
                return True
            # This will be hitting the oponent's piece and is valid
            elif len(board[end]) == 1 and board[end][0] != color:
                return True
        elif self.__is_finishing(color, board):
            # This means removing the piece in the exact position which should be
            # valid
            if end == 0 or end == 24:
                return True
            elif color == 'white' and end > 24:
                # This means there is a piece before this piece that needs to be
                # removed first
                for i in range(18, start):
                    if len(board[i]) != 0 and board[i][0] == color:
                        return False
                return True
            elif color == 'black' and end < 0:
                # This means there is a piece before this piece that needs to be
                # removed first
                for i in range(5, start, -1):
                    if len(board[i]) != 0 and board[i][0] == color:
                        return False
                return True

        return False




    def __get_cp_board(self):
        cp_board = [[] for i in range(24)]
        for i in range(24):
            for item in self.__board[i]:
                cp_board[i].append(item)
        return cp_board
    
    def get_valid_moves(self, dies, color):
        """
        A function that would provide all possible moves for 
        the given color.
        """
        valid_moves = {}
        move_dir = 1 if color == 'white' else -1
        for i in range(24):
            valid_moves[i] = []
            pos_len = len(self.__board[i])
            # this means this move can be potentially valid.
            if pos_len != 0 and color == self.__board[i][0]:
                # prev_roll = 0
                cp_board = self.__get_cp_board()

                if len(dies) == 2:
                    first_dice = i + dies[0] * move_dir
                    second_dice = i + dies[1] * move_dir
                    sum_dice = i + (dies[0] + dies[1]) * move_dir
                    if self.__move_is_valid(i, first_dice, color, cp_board):
                        valid_moves[i].append({'pos': first_dice, 'value': 1})
                    if self.__move_is_valid(i, second_dice, color, cp_board):
                        valid_moves[i].append({'pos': second_dice, 'value': 1})
                    if len(valid_moves[i]) != 0:
                        tmp = cp_board[i].pop()
                        cp_board[valid_moves[i][0]['pos']].append(tmp)
                        if self.__move_is_valid(valid_moves[i][0]['pos'], sum_dice, color, cp_board):
                            valid_moves[i].append({'pos': sum_dice, 'value': 2})
                    # Consider the count of the pieces when doing this
                else:
                    dice_val = dies[0]
                    dice_mv = i + dice_val * move_dir
                    if self.__move_is_valid(i, dice_mv, color, cp_board):
                        pos_len = len(cp_board[i])
                        for j in range(min(4, pos_len)):
                            valid_moves[i].append({'pos': dice_mv, 'value': j + 1})
                    len_valids = len(valid_moves[i])
                    if len_valids != 0:
                        sum_dice = dice_mv
                        # Current position

                        for k in range(3):
                            c_board = self.__get_cp_board()

                            prev_iteration = [item for item in valid_moves[i]]
                            cur_pos = valid_moves[i][0]['pos'] + k * dice_val * move_dir
                            sum_dice += dice_val * move_dir
                            # This should be sufficient for seeing whether the move would
                            # allow emptying or not
                            moving_pieces = min(2 + k, len(c_board[i]))
                            # print(moving_pieces)
                            for j in range(moving_pieces):
                                c_board[i].pop()
                                print(cur_pos)
                                if cur_pos >= 0 and cur_pos < 24:
                                    c_board[cur_pos].append(color)
                            print(c_board)

                            if self.__move_is_valid(dice_mv, sum_dice, color, c_board):
                                
                                for item in prev_iteration:
                                    if item['pos'] == cur_pos:
                                        for j in range(item['value'] + 1, 5):
                                            valid_moves[i].append({'pos': sum_dice, 'value': j})
        # Restructuring the data in a representative manner for the players
        ret_dict = {}
        for key, value in valid_moves.items():
            ret_dict[key] = {}
            for item in value:
                pos = item['pos'] if item['pos'] >= 0 and item['pos'] < 24 else 24 if item['pos'] > 23 else -1 
                if not ret_dict[key].get(pos):
                    ret_dict[key][pos] = set()
                ret_dict[key][pos].add(item['value'])
        for key, value in ret_dict.items():
            for k, v in value.items():
                value[k] = list(v)
        return {key: value for key, value in ret_dict.items() if len(ret_dict[key]) != 0}
        
    def make_a_move(self, moves, dies, color):
        # Error checking the given move
        sum_moves = 0
        for m in moves:
            for mm in moves[m]:
                if not self.__move_is_valid(m, mm, color, self.__board):
                    return False
                sum_moves += moves[m][mm]
        if sum_moves != len(dies):
            return False
        # Making the moves
        direction = -1 if color == 'black' else 1
        for m in moves:
            for mm in moves[m]:
                if moves[mm][m] > 1:
                    # Check the count of the moves
                    # Place the pieces in their proper spot
                    pass

            
                    
                


    def __reset_board(self):
        empty_board = [[] for i in range(24)]
        for _ in range(2):
            empty_board[0].append('white')
            empty_board[23].append('black')
        for _ in range(5):
            empty_board[5].append('black')
            empty_board[11].append('white')
            empty_board[12].append('black')
            empty_board[18].append('white')
        for _ in range(3):
            empty_board[7].append('black')
            empty_board[16].append('white')
        self.__board = empty_board

    def debug_board(self):
        print(self.__board)
    
        

        


    def __play_player(self, player):
        """
        Running the code from docker container and sending the
        parameters.
        :param: the player instance
        """
        pass

    def __is_game_over(self):
        pass

    def run_game():
        pass

if __name__ == '__main__':
    game = Game('', '')
    import pprint; pprint.pprint(game.get_valid_moves([6, 6, 6, 6], 'white'))