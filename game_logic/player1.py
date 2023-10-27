from player import Player


class AIPlayer(Player):
    """
    This class is a wrapper for your implementation of Backgammon AI.
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super().__init__("Player 2")

    def make_a_mock_move(self, move: {int: int}, board: [[str]], hits: {str: int}, color: str) -> None:
        """
        A method for making a mock move.
        :param: move: the dictionary that contains a single move where key is the row that a piece
        is being moved from and value is the value of the dice.
        :param: board: a copy of the board which was sent to the player for the details about
        the board.
        :param: hits: the number of pieces that are hit for each player stored in dictionary.
            example: hits['black'] contains the number of pieces that have been hit for the
            black player.
        :param: color: the color that you are playing as.
        :return: None
        """

        super().make_a_mock_move(move, board, hits, color)

    def all_valid_moves(self, board: [[str]], dice: int, color: str, hits: int) -> [{int: int}]:
        """
        This method returns an array containing all of the valid moves your AI would be
        able to make.
        :param: board: a copy of the board which was sent to the player for the details about
        the board.
        :param: dice: the value of the dice for which we are trying to get all the valid moves
        from.
        :param: color: this parameter refers to the color you are playing as.
        :param: hits: refers to the current number of hits you have.
        :return: an array of dictionary with a single key refering to the start position and with
        the value of dice.
        """
        return super().all_valid_moves(board, dice, color, hits)


    def move_is_valid(self, start: int, finish: int, color: str, board: [[str]], dice: int, hits:int) -> bool:
        """
        A method that determines if a given move is valid.
        :param: start: the start position of the move.
        :param: finish: the position of the piece after move is made.
        :param: color: the color that you are playing as.
        :param: board: a copy of the board which was sent to the player for the details about
        the board.
        :param: The dice value that was played to make this move.
        :param: hits: this refers to the value of hits[color].
        :return: true if the move is valid; otherwise false
        """
        return super().move_is_valid(start, finish, color, board, dice, hits)

    def has_valid_moves(self, board: [[str]], dies: [int], color: str, hits: int) -> bool:
        """
        This method would return true if there are any valid moves left; otherwise false.
        :param: board: a copy of the board which was sent to the player for the details about
        the board.
        :param: dies: the array of dies
        :param: color: the color that you are playing as.
        :param: hits: the value of hits for your color.
        """
        return super().has_valid_moves(board, dies, color, hits)
    
    def random(self):
        """
        The random library
        """
        return super().random()
    
    def math(self):
        """
        The math library
        """
        return super().math()
        
    
    def make_a_move(self, board: [[str]], dies: [int], color: str, hits: {str: int}) -> [{ int: int }]:
        """
        This function will be called to receive the moves your AI is going to make.
        :param: board: a copy of the actual board to show how the game currently looks like.
        :param: dies: the dies you have rolled stored as an array of integers.
        :param: color: the color you are playing as.
        :param: hits: the total number of hits each player has stored in a dictionary format.
            For example: hits['black'] refers to the total number of hits the black player has
            received.
        :return: an array of dictionaries with a single element stored in each.
        """

        # Write your own code in place of the code below.

        # Array of moves
        moves = []

        # If there are no valid moves, there is no point for trying to make a move
        # This would also become false when you have played all your dies.
        while self.has_valid_moves(board, dies, color, hits[color]):
            # Iterating through the dies for making moves
            for i in range(len(dies) - 1, -1, -1):
                # Getting all the valid moves for the dice at position i
                move = self.all_valid_moves(board, dies[i], color, hits[color])
                # This means that the dice at position i has at least one valid move
                if len(move) != 0:
                    # Making a random valid move
                    move = move[self.random().randint(0, len(move) - 1)]
                    moves.append(move)
                    # Updating the boad copy so the new possible moves would become valid
                    self.make_a_mock_move(move, board, hits, color)
                    # Removing the dice your AI just played.
                    dies.pop(i)
        return moves
