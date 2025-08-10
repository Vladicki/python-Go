from piece import Piece  # Import the piece class
# Class that represents stone
class Stone():
    # Coordinates of a stone
    row = -1
    col = -1
    player = Piece.NoPiece
    chain = None
    
    # Initiates a new stone
    def __init__(self, row, col, player):
        self.row = row
        self.col = col
        self.player = player

    # Returns true if two stones are equal
    def compare(self, secondStone):
        return self.row == secondStone.row and self.col == secondStone.col and self.player == secondStone.player
    
    # Checks if a given stone has the same color
    def hasSameColor(self, stone):
        return self.player == stone.player
    
    # Checks if a given color is the same color
    def isSameColor(self, color):
        return self.player == color