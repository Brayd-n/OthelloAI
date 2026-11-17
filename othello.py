"""
Othello with minimax AI playing
name: Braydon Callender
date: 11/11/2026
"""
#what is stored in each square of the board
EMPTY =  0 # no disc in the square
BLACK = 1 # a black disk
WHITE = -1 # a white disk, i use -1 because whot is "the opponent" so negative of the player

SIZE = 8 # the board is 8x8

#the directions that you can choose from any square ( row , col)
DIRECTIONS = [(-1,-1), (-1,0), (-1,1), # up left, up, up right
               (0,-1),         (0,1),  # left, right
               (1,-1), (1,0), (1,1)]   # down left, down, down right


# now lets set up how much each square is worth to the player
# row 0 is the top row, col 0 is  the left side

WEIGHTS = [
    [100, -20, 10,  5,  5, 10, -20, 100],   # top edge: a corner is worth 100
    [-20, -50, -2, -2, -2, -2, -50, -20],   # the -50s touch a corner diagonally: bad, they give the corner away
    [ 10,  -2, -1, -1, -1, -1,  -2,  10],   # the 10s are safe edge squares
    [  5,  -2, -1, -1, -1, -1,  -2,   5],   # plain edge squares are a little good
    [  5,  -2, -1, -1, -1, -1,  -2,   5],   # the middle squares are close to worthless
    [ 10,  -2, -1, -1, -1, -1,  -2,  10],   # the table is the same upside down...
    [-20, -50, -2, -2, -2, -2, -50, -20],   # ...and left to right
    [100, -20, 10,  5,  5, 10, -20, 100],   # bottom edge, same as the top
]



def new_board():
    ''' return a fresh 8x8 board set up for the start of a new game'''
    board = [] # start with an empty board
    for row in range(SIZE): # make 8 rows
        new_row = [] # a new row starts empty
        for col in range(SIZE): # 8 suquares in each row
            new_row.append(EMPTY) #every square starts empty
        board.append(new_row) # add the finished row to the board

    # set up the initial four squares with their respective colors
    board[3][3] = WHITE
    board[4][4] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK

    return board

def print_board(board):
    ''' print the board ot the screen'''
    print("  ", end="") #
    for col in range(SIZE):
        print(col, end=" ")
    print()
    for row in range(SIZE):# one line per row
        print(row, end=" ")  # the row nummber at the start
        for col in range(SIZE): # go across the row
            square = board[row][col] # what is on this square
            if square == EMPTY:
                print(".", end=" ") #empty
            elif square == BLACK:
                print("B", end=" ") # blakc
            else:
                print("W", end=" ") # white
        print() # new line after each row


def on_board(row, col):
    ''' check if a row and col are inside the board'''
    if row< 0 or row >= SIZE: # abovie the top or below the bottom
        return False
    if col < 0 or col >= SIZE: # off the left or right side
        return False
    return True # if it passed both of our rigirous tests it is on the board


def flips_for_move(board, row, col, player):
    ''' return a list of discs that would flip if a player puts a disc at row, col. an empty list means the move is not legal'''
    if board[row][col] != EMPTY:  # a square that already has a disc is not a legal move
        return []
    opponent = -player # the other players number
    flips = [] # will hold every disc that flips from all directions

    # look in each of the 8 directions
    for direction in DIRECTIONS:
        row_step = direction[0] # hpow much the row changes each step
        col_step = direction[1] # how mych the column changes each step
        line = [] # opponent discs we pass over
        check_row = row + row_step # te first square next tot the move square
        check_col = col + col_step

        # keep walking while we see the opponent's discs
        while on_board(check_row, check_col) and board[check_row][check_col] == opponent:
            line.append((check_row, check_col)) # remember this disc, it flips if the run is closed
            check_row += row_step # take another step in the same direction
            check_col += col_step

        # the run only counts if it ends on one of our own discs
        if len(line) > 0 and on_board(check_row, check_col) and board[check_row][check_col] == player:
            for disc in line: # the discs are sandwhiched, so all of them flip
                flips.append(disc)

    return flips # empty means nothing flips, so the move would be illegal


def legal_moves(board, player):
    ''' return a list of every (row, col) where player can move'''
    moves = [] # the legal squares found so far
    for row in range(SIZE): # check every row
        for col in range(SIZE): # and every column
            flips = flips_for_move(board, row, col, player) # what would flip here?
            if len(flips) > 0: # if something flips
                moves.append((row, col)) # this square is a legal move
    return moves


def copy_board(board):
    ''' make a separate copy of the board'''
    copy = [] # start blank
    for row in range(SIZE):
        new_row = [] # brand new row for the copy
        for col in range(SIZE):
            new_row.append(board[row][col]) # copy each square over
        copy.append(new_row)
    return copy # return that copy so that changing it will not alter the original board


def apply_move(board, row, col, player):
    ''' return a NEW board with the move made, the old board is not changed'''
    after = copy_board(board) # work on a copy
    flips = flips_for_move(board, row, col, player) # the discs this move flips
    for disc in flips:
        after[disc[0]][disc[1]] = player # turn each flipped disc to the player's color
    after[row][col] = player # place the new disc
    return after # this does not check that the move is legal


