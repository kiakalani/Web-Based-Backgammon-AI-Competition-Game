"""
Author: Kia Kalani
Student ID: 101145220
This is file is responsible for running the game
and creating the competition between two AIs
"""

from random import randint


class Game:
    def __init__(self, player1, player2) -> None:
        self.__player1 = player1
        self.__player2 = player2
        self.__turn = False
        self.__round = 1
        self.__board = []
        self.__reset_board()
    
    def __is_finishing(self, color):
        """
        This function returns true if the given color
        has collected all of their pieces into their
        side otherwise false.
        :param: color: the color of the piece
        :return: true if the player is finishing up
        otherwise false
        """
        if color == 'white':
            for i in range(6, 24):
                if len(self.__board[i]) != 0 and self.__board[i][0] == 'white':
                    return False
        elif color == 'black':
            for i in range(18):
                if len(self.__board[i]) != 0 and self.__board[i][0] == 'black':
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
            if end == 16:
                    print('Color is', color, 'starting from', start)
            # This is the scenario where the pieces are the same color or position is empty
            if len(board[end]) == 0 or board[end][0] == color:
                
                return True
            # This will be hitting the oponent's piece and is valid
            elif len(board[end]) == 1 and board[end][0] != color:
                return True
        elif self.__is_finishing(color):
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
                moved_pieces = [i]
                # TODO: Proceed with the if statement to see if everything is valid
                # The looping would become way too complex
                # prev_roll += dice
                # for j in range(len(dies)):
                #     dice = dies[j]

                    
                #     dice_mv = i + move_dir * dice

                #     # This means the player can move the piece to the new location
                #     if len(cp_board[i]) != 0 and self.__move_is_valid(i, dice_mv, color, cp_board):
                #         valid_moves[i].append(dice_mv)
                #         tmp_piece = cp_board[i].pop()
                #         if dice_mv >= 0 and dice_mv < 24:
                #             cp_board[dice_mv].append(tmp_piece)
                #             if len(moved_pieces) - 1 < len(dies):
                #                 moved_pieces.append(dice_mv)
                    
                    
                    # This means the previous move was acceptable and we can check for
                    # the sum of the previous move with current move.
                    # if j != 0 and len(valid_moves[i]) != 0:
                    #     if i == 11:
                    #         print('Sum is ', prev_roll)
                    #     dice_mv = i + prev_roll * move_dir
                        
                    #     if self.__move_is_valid(i, dice_mv, color):
                    #         valid_moves[i].append(dice_mv)
                    #     else:
                    #         prev_roll -= dice
        return {key: value for key, value in valid_moves.items() if len(value) != 0}

            
                    
                


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
    game.debug_board()
    print(game.get_valid_moves([6, 1], 'white'))