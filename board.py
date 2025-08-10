from PyQt6.QtWidgets import QFrame, QMessageBox  , QPushButton , QSizePolicy,QGraphicsColorizeEffect, QApplication, QWidget,QVBoxLayout, QRadioButton, QPushButton, QHBoxLayout, QLabel, QMessageBox, QDialog, QDialogButtonBox, QLabel, QPushButton, QRadioButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint,QRect, QPointF,QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon,QBrush, QFont


from piece import Piece  # Import the Piece class
from game_logic import GameLogic
from stone import Stone  # Import Piece class


class Board(QFrame):  # Base the board on a QFrame widget
    updateTimerSignal = pyqtSignal(int, int)  # Signal sent when the timer is updated
    clickLocationSignal = pyqtSignal(str)  # Signal sent when there is a new click location
    squareSize = gap =  0
    radius = 0
    timerSpeed = 1000  # the timer updates every 1 second
    boardCoord = 0

    # Default configuration
    size = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selector = GoBoardSizeSelector()
        self.selector.sizeSelected.connect(self.initializeBoard)  # Connect size selection to initialization
        self.selector.show()  # Show the size selector immediately

        self.gameLogic = GameLogic(self)
        self.gameControlWidget = None  # Add a reference to the GameControlWidget

        self.isStarted = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)

        self.player1_time = 600  # 10 minutes for player 1
        self.player2_time = 600  # 10 minutes for player 2
        self.current_player = 1  # Player 1 starts first


    def switchTurn(self):
        """Switches the turn and adds 5 seconds to the new current player's timer."""
        # if self.current_player == 1:
        #     self.player2_time += 5
        #     self.current_player = 2

        # else:
        #     self.player1_time += 5
        #     self.current_player = 1

        # # Update the label in the GameControlWidget
        # self.gameControlWidget.update_current_label(self.current_player)

        # print(f"Switching turn to Player {self.current_player}")



    def timerEvent(self):
        """Handles the timer event."""
        if self.current_player == 1:
            self.player1_time -= 1
            if self.player1_time <= 0:
                print("Black players time is up! Game over.")


                # self.resetGame()
                self.timer.stop()
                
        else:
            self.player2_time -= 1
            if self.player2_time <= 0:
                print("White players time is up! Game over.")
                        
                
                # self.resetGame()
                self.timer.stop()
                

        # Emit updated timer values
        self.updateTimerSignal.emit(self.player1_time, self.player2_time)


        # Emit updated timer values
        self.updateTimerSignal.emit(self.player1_time, self.player2_time)

    def handleTurnChange(self):
        """Handles a turn change (e.g., when a player finishes their turn)."""
        self.switchTurn()
        print(f"Player 1 time: {self.player1_time} seconds, Player 2 time: {self.player2_time} seconds")


    def paintEvent(self, event):
        if self.size is None:
            return

        painter = QPainter(self)
        self.drawBoard(painter, self.size)

        
        self.drawPieces(painter)
         




    def initializeBoard(self, size):
        '''Initializes the board with the selected size'''
        self.gameLogic = GameLogic(self)
        self.size = size
        self.boardWidth = self.boardHeight = self.size

        if not self.gameControlWidget:
            self.gameControlWidget = GameControlWidget(self, self.gameLogic, None, self.boardCoord)
            self.gameControlWidget.show()
            self.gameControlWidget.update_current_label(self.current_player)
            # Connect the updateTimerSignal to the display method
            self.updateTimerSignal.connect(self.gameControlWidget.update_timer_display)


        # Initialize the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)

        # Initialize the board array with `Piece.NoPiece`
        self.boardArray = [[Piece.NoPiece for _ in range(self.boardWidth)] for _ in range(self.boardHeight)]

        self.isStarted = False
        self.start()
        self.update()
        self.printBoardArray()

        # Create the GameControlWidget once the board is drawn

        # self.gameControlWidget.updateMargin()





    def mousePosToColRow(self, event):
        '''Convert the mouse click event to a row and column, accounting for the gap.'''
        pos = event.position()  # Get the position of the mouse event

        # squareSize = int(min(self.width(), self.height()) / (self.size + 2))
        gap = self.squareSize
        
        # print(gap)
        # print(self.radius)
    
        # Adjust the position to account for the gap
        adjustedX = pos.x() - gap + self.radius
        adjustedY = pos.y() - gap + self.radius

        # Check if the click is within the board boundaries
        if 0 <= adjustedX < self.boardWidth * self.squareSize and 0 <= adjustedY < self.boardHeight * self.squareSize:
            col = int(adjustedX // self.squareSize)  # Calculate column index
            row = int(adjustedY // self.squareSize)  # Calculate row index
            return row, col
        else:
            # If outside the board, return an invalid position
            return -1, -1


    def mousePressEvent(self, event):
        '''Handles mouse press events to place pieces on the board.'''
        pos = event.position()  # Get the position of the mouse event
        clickLoc = f"click location [{int(pos.x())}, {int(pos.y())}]"  # Log the click location
        # print("mousePressEvent() - " + clickLoc)

        # Determine the row and column of the click
        row, col = self.mousePosToColRow(event)
        
        if row != -1 and col != -1:
            # Only attempt to move if the click is within a valid square



            if (self.gameLogic.placeStone(row, col)):
                if self.current_player == 1:
                    self.player2_time += 5
                    self.current_player = 2

                else:
                    self.player1_time += 5
                    self.current_player = 1

                # Upda  te the label in the GameControlWidget
                self.gameControlWidget.update_current_label(self.current_player)

                print(f"Switching turn to Player {self.current_player}")

            # self.switchTurn()
            
            self.update()  # Redraw the board
            self.printBoardArray()


            # self.tryMove(row, col)

        self.clickLocationSignal.emit(clickLoc)


    def tryMove(self, row, col):
        '''Attempts to place a piece on the board'''

        if self.boardArray[row][col] == Piece.NoPiece:
            self.boardArray[row][col] = Piece.Black  # Example: place a Black piece

            
        # Update the label in the GameControlWidget
            self.gameControlWidget.update_current_label(self.current_player)
            self.update()  # Redraw the board
            self.printBoardArray()
        else:
            print(f"Square [{row}, {col}] is already occupied!")


    def reset(self):
        '''Clears pieces from the board'''
        """Resets the game and timers."""
        self.player1_time = 600
        self.player2_time = 600
        self.blackPrisoners = 0
        self.whitePrisoners = 0
        self.gameLogic.isFinished = False
        self.gameLogic.reset()

        self.current_player = 1
        self.gameControlWidget.update_current_label(self.current_player)

        self.updateTimerSignal.emit(self.player1_time, self.player2_time)
        self.boardArray = [[Piece.NoPiece for _ in range(self.boardWidth)] for _ in range(self.boardHeight)]
        self.update()  # Trigger repaint to show cleared board

        
    def printBoardArray(self):
        '''prints the boardArray in an attractive way'''
        boardArray = self.gameLogic.boardArray
        print("boardArray:")
        
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in boardArray]))

    
    def start(self):
        '''starts game'''
        self.isStarted = True  # set the boolean which determines if the game has started to TRUE
        self.reset()  # reset the game
        self.timer.start(self.timerSpeed)  # start the timer with the correct speed
        print("start () - timer is started")



    def boardCoord_getter(self):
        return self.boardCoord
    

    def timerEvent(self):
        """Handles the timer event."""
        if self.current_player == 1:
            self.player1_time -= 1
            if self.player1_time <= 0:
                print("Player 1's time is up! Game over.")
                game_over_widget = GameOverWidget( self, self.gameLogic)
                game_over_widget.exec()  # Show the game over widget
                self.timer.stop()
        else:
            self.player2_time -= 1
            if self.player2_time <= 0:
                print("Player 2's time is up! Game over.")
                game_over_widget = GameOverWidget(self, self.gameLogic)
                game_over_widget.exec()  # Show the game over widget
                self.timer.stop()

        # Emit updated timer values
        self.updateTimerSignal.emit(self.player1_time, self.player2_time)
            
    def squareWidth(self):
        '''returns the integer width of one square in the board'''
        self.squareSize = int(min(self.width(), self.height()) / 10)
        return self.squareSize

    def squareHeight(self):
        '''returns the integer height of one square in the board'''
        self.squareSize = int(min(self.width(), self.height()) / 10)
        return self.squareSize


    def drawBoard(self, painter, size):
        '''Draws the board background, grid, and coordinates.'''
        # Calculate the square size and gap
        squareSize = int(min(self.width()/(size +1), self.height()/(size + 1))  )
        self.squareSize = squareSize

        boardSize = squareSize * (size - 1)  # Actual board covers (size - 1) squares
        boardGap = squareSize  # Use the square size as the boardGap
        gap = boardGap // 4

        letterSpacing = int(squareSize * 0.11)
        originX = boardGap
        originY = boardGap
        self.boardCoord = int(boardSize + squareSize * 3 / 2)
        
        # Set and extend the background rectangle to include one extra square size
        self.background = self.rect()
        self.background.setRect(
            int(gap),  # Starting X to include labels and one square size boardGap
            int(gap),  # Starting Y to include labels and one square size gap
            int(self.boardCoord),  # Width includes labels + 2 square sizes for the gap
            int(self.boardCoord),  # Height includes labels + 2 square sizes for the gap
        )
        # print("DrawBoard")
        # print(self.boardCoord)

        # Set and fill the background color for the extended area
        background_color = QColor(216, 180, 108)
        painter.fillRect(self.background, background_color)

        # Set font for labels (bold and larger size)
        font = painter.font()
        font.setBold(True)  # Make the font bold
        font.setPointSize(16)  # Increase the font size (adjust as needed)
        painter.setFont(font)

        # Set pen for label color (black)
        painter.setPen(QColor(0, 0, 0))  # Black pen for text
        # Set font for column labels (letters)
        font = painter.font()
        font.setPointSize(int(squareSize * 0.3))  # Adjust size for letters
        font.setBold(True)  # Optional: Make it bold
        painter.setFont(font)

        # Draw column labels (letters at the top)
        for col in range(size):  # Labels for the actual squares (0 to size - 2)
            x = originX - letterSpacing + col * squareSize  # Center the label
            y = int(originY - squareSize * 0.25)  # Place above the top grid line
            painter.drawText(QPoint(x, y), chr(65 + col))  # ASCII A=65

        # Draw row labels (numbers on the side)
        for row in range(size):  # Labels for the actual squares (0 to size - 1)
            x = originX - int(squareSize * 0.6)  # Place to the left of the left grid line
            y = originY + letterSpacing + row * squareSize  # Center the label
            painter.drawText(QPoint(x, y), str(size - row))  # Reverse the row numbering

        # Draw horizontal grid lines
        for row in range(size):  # size lines for size - 1 squares
            y = originY + row * squareSize
            start_point = QPoint(originX, y)
            end_point = QPoint(originX + boardSize, y)
            painter.drawLine(start_point, end_point)

        # Draw vertical grid lines
        for col in range(size):  # size lines for size - 1 squares
            x = originX + col * squareSize
            start_point = QPoint(x, originY)
            end_point = QPoint(x, originY + boardSize)
            painter.drawLine(start_point, end_point)

        # Create the GameControlWidget once the board is drawn
        if not self.gameControlWidget:  # Check if it's already created
            self.gameControlWidget = GameControlWidget(self, self.gameLogic, None, self.boardCoord)
            self.gameControlWidget.show()



    def drawPieces(self, painter):
        '''Draws the pieces on the board'''
        boardArray= self.gameLogic.boardArray
        self.radius = self.squareSize*0.4
        # print(self.radius)
        for row in range(len(boardArray)):
            for col in range(len(boardArray[row])):
                self.printBoardArray
                piece = boardArray[row][col]
                if piece != Piece.NoPiece:
                    # Calculate the center point at the intersection of grid lines
                    center = QPointF(
                        col * self.squareSize + self.squareSize,
                        row * self.squareSize + self.squareSize
                    )
                    # Determine the color of the piece
                    color = QColor(0, 0, 0) if piece.player == Piece.Black else QColor(255, 255, 255)
                    painter.setBrush(QBrush(color))
                    # Draw the circle centered on the intersection
                    painter.drawEllipse(center, float(self.radius), float(self.radius))

    def redo(self):
        """Handle the Redo action."""
        print("Redo action triggered")
        # Implement the redo logic here

    def pass_move(self):
        """Handle the Pass action."""
        print("Pass action triggered")
        # Implement the pass logic here

    def undo(self):
        # self.gameLogic = GameLogic(self)
        self.gameLogic.undo()
        self.update()
        self.gameControlWidget.update_current_label(self.current_player)