def count_discs(board):
    ''' count the discs, returns the black count and the white count'''
    black = 0  # black starts at 0
    white = 0 # white starts at 0
    for row in range(SIZE):
        for col in range(SIZE): # look at all 64 squares
            if board[row][col] == BLACK:
                black += 1 # one more black disc
            elif board[row][col] == WHITE:
                white += 1 # one more white disc
    return black, white # returns two numbers: black, white


def game_over(board):
    ''' the game is over when neither player can move'''
    black_moves = legal_moves(board, BLACK)# blacks moves
    white_moves = legal_moves(board, WHITE) # whites moves
    if len(black_moves) == 0 and len(white_moves) == 0: # no one can move
        return True # gg
    return False


def evaluate(board):
    ''' score a board. positive is good for black, negative is good for white'''
    black_moves = len(legal_moves(board, BLACK)) # how many moves does black have
    white_moves = len(legal_moves(board, WHITE)) # how many moves does white have

    # if the game is over, the real result counts the most
    if black_moves == 0 and white_moves == 0:
        black, white = count_discs(board) # the final disc counts
        return 10000 * (black - white) # a huge number so a win or loss beats any normal score

    # add up the square values (black adds, white subtracts)
    position = 0 # running total
    for row in range(SIZE):
        for col in range(SIZE):
            position += WEIGHTS[row][col] * board[row][col]  # the board holds 1, -1, or 0, so black adds the weight, white subtracts it, emtpty adds nothing

    # having more moves than the opponent is good
    mobility = black_moves - white_moves #positive when black has more moves, negative when white has more

    return position + 5 * mobility # each extra move is worth 5 points, add that to the position score


def minimax(board, depth, player, alpha, beta, use_ab, stats, debug, path):
    ''' look depth moves ahead and return (value, best_move) for player.
    black wants the biggest score, white wants the smallest.
    alpha is the best score black is sure of, beta is the best for white.'''
    stats["nodes"] += 1 # one more board looked at

    # stop if we are out of depth or the game is over
    if depth == 0 or game_over(board): # this is the base case that ends recursion
        value = evaluate(board) # score the board
        if debug: # if debug is on
            print("  " + " ".join(path), "->", value) # print the path of moves that led to this board
        return value, None # there is no move to report

    moves = legal_moves(board, player) # every move this player can make
    if player == BLACK:
        name = "B" # letter used in debug
    else:
        name = "W"

    # no moves, so this player passes and the other player goes
    if len(moves) == 0:
        pass_path = path + [name + " pass"] # path + [] to make a new list | same board, other player, one less depth
        result = minimax(board, depth - 1, -player, alpha, beta, use_ab, stats, debug, pass_path)
        return result[0], None # result[0] is the value, None means that no move was made, just a pass

    best_move = None # best move found so far
    if player == BLACK:
        # black wants the biggest score
        best = float("-inf") # lower than any real score, so the first move will always be better
        for move in moves: # try ever legal move
            row = move[0]
            col = move[1]
            child = apply_move(board, row, col, player) # the board after this move is made
            move_text = name + "(" + str(row) + "," + str(col) + ")" # debugging text
            result = minimax(child, depth - 1, -player, alpha, beta, use_ab, stats, debug, path + [move_text]) # score that board with the other player to move and one less depth
            value = result[0] # minimax gives back (value, move) we obv want the value
            if value > best: # if better than anything so far
                best = value # remember the score
                best_move = move # and the move that got it there
            if use_ab: # if we are using alpha beta pruning
                alpha = max(alpha, best) # alpha is the best score black is sure of
                if alpha >= beta:
                    break  # white already has a better option, stop looking
    else:
        # white wants the smallest score
        best = float("inf") #higher than any real score, so first move will always be better
        for move in moves:
            row = move[0]
            col = move[1]
            child = apply_move(board, row, col, player)
            move_text = name + "(" + str(row) + "," + str(col) + ")"
            result = minimax(child, depth - 1, -player, alpha, beta, use_ab, stats, debug, path + [move_text])
            value = result[0]
            if value < best: # white likes ssmaller scores
                best = value
                best_move = move
            if use_ab:
                beta = min(beta, best) # beta is the best score white is sure of
                if alpha >= beta:
                    break  # black already has a better option, stop looking
    return best, best_move # return the value of the board and the move that gets it there


def choose_move(board, player, depth, use_ab=True, debug=False):
    ''' pick a move for player. returns the move, its score, and how many
    boards were looked at'''
    stats = {"nodes": 0}
    if debug:
        if use_ab:
            pruning = "on"
        else:
            pruning = "off"
        print("Searching depth " + str(depth) + ", pruning " + pruning)
    # start the search with the widest window: alpha is -infinity, beta is +infinity, no moves in the path yet
    result = minimax(board, depth, player, float("-inf"), float("inf"), use_ab, stats, debug, [])
    value = result[0] # the score
    move = result[1] # the move that gets it tot hat score
    if debug:
        print("Chosen move " + str(move) + ", value " + str(value) + ", states examined " + str(stats["nodes"]))
    return move, value, stats["nodes"]# the move, its score, and how many boards it looked at.


#testing
# if __name__ == "__main__":
