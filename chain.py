from piece import Piece  # Import the piece class
from stone import Stone  # Import the stone class
# Represents chain of stones
class Chain:
    Stones = []
    
    # Initiates a new chain
    def __init__(self):
        self.Stones = []
    
    # Adds a new stone
    def addStone(self, stone):
        # Check if a given stone is already in our chain
        if not(self.isAlreadyIn(stone)):
            # Check if it has it's own chain
            if stone.chain != None:
                # Merge two chains if it has it's own chain
                self.MTCA(stone.chain)
            else:
                # Otherwise just add this stone to the chain
                self.Stones.append(stone)
                # Add reference to the chain for this stone
                stone.chain = self
    
    # Removes stone from the chain
    def removeStone(self, stone):
        # Remove the reference
        stone.chain = None
        # Remove the stone
        self.Stones.remove(stone)
            
        
        
    # Checks if a stone is already in the chain
    def isAlreadyIn(self, stone):
        # Check every stone in the chain
        for stoneIn in self.Stones:
            # If foud the same, return true
            if(stoneIn.compare(stone)):
                return True
        return False
    
    # MERGIN TWO CHAINS ALGORITHM p.s. see documentation
    def MTCA(self, chainGiven):
        # Iterate throug every stone in a given chain
        for stoneGiven in chainGiven.Stones:
            # Remove this stone from the given chain
            chainGiven.removeStone(stoneGiven)
            # Add every stone to our chain
            self.addStone(stoneGiven)
        