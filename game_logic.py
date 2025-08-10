from piece import Piece  # Import Piece class
from chain import Chain # Import chain class
from stone import Stone  # Import Piece class
from direction import Direction  # Import Direction class
from copy import deepcopy
class GameLogic:
    print("Game Logic Object Created")
    # Set board size
    size = 9
    boardWidth = size
    boardHeight = size
    # Data about current turn
    currentTurn = Piece.NoPiece
    # Data about previous turn
    previousTurn = Piece.NoPiece
    # Data about previous move of black
    previousStoneBlack = Stone(-1, -1, Piece.Black)
    # Data about previous move of white
    previousStoneWhite = Stone(-1, -1, Piece.White)
    # Amount of point for each player
    blackScore = 0
    whiteScore = 0
    # Amount of taken prisoners for each player
    blackPrisoners = 0
    whitePrisoners = 0
    # Amount of taken prisoners for each player for the last move
    blackPrisonersHistory = 0
    whitePrisonersHistory = 0
    # Amount of point for white because black begins
    komi = 7
    # Amount of passes in a row to determine the end of the game
    passCount = 0
    isFinished = False

    # Starts the game logic
    def __init__(self, parent):
        self.initLogic()

    # Initiates the game logic
    def initLogic(self):
        # Set up the board array

        self.boardWidth = self.size
        self.boardHeight = self.size
        self.boardArray = [[Piece.NoPiece for _ in range(self.boardWidth)] for _ in range(self.boardHeight)]
        # Data to store previous table allows user to make undo/redo
        self.boardArrayHistory = deepcopy(self.boardArray)
        # Set first turn to black
        self.currentTurn = Piece.Black

    # Allows players to pass their turn
    def passTurn(self):
        # Update amount of passes in a row
        self.passCount += 1
        # Check if game has ended
        if(self.passCount >= 2):
            # The game has ended, calculate points and determine winner
            print("Game has ended!")
            self.isFinished = True
            # Calculate the scores
            self.CalculateScores()
            # Output the winner
            if(self.blackScore < self.whiteScore):
                print("White won!")
            else:
                print("Black won!")
        # If we are still playing
        else:
            # Check whose turn it was
            if(self.currentTurn == Piece.Black):
                # If black passes, white gets 1 prisoner
                self.whitePrisoners += 1
            elif(self.currentTurn == Piece.White):
                # Otherwise if white passes, black gets 1 prisoner
                self.blackPrisoners += 1
        self.changeTurn()         
    # Allows user to roll the board back one move
    def undo(self):
        print("The previous step was undo, place the stone again")
        # Set current version to zero
        self.whitePrisoners = 0
        self.blackPrisoners = 0
        self.whiteScore = 0
        self.blackScore = 0
        self.boardArray = None
        # Update current version with a saved data 
        self.boardArray = self.boardArrayHistory
        # Change the turn so player can place the stone again
        self.changeTurn()
        

        
        
    # Place the stone // main method of the game logic file
    def placeStone(self, row, col):
        # Checks position
        if self.isCorrectCoordinates(row, col):
            # Checks if already occupied
            if (not self.isOccupied(row, col)):
                # Check for KO rule
                stoneToPlace = Stone(row, col, self.currentTurn)
                if self.checkKO(stoneToPlace):
                    # Check for suicide rule
                    if(self.checkSuicide(stoneToPlace)):
                        # Save board data before placing the stone
                        self.boardArrayHistory = deepcopy(self.boardArray)
                        # If everything is fine, place the stone
                        self.boardArray[stoneToPlace.row][stoneToPlace.col] = stoneToPlace
                        # Handle all the changes
                        self.neighboursCheckOneByOne(stoneToPlace)
                        # If stone was placed correctly, save turn and position as a previous move
                        self.previousTurn = stoneToPlace.player
                        # Save turn for black
                        if stoneToPlace.player == Piece.Black:
                            self.previousStoneBlack = Stone(stoneToPlace.row, stoneToPlace.col, Piece.Black)
                        # Save turn for white
                        if stoneToPlace.player == Piece.White:
                            self.previousStoneWhite = Stone(stoneToPlace.row, stoneToPlace.col, Piece.White)
                        # Print success message
                        print(f"Placed {stoneToPlace.player} stone on the [{stoneToPlace.row}, {stoneToPlace.col}].")
                        # Change turn
                        self.changeTurn()
                        # Update pass count to zero
                        self.passCount = 0
                        return True
                    # Error messages for each issue
                    else: 
                        print(f"Square [{stoneToPlace.row}, {stoneToPlace.col}] cannot be choosen because of suicide rule!")
                else:
                    print(f"Square [{stoneToPlace.row}, {stoneToPlace.col}] cannot be choosen because of KO rule!")
            else:
                print(f"Square [{row}, {col}] is already occupied!")
        else:
            print(f"Square [{row}, {col}] is out of boundary!")
        return False
    # Resets the game
    def reset(self):
        # Clear the board
        self.boardArray = [[Piece.NoPiece for _ in range(self.boardWidth)] for _ in range(self.boardHeight)]
        # Set first turn to black
        self.currentTurn = Piece.Black
        # Sets scores, prisoners to zero

        self.whitePrisoners = 0
        self.blackPrisoners = 0
        self.whiteScore = 0
        self.blackScore = 0
    # Changes turn
    def changeTurn(self):
        if self.currentTurn == Piece.Black:
            self.previousTurn = Piece.Black
            self.currentTurn = Piece.White
        elif self.currentTurn == Piece.White:
            self.previousTurn = Piece.White
            self.currentTurn = Piece.Black
    
    # Enforces the KO rule
    def checkKO(self, stoneToPlace):
        # Checks if previous move was the same for black
        if stoneToPlace.player == Piece.Black:
            return not self.previousStoneBlack.compare(stoneToPlace)
            
        # Checks if previous move was the same for white
        elif stoneToPlace.player == Piece.White:
            return not self.previousStoneWhite.compare(stoneToPlace)
        # If it was not the same, everything is good
        return True
    
    # Enforces the suicide rule, fails if surrounded by enemy
    def checkSuicide(self, stoneToPlace):
        return not self.isSurroundedByEnemy(stoneToPlace)
    
    # Removes any stone from the given coordinate
    def removeStone(self, row, col):
        self.boardArray[row][col] = Piece.NoPiece
        print(f"Stone on the [{row}, {col}] was removed")

    # Checks if a given chain has any liberties
    def hasAnyLibertiesChain(self, chain):
        for stone in chain.Stones:
            if(self.hasAnyLibertiesStone(stone)):
                return True
            
    # Checks if a given stone has liberties
    def hasAnyLibertiesStone(self, stone):
        result = 0
        # Check left
        if(not self.isOccupied(stone.row, stone.col - 1)):
            result += 1
        # Check right
        if(not self.isOccupied(stone.row, stone.col + 1)):
            result += 1
        # Check up
        if(not self.isOccupied(stone.row + 1, stone.col)):
            result += 1
        # Check down
        if(not self.isOccupied(stone.row - 1, stone.col)):
            result += 1
        if result == 0:
            print(f"Stone on the [{stone.row}, {stone.col}] has {result} liberties.")
        return result > 0
    
    # Checks if a given stone can live
    def isSurroundedByEnemy(self, stone):
        result = 0
        color = Piece.Black if stone.isSameColor(Piece.White) else Piece.White
        # Check left
        if(self.isOccupiedByPlayer(stone.row, stone.col - 1, color)):
            result += 1
        # Check right
        if(self.isOccupiedByPlayer(stone.row, stone.col + 1, color)):
            result += 1
        # Check up
        if(self.isOccupiedByPlayer(stone.row + 1, stone.col, color)):
            result += 1
        # Check down
        if(self.isOccupiedByPlayer(stone.row - 1, stone.col, color)):
            result += 1
        if result == 4:
            print(f"Stone on the [{stone.row}, {stone.col}] has {result} enemies around.")
        return result == 4
    
    # Checks if a given cell is occupied
    def isOccupied(self, row, col):
        # Return true if not correct or occupied
        return (not self.isCorrectCoordinates(row, col)) or self.boardArray[row][col] != Piece.NoPiece
    
    # Checks if a given cell is occupied by the specific player. Used for checking the suicide rule
    def isOccupiedByPlayer(self, row, col, enemyColor):
        # Return true if occupied by specific player
        return self.isCorrectCoordinates(row, col) and self.boardArray[row][col] != Piece.NoPiece and self.boardArray[row][col].isSameColor(enemyColor)

    # Checks if coordinates are correct
    def isCorrectCoordinates(self, row, col):
        return row < self.size and col < self.size and row >= 0 and col >= 0
    
    # Should be called after the stone is placed because of liberties check
    # Cheks if a given stone has any neighbours
    def neighboursCheckOneByOne(self, stone):
        # Check if there is no border on the left
        if (self.isCorrectCoordinates(stone.row, stone.col - 1)):
            # Calculate and get left neighbour
            leftNeighbour = self.boardArray[stone.row][stone.col - 1]
            # Hangdle left neighbour
            self.hangleNeighbour(stone, leftNeighbour)
        # Check if there is no border on the right
        if (self.isCorrectCoordinates(stone.row, stone.col + 1)):
            # Calculate and get right neighbour
            rightNeighbour = self.boardArray[stone.row][stone.col + 1]
            # Hangdle right neighbour
            self.hangleNeighbour(stone, rightNeighbour)
        # Check if there is no border on the top
        if (self.isCorrectCoordinates(stone.row - 1, stone.col)):
            # Calculate and get top neighbour
            topNeighbour = self.boardArray[stone.row - 1][stone.col]
            # Hangdle left neighbour
            self.hangleNeighbour(stone, topNeighbour)
        # Check if there is no border down
        if (self.isCorrectCoordinates(stone.row + 1, stone.col)):
            # Calculate and get left neighbour
            downNeighbour = self.boardArray[stone.row + 1][stone.col]
            # Hangdle left neighbour
            self.hangleNeighbour(stone, downNeighbour)

    # Check specific neighbour
    def hangleNeighbour(self, stone, neighbour):
        # Check if it's not an empty space
        if neighbour != Piece.NoPiece:
            # Check if it's same color
            if neighbour.hasSameColor(stone):
                # Handle friendly neighbour case
                self.handleFriend(stone, neighbour)
            # If the neighbour is enemy
            else: 
                # Handle enemy neighbour case
                self.handleEnemy(neighbour)

    # What should we do with a friend stone when placing the stone near
    def handleFriend(self, stone, friend):
        # Check if it has no chain yet
        if(friend.chain == None):
            # Create new chain
            chain = Chain()
            # Add there our stones
            chain.addStone(stone)
            chain.addStone(friend)
            # Add reference to this chain for stones
            stone.chain = chain
            friend.chain = chain
        # If the neighbour has it's own chain
        else:
            # Add the stone to this chain
            friend.chain.addStone(stone)
            # Add reference to this chain for the stone
            stone.chain = friend.chain
        

    # What should we do with an enemy stone when placing our stone near
    def handleEnemy(self, enemy):
        # If the enemy is a single stone and is not a part of any chain
        if(enemy.chain == None):
            # If the enemy enemy has no liberties, it's being captured
            if(not self.hasAnyLibertiesStone(enemy)):
                # Remove enemy from the board
                self.removeStone(enemy.row, enemy.col)
                # Add scores for capturing
                if(enemy.player == Piece.Black):
                    self.whitePrisoners += 1
                else:
                    self.blackPrisoners += 1
        # If the enemy has it's own chain
        else:
            # Check if the enemy chain has any liberties after placement
            if(not self.hasAnyLibertiesChain(enemy.chain)):
                # Remove every stone in this chain
                for stoneInChain in enemy.chain.Stones:
                    self.removeStone(stoneInChain.row, stoneInChain.col)
                    # Add scores for capturing
                    if(enemy.player == Piece.Black):
                        self.whitePrisoners += 1
                    else:
                        self.blackPrisoners += 1
        
    # Calculates amount of points for the territory and prisoners           
    def CalculateScores(self):
        # Set up scores
        whiteTotal = 0
        blackTotal = 0
        neutral = 0
        # Nested loop to analyze the board and territories
        for row in range(self.size):
            for col in range(self.size):
                # If this place is empty, calculate on which territory it is
                if(self.boardArray[row][col] == Piece.NoPiece):
                    whome = self.goIntoEachDirection(row, col)
                    if(whome == Piece.Black): blackTotal += 1
                    elif(whome == Piece.White): whiteTotal += 1
                    else: neutral += 1
        # After the whole cycle, set up the results, do not forget komi for black begins
        self.whiteScore = whiteTotal + self.whitePrisoners + self.komi
        self.blackScore = blackTotal + self.blackPrisoners
        print("Results are calculated!")
        
    # Goes into each direction and check which territory it is 
    def goIntoEachDirection(self, row, col):
        # Set up stone counters
        black = 0
        white = 0
        # Go each direction first and find each border
        left = self.goInDirection(row, col, Direction.Left) 
        right = self.goInDirection(row, col, Direction.Right) 
        up = self.goInDirection(row, col, Direction.Up) 
        down = self.goInDirection(row, col, Direction.Down) 
        # Calculate each direction
        # Left
        if(left == Piece.Black): black += 1
        elif(left == Piece.White): white += 1
        # Right
        if(right == Piece.Black): black += 1
        elif(right == Piece.White): white += 1
        # Up
        if(up == Piece.Black): black += 1
        elif(up == Piece.White): white += 1
        # Down
        if(down == Piece.Black): black += 1
        elif(down == Piece.White): white += 1
        # Return the result
        if black > 0 and white == 0: return Piece.Black
        if black == 0 and white > 0: return Piece.White
        # Otherwise it's no one's
        return Piece.NoPiece
        
        
        
    # Goes into one direction on the board, returns found stone color or -1 if border met
    def goInDirection(self, row, col, direction):
        # print(f"Checking the cell [{row}, {col}].")
        # If here is the border, return -1
        if not self.isCorrectCoordinates(row, col):
            return -1
        # If here is the stone, return color
        if(self.boardArray[row][col] != Piece.NoPiece):
            return self.boardArray[row][col].player
        # If there is nothing, keep going the same direction
        match direction:
            # Go left
            case Direction.Left:
                return self.goInDirection(row, col - 1, direction)
            # Go right
            case Direction.Right:
                return self.goInDirection(row, col + 1, direction)
            # Go up
            case Direction.Up:
                return self.goInDirection(row - 1, col, direction)
            # Go down
            case Direction.Down:
                return self.goInDirection(row + 1, col, direction)
                
        
                                
                            
                        
                    
                        
                        
            
    
    # Checks if a given stone laying on the border
    # def isOnBorder(self, stone):
    #     return stone.row == self.size - 1 or stone.col == self.size -1 or stone.row == 0 or stone.col == 0
    
    # def isInAngle(self, stone):
    #     return (stone.row == self.size - 1 and (stone.col == 0 or stone.col == self.size - 1)) or (stone.col == self.size - 1 and (stone.row == 0 or stone row == self.size - 1))

