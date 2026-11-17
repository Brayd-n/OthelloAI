'''
Tkinter window for Othello.
Name: Braydon Callender
Date: 11/11/2026
'''
import tkinter as tk

from othello import (BLACK, WHITE, SIZE, new_board, legal_moves,
                     apply_move, count_discs, game_over, choose_move)

CELL = 60  # size of one square in pixels


def color_name(player):
    ''' return the word for a player'''
    if player == BLACK:
        return "Black"
    return "White"


class OthelloApp:
    ''' the game window. keeps track of the board and whose turn it is'''

    def __init__(self, root): # runs once the window is made
        self.root = root # keep it so other methods can use it
        root.title("Othello") # the text in the title bar of the window
        self.timer = None  # a computer move that is waiting, if there is one

        # the board is drawn on a canvas
        self.canvas = tk.Canvas(root, width=CELL * SIZE, height=CELL * SIZE, # 8 squares of 60 pixels each
                                highlightthickness=0) # no border around the canvas
        self.canvas.pack() # put the canvas in the window
        self.canvas.bind("<Button-1>", self.on_click) # left mouse click on the canvas calls the methon on click

        # text under the board for the turn, score and messages
        self.status = tk.Label(root, text="", font=("Arial", 13)) # a  text label for the status, empty for now
        self.status.pack(pady=5) # put it below the canvas with a little space above and below

        new_button = tk.Button(root, text="New game", command=self.new_game)
        new_button.pack(pady=5)

        # settings for the computer player, read again on every move
        self.computer_black = tk.BooleanVar(value=False)
        self.computer_white = tk.BooleanVar(value=False)
        self.use_ab = tk.BooleanVar(value=True)
        self.debug = tk.BooleanVar(value=False)
        self.depth = tk.IntVar(value=3)

        controls = tk.Frame(root)
        controls.pack(pady=5)

        black_box = tk.Checkbutton(controls, text="Computer plays Black",
                                   variable=self.computer_black,
                                   command=self.maybe_computer_turn)
        black_box.grid(row=0, column=0, sticky="w")

        white_box = tk.Checkbutton(controls, text="Computer plays White",
                                   variable=self.computer_white,
                                   command=self.maybe_computer_turn)
        white_box.grid(row=0, column=1, sticky="w")

        ab_box = tk.Checkbutton(controls, text="Alpha-beta pruning",
                                variable=self.use_ab)
        ab_box.grid(row=1, column=0, sticky="w")

        debug_box = tk.Checkbutton(controls, text="Debug output (in terminal)",
                                   variable=self.debug)
        debug_box.grid(row=1, column=1, sticky="w")

        depth_label = tk.Label(controls, text="Search depth:")
        depth_label.grid(row=2, column=0, sticky="e")

        depth_box = tk.Spinbox(controls, from_=1, to=8, width=4,
                               textvariable=self.depth, state="readonly")
        depth_box.grid(row=2, column=1, sticky="w")

        move_button = tk.Button(controls, text="Computer move",
                                command=self.computer_move)
        move_button.grid(row=3, column=0, pady=4)

        self.info = tk.Label(controls, text="")
        self.info.grid(row=3, column=1)

        self.new_game()

    def new_game(self):
        ''' reset everything for a new game. black goes first'''
        # cancel a waiting computer move from the old game
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.board = new_board()
        self.player = BLACK
        self.finished = False
        self.note = ""
        self.info.config(text="")
        self.draw()
        self.maybe_computer_turn()

    def draw(self):
        ''' draw the board, the dots for legal moves, and the status text'''
        self.canvas.delete("all")
        if self.finished:
            hints = []
        else:
            hints = legal_moves(self.board, self.player)
        for row in range(SIZE):
            for col in range(SIZE):
                x1 = col * CELL
                y1 = row * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL
                # the green square
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill="#2e7d32", outline="black")
                piece = self.board[row][col]
                if piece == BLACK:
                    self.canvas.create_oval(x1 + 6, y1 + 6, x2 - 6, y2 - 6,
                                            fill="black", outline="gray")
                elif piece == WHITE:
                    self.canvas.create_oval(x1 + 6, y1 + 6, x2 - 6, y2 - 6,
                                            fill="white", outline="gray")
                elif (row, col) in hints:
                    # a small dot on squares where the player can move
                    self.canvas.create_oval(x1 + 25, y1 + 25, x2 - 25, y2 - 25,
                                            fill="#a5d6a7", outline="")
        self.update_status()

    def update_status(self):
        ''' show the score and whose turn it is, or the final result'''
        black, white = count_discs(self.board)
        score = "Black " + str(black) + "  White " + str(white)
        if self.finished:
            if black > white:
                result = "Black wins!"
            elif white > black:
                result = "White wins!"
            else:
                result = "It's a tie."
            text = "Game over. " + score + ". " + result
        else:
            text = color_name(self.player) + "'s turn.   " + score
        # a pass message goes on its own line above
        if self.note != "":
            text = self.note + "\n" + text
        self.status.config(text=text)

    def on_click(self, event):
        ''' turn a mouse click into a square and play it if it is legal'''
        # ignore clicks after the game ends or on the computer's turn
        if self.finished or self.is_computer(self.player):
            return
        row = event.y // CELL
        col = event.x // CELL
        moves = legal_moves(self.board, self.player)
        if (row, col) not in moves:
            return
        self.play(row, col)

    def play(self, row, col):
        ''' make the move for the current player, then switch turns'''
        self.board = apply_move(self.board, row, col, self.player)
        self.player = -self.player
        self.after_move()

    def after_move(self):
        ''' check for a pass or the end of the game, then redraw'''
        self.note = ""
        if game_over(self.board):
            self.finished = True
        elif len(legal_moves(self.board, self.player)) == 0:
            # this player has no move, so they pass
            self.note = color_name(self.player) + " has no moves and passes."
            self.player = -self.player
        self.draw()
        self.maybe_computer_turn()

    def is_computer(self, player):
        ''' true if the computer is set to play this color'''
        if player == BLACK:
            return self.computer_black.get()
        return self.computer_white.get()

    def maybe_computer_turn(self):
        ''' if it is a computer color's turn, schedule its move'''
        if self.finished or self.timer is not None:
            return
        if self.is_computer(self.player):
            # wait 300 milliseconds so the board is drawn first
            self.timer = self.root.after(300, self.run_timer)

    def run_timer(self):
        ''' called when the timer goes off, makes the computer's move'''
        self.timer = None
        if not self.finished and self.is_computer(self.player):
            self.play_computer()

    def computer_move(self):
        ''' the Computer move button, plays for whoever's turn it is'''
        if self.finished or self.timer is not None:
            return
        self.play_computer()

    def play_computer(self):
        ''' search for the best move for the current player and play it'''
        self.info.config(text="Thinking...")
        self.root.update_idletasks()
        result = choose_move(self.board, self.player, self.depth.get(),
                             use_ab=self.use_ab.get(),
                             debug=self.debug.get())
        move = result[0]
        nodes = result[2]
        self.info.config(text=color_name(self.player) + " chose " + str(move) +
                         "\nStates examined: " + str(nodes))
        self.play(move[0], move[1])


if __name__ == "__main__":
    root = tk.Tk()
    OthelloApp(root)
    root.mainloop()