"""
Author: Kia Kalani
Student ID: 101145220
This module contains the abstract class for
how the Player class should originally look like.
In addition, the players would inherit this class
and use the provided methods to write a better
implementation for their AI.
"""
import random
import math
class Player:
    """
    An abstract class for the player instances that would be
    making the moves
    """

    def __init__(self, name: str) -> None:
        """
        Constructor
        """
        self.__player_name = name

    def get_name(self) -> str:
        """
        Getter for player's name
        """

        return self.__player_name

    def __is_finishing(self, color: str, board: [[str]]) -> bool:
        """
        Check to see if the player is finishing up with their pieces
        :param: color: The player's color.
        :param: board: The current board.
        :return: True if player is finishing otherwise false.
        """

        for i in range(18):
            index = i if color == 'black' else 23 - i
            if len(board[index]) != 0 and color == board[index][0]:
                return False
        return True

    def make_a_mock_move(self, move: {int: int}, board: [[str]], hits: {str: int}, color: str) -> None:
        """
        A helper function for allowing the players to make a mock move
        to see the upcoming valid moves afterward.
        :param: move: the move dictionary.
        :param: board: the mock board that was sent from the game class
        :param: hits: the mock hits object
        """

        for start, dice in move.items():
            if start > -1 and start < 24:
                board[start].pop()
            else:
                hits[color] -= 1
            end_pos = start + dice * (1 if color == 'black' else -1)
            if end_pos >= 0 and end_pos < 24:
                if len(board[end_pos]) == 1 and color != board[end_pos][0]:
                    board[end_pos].pop()
                board[end_pos].append(color)
        
    def random(self):
        """
        A method to provide the random library
        to the users since they can't import
        anything.
        :return: The random library
        """
        return random

    def math(self):
        """
        A method to provide the math library
        to the users since they can't import
        anything.
        :return: The math library
        """
        return math

    def move_is_valid(self, start: int, finish: int, color: str, board: [[str]], dice, hits:int) -> bool:
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
            
            if color == 'black':
                if start + dice * direction == 24:
                    return True
                for i in range(18, start):
                    if len(board[i]) != 0 and board[i][0] == color:
                        return False
            else:
                if start + dice * direction == -1:
                    return True
                for i in range(start + 1, 6):
                    if len(board[i]) != 0 and board[i][0] == color:
                        return False
            return True
        return False

    def all_valid_moves(self, board: [[str]], dice: int, color: str, hits: int) -> [{int: int}]:
        """
        Getter for all of the valid moves for a given dice
        :param: board: The current board.
        :param: dice: The dice the player is trying to play
        :param: color: The color of the current player.
        :param: hits: The number of hits the current player has
        :return: All of the valid moves for the given dice.
        """

        direction = 1 if color == 'black' else -1
        if hits > 0:
            start_pos = 24 if color == 'white' else -1
            if self.move_is_valid(start_pos, (start_pos + (dice * direction)), color, board, dice, hits):
                return [{start_pos: dice}]
            return []
        valids = []
        for i in range(24):
            if len(board[i]) != 0 and board[i][0] == color:
                if self.move_is_valid(i, i + (dice * direction), color, board, dice, hits):
                    valids.append({i: dice})
        
        return valids

    def has_valid_moves(self, board: [[str]], dies: [int], color: str, hits: int) -> bool:
        """
        This method would return true if the player has valid moves; otherwise false.
        :param: board: The current board.
        :param: dies: The dies the player has rolled.
        :param: color: The color of the current player.
        :param: hits: The number of hits the current player has
        :return: True if the player has a valid move; otherwise, false.
        """

        for d in dies:
            if len(self.all_valid_moves(board, d, color, hits)) != 0:
                return True
        return False

    def make_a_move(self, board: [[str]], dies:[int], color: str, hits: {str: int}) -> [{int: int}]:
        """
        This will be the function that would be called for
        players to make a move.
        """

        return [{} for d in dies]
    