class GoBoardSizeSelector(QWidget):
    sizeSelected = pyqtSignal(int)  # Signal to emit the selected size

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Select Go Board Size")
        self.setGeometry(100, 100, 300, 200)
        self.center()
        # self.show()

        # Main layout
        self.layout = QVBoxLayout()

        # Label
        self.label = QLabel("Select the board size for the game of Go:")
        self.layout.addWidget(self.label)

        # Radio buttons
        self.radio_9x9 = QRadioButton("9x9")
        self.radio_13x13 = QRadioButton("13x13")
        self.radio_19x19 = QRadioButton("19x19")
        self.radio_9x9.setChecked(True)  # Default selection

        # Add radio buttons to layout
        self.layout.addWidget(self.radio_9x9)
        self.layout.addWidget(self.radio_13x13)
        self.layout.addWidget(self.radio_19x19)

        # Confirm button
        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.layout.addWidget(self.confirm_button)

        # Set layout
        self.setLayout(self.layout)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)



    def center(self):
        '''Centers the window on the screen'''
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 6
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

        
    def confirm_selection(self):
        '''Emit the selected size and close the selector'''
        if self.radio_9x9.isChecked():
            self.size = 9
            GameLogic.size = 9

        elif self.radio_13x13.isChecked():
            self.size = 13
            GameLogic.size = 13

        elif self.radio_19x19.isChecked():
            self.size = 19
            GameLogic.size = 19

        else:
            self.size = 9  # Default to 9x9 if no selection is made

        self.sizeSelected.emit(self.size)  # Emit the selected size
        self.close()  # Close the selector

