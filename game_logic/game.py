"""
Author: Kia Kalani
Student ID: 101145220
This module deals with running the
competition between the two provided
AIs. They would be stored in files named
player1 and player2 and ran in a container
to ensure the security of the procedure.
"""

import json
import signal
from random import randint

import player1
import player2
from player import Player

def timeout_exception(self, signum, frame):
    """
    A method for providing the timeout exception
    if user's implementation takes more than a second
    """

    raise Exception('Timeout occured')

class Game:
    """
    This class will run the competition between two AIs.
    """

    def __init__(self) -> None:
        """
        Constructor
        """

        self.__player1 = player1.AIPlayer()
        self.__player2 = player2.AIPlayer()
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
        Check to see if the player is finishing up with their pieces.
        :param: color: The current player's color.
        :param: board: The current board in the game.
        :return: True if the player is finishing; otherwise false.
        """

        for i in range(18):
            index = i if color == 'black' else 23 - i
            if len(board[index]) != 0 and color == board[index][0]:
                return False

        return True

    def get_winner(self) -> str:
        """
        Returns the winner of the game.
        :return: a string mentioning the color of the winner.
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
                
    def move_is_valid(
        self, start: int, finish: int,
        color: str, board: [[str]], dice, hits=None
    ) -> bool:
        """
        A method that specifies whether the move that the player is
        trying to make is valid.
        :param: start: The start position of the piece.
        :param: finish: The end position of the move.
        :param: color: The color of the current player.
        :param: board: The current board.
        :param: dice: The dice that the player rolled.
        :param: hits: Would specify whether the player has pieces
        that are hit and need to be moved first.
        :return: True if the move is valid; otherwise false.
        """

        if hits == None:
            # This means, we are using the function for 
            # direct instance of the board.
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
        with the given dice for the player otherwise false.
        :param: color: The color of the current player
        :param: dice: The specific dice the current player has rolled.
        :param: board: The board instance.
        :param: hits: The number of hits each player has associated with them.
        """

        # If not specified, that means we are dealing with the
        # direct instances.
        if board == None:
            board = self.__board
        if hits == None:
            hits = self.__hits

        direction = 1 if color == 'black' else -1
        if hits[color] != 0:
            # If they are hit, they have to move their hit pieces first.
            # If they can't, they have no valid moves for this dice.
            pos = (dice * direction) + (-1 if color == 'black' else 24)
            if len(board[pos]) != 0 and board[pos][0] != color:
                return False
            return True
        else:
            for i in range(24):
                # Looping through all of the positions and checking whether there
                # is a piece that has a valid move for the rolled dice.
                if len(board[i]) != 0 and board[i][0] == color:
                    if self.move_is_valid(i, i + dice * direction, color, board, dice):
                        return True
            return False
            
                
    def make_move(self, move:{int:int}, color: str, dice: int, board=None, hits=None) -> None:
        """
        This function is responsible for making a move by the given parameters.
        :param: move: A dictionary where key is the start position and value is the
            dice the piece is going to move by.
        :param: color: The color of the current player.
        :param: dice: The current dice the player rolled.
        :param: board: The board instance.
        :param: hits: The total hits each player has
        """

        # Making sure appropriate instances are selected.
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
        This function returns a copy of the board.
        :return: a copy of the board
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
        """
        A method to validate whether the moves made
        are corresponding to valid dies.
        """

        if len(moves) > len(dies):
            return False

        for m in moves:
            for move, dice in m.items():
                if not dice in dies:
                    return False
        return True
    
    def __valid_moves_made(
        self, moves: [{int:int}], dies: [int], color: str, hits: {str:int}
    ):
        """
        A helper function to check whether valid moves
        are made or not.
        """

        # Creating copies for not modifying the originals
        board_cp = self.get_board()
        dies_cp = [d for d in dies]

        for m in moves:
            if len(m) != 1:
                return False
            for move, dice in m.items():
                finish = move + (dice * (1 if color == 'black' else -1))
                if not self.move_is_valid(move, finish, color, board_cp, dice, hits):
                    # The player is trying to make an invalid move.
                    return False
                self.make_move(m, color, dice, board_cp, hits)
                dies_cp.remove(dice)

        for d in dies_cp:
            if self.has_valid_moves(color, d, board_cp, hits):
                # That means the player is missing a move
                return False
        return True
    

    def make_player_move(
        self, player, color: str, dies: [int], hits: int, game_outcome: dict
    ) -> bool:
        """
        A method to do all the necessary checks and make the move for
        the player.
        :param: player: The player instance.
        :param: color: The player's color
        :param: dies: The dies the player has rolled.
        :param: hits: The number of hits of the current player's pieces.
        :param: game_outcome: A dictionary to track the moves made in the
        game.
        :return: True if the move has been made successfully; otherwise False
        """

        # Getting the moves of the player
        signal.signal(signal.SIGALRM, timeout_exception)
        signal.alarm(1)
        try:
            # Making sure making a move doesn't take more than a second
            moves = player.make_a_move(self.get_board(), [d for d in dies], color, hits)
        except Exception as e:
            return False
        
        # Check to see if the player plays the dies associated with them
        if not self.__dies_valid(dies, moves):
            return False
        # Check to see if the player is trying to make valid moves
        if not self.__valid_moves_made(moves, dies, color, {k: v for k, v in self.__hits.items()}):
            return False
        
        # Playing the moves on the board since everything is validated
        for m in moves:
            for _, dice, in m.items():
                self.make_move(m, color, dice)
        
        # Tracking the move the player made
        game_outcome['rounds'][-1]['moves'].append({
            'color': color,
            'dies': dies,
            'moves': moves
        })

        return True

    def roll_dies(self) -> [int]:
        """
        This function returns the array of dies that the player
        rolled.
        :return: an array of integers where each of them are between
        1 and 6.
        """
        dies = [randint(1, 6), randint(1, 6)]
        if dies[1] == dies[0]:
            dies += [dies[0], dies[0]]
        return dies
    
    def get_winner_points(self) -> int:
        """
        A function for getting the points of the winner.
        :return: an integer indicating the points of the player.
        """
        colors = {'black': 0, 'white': 0}
        for r in self.__board:
            r_len = len(r)
            if r_len != 0:
                colors[r[0]] += r_len
        if colors['black'] == 0:
            return 2 if colors['white'] == 15 else 1
        elif colors['white'] == 0:
            return 2 if colors['black'] == 15 else 1
        else:
            return 0
    def __assign_colors(self) -> {str: Player}:
        """
        A simple function to decide which AI is playing as
        what color
        :return: a dictionary that assigns colors to the players
        """
        ret_dict = {'white': self.__player1 if randint(1, 2) == 1 else self.__player2}
        ret_dict['black'] = self.__player1 \
            if ret_dict['white'] != self.__player1 else self.__player2
        return ret_dict

    def run(self) -> dict:
        """
        This method would run the game and provide its result.
        :return: A dictionary containing the winner, loser, the scores,
        the colors associated with each player, and all the moves made
        for each round.
        """
        game_outcome = {
            'scores': {
                'white': 0,
                'black': 0
            },
            'colors': self.__assign_colors(),
            'winner': None,
            'rounds': []
        }
        first_turn = second_turn = ''
        while game_outcome['scores']['white'] < 7 and game_outcome['scores']['black'] < 7:
            # Deciding who plays first
            if game_outcome['scores']['white'] == 0 and game_outcome['scores']['black'] == 0:
                first_turn = 'white' if randint(1,2) == 1 else 'black'
                second_turn = 'white' if first_turn != 'white' else 'black'
            game_outcome['rounds'].append({'winner': None, 'moves': []})
            self.__reset_board()
            while len(game_outcome['rounds']) == 0 or game_outcome['rounds'][-1]['winner'] == None:
                dies = self.roll_dies()
                # If make_player_move functions return false, it would mean the player tried to do
                # something illegal
                if not self.make_player_move(
                    game_outcome['colors'][first_turn], first_turn, dies,
                    {k: v for k,v in self.__hits.items()}, game_outcome
                ):
                    game_outcome['scores'][first_turn] = 0
                    game_outcome['scores'][second_turn] = 7
                    game_outcome['winner'] = game_outcome['colors'][second_turn]
                    game_outcome['rounds'] = []
                    return game_outcome
                dies = self.roll_dies()
                game_outcome['rounds'][-1]['winner'] = self.get_winner()
                # If this has a value, it would mean the first player won the round
                if game_outcome['rounds'][-1]['winner']:
                    break
                if not self.make_player_move(
                    game_outcome['colors'][second_turn], second_turn, dies,
                    {k: v for k, v in self.__hits.items()}, game_outcome
                ):
                    game_outcome['scores'][second_turn] = 0
                    game_outcome['scores'][first_turn] = 7
                    game_outcome['winner'] = game_outcome['colors'][first_turn]
                    game_outcome['rounds'] = []
                    return game_outcome
                game_outcome['rounds'][-1]['winner'] = self.get_winner()
            # Adding the score for the appropriate player
            game_outcome['scores'][game_outcome['rounds'][-1]['winner']] += self.get_winner_points()
            # Setting the player's turn according to the color
            first_turn = game_outcome['rounds'][-1]['winner']
            second_turn = 'white' if game_outcome['rounds'][-1]['winner'] == 'black' else 'black'
        # Setting the total winner of the game
        game_outcome['winner'] = game_outcome['colors']['white'].get_name() \
            if game_outcome['scores']['white'] >= 7 else\
                game_outcome['colors']['black'].get_name()
        game_outcome['colors'] = {k: v.get_name() for k, v in game_outcome['colors'].items()}
        return game_outcome

if __name__ == '__main__':
    g = Game()
    print(json.dumps(g.run()))