class GameControlWidget(QWidget):
    def __init__(self,board, gameLogic, parent=None, boardCoord=0):
        super().__init__(parent)
        self.gameLogic = gameLogic
        self.board = board
        self.boardCoord = boardCoord
        self.setStyleSheet("background-color: #cccccc;")
        self.setMinimumWidth(boardCoord+200)
        self.setWindowTitle("Controls")
        self.center
        # Create layout for the widget
        layout = QVBoxLayout(self)
        # layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)




        self.currentPlayerWidget = QPushButton()  # Add a label to the button
        self.currentPlayerWidget.setFixedSize(100, 34)  # Set fixed size for Undo button
        self.currentPlayerWidget.setIconSize(QSize(28, 28))
        self.currentPlayerWidget.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: white;
                    border: 2px solid black;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
        self.currentPlayerWidget.setText("Black's Turn")



        # Optional: Adjust text position relative to icon (icon on the left, text on the right)
        self.currentPlayerWidget.setStyleSheet("""
            QPushButton {
                text-align: left;  /* Align text to the left */
                padding-left: 10px;  /* Add some padding between icon and text */
                border: 2px solid black;
                border-radius: 5px;
                background-color: white;

                                  }
        """)

        layout.addWidget(self.currentPlayerWidget)



        # Timer display labels
        self.timer_label_player1 = QLabel("Player 1 Time: 10:00")
        self.blackPrisoners = QLabel("Black Prisoners: 0")
        self.timer_label_player2 = QLabel("Player 2 Time: 10:00")
        self.whitePrisoners = QLabel("White Prisoners: 0")

        layout.addWidget(self.timer_label_player1)
        layout.addWidget(self.blackPrisoners)
        layout.addWidget(self.timer_label_player2)
        layout.addWidget(self.whitePrisoners)

        
        # Set the left margin dynamically based on boardCoord
        # self.updateMargin()
        # Undo button
        undo_button = QPushButton("Undo")  # Add a label to the button
        undo_button.setIcon(QIcon("./icons/undo.png"))
        undo_button.setFixedSize(100, 34)  # Set fixed size for Undo button
        undo_button.setIconSize(QSize(28, 28))

        # Optional: Adjust text position relative to icon (icon on the left, text on the right)
        undo_button.setStyleSheet("""
            QPushButton {
                text-align: left;  /* Align text to the left */
                padding-left: 10px;  /* Add some padding between icon and text */
                background-color: lightgreen;
                border: 2px solid black;
                border-radius: 5px;
                background-color: lightSkyBlue;

                                  }
        """)

        layout.addWidget(undo_button)

        # Redo button
        redo_button = QPushButton("Redo")
        redo_button.setIcon(QIcon("./icons/redo.png"))
        redo_button.setFixedSize(100, 34)  # Set fixed size for Redo button
        redo_button.setIconSize(QSize(28, 28))
        layout.addWidget(redo_button)


        # Optional: Adjust text position relative to icon (icon on the left, text on the right)
        redo_button.setStyleSheet("""
            QPushButton {
                text-align: left;  /* Align text to the left */
                padding-left: 10px;  /* Add some padding between icon and text */
                background-color: lightgreen;
                border: 2px solid black;
                border-radius: 5px;
                 background-color: lightSkyBlue;

            }
        """)
        # Pass button
        pass_button = QPushButton("Pass")
        pass_button.setIcon(QIcon("./icons/pass.png"))
        pass_button.setFixedSize(100, 34)  # Set fixed size for Pass button
        pass_button.setIconSize(QSize(28, 28))
        layout.addWidget(pass_button)

        pass_button.setStyleSheet("""
            QPushButton {
                text-align: left;  /* Align text to the left */
                padding-left: 10px;  /* Add some padding between icon and text */
                background-color: lightgreen;
                border: 2px solid black;
                border-radius: 5px;
                 background-color: lightSkyBlue;

                                  }
        """)
        # Reset button
        reset_button = QPushButton("Reset")
        reset_button.setFixedSize(100, 34)  # Set fixed size for Pass button
        reset_button.setIconSize(QSize(28, 28))
        layout.addWidget(reset_button)

        reset_button.setStyleSheet("""
            QPushButton {
                text-align: left;  /* Align text to the left */
                padding-left: 10px;  /* Add some padding between icon and text */
                background-color: lightgreen;
                border: 2px solid black;
                border-radius: 5px;
                 background-color: lightSkyBlue;

                                  }
        """)
        # Connect buttons to corresponding functions
        undo_button.clicked.connect(self.board.undo)
        redo_button.clicked.connect(Board.redo)
        pass_button.clicked.connect(self.gameLogic.passTurn)
        reset_button.clicked.connect(self.board.reset)


        # board = Board()
        board.updateTimerSignal.connect(self.update_timer_display)

    def center(self):
        '''Centers the window on the right side of the screen'''
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        # Set the x-coordinate to place the window on the right side
        x = screen.width() - size.width() - 10  # 10 is the margin from the right edge
        y = (screen.height() - size.height()) // 2  # Keep the y-coordinate centered vertically
        self.move(x, y)

    def update_current_label(self, current_player):
        """Update the button to indicate the current player's turn."""
        if current_player == 1:
            # Black's turn
            self.currentPlayerWidget.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: white;
                    border: 2px solid black;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            self.currentPlayerWidget.setText("Black's Turn")
        elif current_player == 2:
            # White's turn
            self.currentPlayerWidget.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 2px solid black;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            self.currentPlayerWidget.setText("White's Turn")

        self.currentPlayerWidget.update()




    def update_timer_display(self, player1_time, player2_time):
        """Update the timer display for both players."""
        player1_minutes, player1_seconds = divmod(player1_time, 60)
        player2_minutes, player2_seconds = divmod(player2_time, 60)

        blackPrisonersNum = self.gameLogic.blackPrisoners
        whitePrisonersNum = self.gameLogic.whitePrisoners

        self.timer_label_player1.setText(f"Player 1 Time: {player1_minutes:02}:{player1_seconds:02}")
        self.blackPrisoners.setText(f"Black Prisoners: {blackPrisonersNum}")
        self.timer_label_player2.setText(f"Player 2 Time: {player2_minutes:02}:{player2_seconds:02}")
        self.whitePrisoners.setText(f"White Prisoners: {whitePrisonersNum}")
        if self.gameLogic.isFinished:
            game_over_widget = GameOverWidget(self.board, self.gameLogic)
            game_over_widget.exec()  # Show the game over widget
            self.gameLogic.isFinished = False

        # print(self.gameLogic.isFinished)
    def updateMargin(self):
        """Update the left margin based on boardCoord"""
        layout = self.layout()
        # print(self.boardCoord)
        layout.setContentsMargins(self.boardCoord, 0, 0, 0)


class GameOverWidget(QDialog):
    def __init__(self,board, gameLogic,parent=None):
        super().__init__(parent)
        self.gameLogic = gameLogic
        self.board = board
        self.setWindowTitle("Game Over")
        self.setGeometry(100, 100, 300, 200)

        # Main layout
        self.layout = QVBoxLayout()

        # Congratulations label with modified font
        self.label = QLabel("Congratulations! Game Over.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set bold and bigger font for "Congratulations!" text
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        self.label.setFont(font)
        
        self.layout.addWidget(self.label)

        self.gameLogic.CalculateScores()
        player1_score = gameLogic.blackScore
        player2_score = gameLogic.whiteScore

        self.score_label_player1 = QLabel(f"Black score: {player1_score}")
        self.score_label_player2 = QLabel(f"White score: {player2_score}")
        self.draw_label = QLabel("Draw")
        
        if player1_score > player2_score:
            self.score_label_player1.setText(f"Black score: {player1_score}")
            self.layout.addWidget(self.score_label_player1)
        elif player2_score > player1_score:
            self.score_label_player2.setText(f"White score: {player2_score}")
            self.layout.addWidget(self.score_label_player2)
        else:
            self.draw_label.setText(f"Draw")
            self.layout.addWidget(self.draw_label)

        # Restart button
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.resetGameOver)
        self.layout.addWidget(self.restart_button)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Center the widget on the screen
        self.center_window()

    def center_window(self):
        """Center the window on the screen."""
        # screen = QDesktopWidget().screenGeometry()  # Get the screen size
        window_size = self.geometry()  # Get the current widget size
        x = (self.width() - window_size.width()) // 2  # Calculate the x position to center
        y = (self.height() - window_size.height()) // 2  # Calculate the y position to center
        self.move(x, y)  # Move the widget to the center of the screen

    def resetGameOver(self):
        self.board.reset()    
        self.close()  # Close the selector


