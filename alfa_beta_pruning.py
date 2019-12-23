import numpy as np

import time


class Game:
    def __init__(self):
        self.initialize_game()

    def initialize_game(self):
        self.size = 5
        self.score = 3
        self.current_state = np.full((self.size, self.size), '.')
        self.depth = 6

        # Player X always plays first
        self.player_turn = 'X'

    def draw_board(self):
        print("\n   | ", end="")
        for i in range(0, self.size):
            print('{} |'.format(i), end=" ")
        print('\n' + '-' * (self.size * 4 + 4))
        for i in range(0, self.size):
            print(' {} |'.format(i), end=" ")
            for j in range(0, self.size):
                s = self.current_state[i, j]
                if s == '.':
                    s = " "
                print('{} |'.format(s), end=" ")
            print('\n' + '-' * (self.size * 4 + 4))
        print()

    # Determines if the made move is a legal move
    def is_valid(self, px, py):
        if px < 0 or px >= self.size or py < 0 or py >= self.size:
            return False
        elif self.current_state[px, py] != '.':
            return False
        else:
            return True

    def is_end(self):
        # check line for 5 elements in a row
        def checkLine(line):
            count = 0
            player = '.'
            for j in range(len(line)):
                if line[j] != '.':
                    if line[j] == player:
                        count += 1
                    else:
                        #if j > self.size - self.score:
                        #   break
                        player = line[j]
                        count = 1
                    if count == self.score:
                        return player
                else:
                    count = 0
            return None

        # check rows
        for i in range(self.size):
            row = self.current_state[i, :]
            player = checkLine(row)
            if player != None:
                return player

        # check columns
        for j in range(self.size):
            column = self.current_state[:, j]
            player = checkLine(column)
            if player != None:
                return player

        for d in range(-self.size + self.score, self.size - self.score + 1):
            diagonal1 = self.current_state.diagonal(d)
            player = checkLine(diagonal1)
            if player != None:
                return player

            diagonal2 = np.fliplr(self.current_state).diagonal(d)
            player = checkLine(diagonal2)
            if player != None:
                return player

        for row in self.current_state:
            for el in row:
                if el == '.':
                    return None
        return '.'

    def freePos(self):
        pos = []
        for i in range(self.size):
            for j in range(self.size):
                if self.current_state[i, j] == '.':
                    pos = pos + [(i, j)]
        return pos

    # Player 'O' is max, in this case AI
    def max_alpha_beta(self, alpha, beta, depth):
        maxv = -2
        px = None
        py = None

        result = self.is_end()

        if result == 'X':
            return (-1, 0, 0)
        elif result == 'O':
            return (1, 0, 0)
        elif result == '.':
            return (0, 0, 0)

        if depth == 0:
            return (0, 0, 0)

        for pos in self.freePos():
            (i, j) = pos
            self.current_state[i, j] = 'O'
            (m, min_i, min_j) = self.min_alpha_beta(alpha, beta, depth - 1)
            #m = m / (self.depth - depth + 1)
            if depth == self.depth:
                print('Pos: {}, Score: {:.2f}'.format(pos, m))
            self.current_state[i, j] = '.'
            if m > maxv:
                maxv = m
                px = i
                py = j
            # Next two ifs in Max and Min are the only difference between regular algorithm and minimax
            if maxv >= beta:
                return (maxv, px, py)

            if maxv > alpha:
                alpha = maxv

        return (maxv, px, py)

    # Player 'X' is min, in this case Human
    def min_alpha_beta(self, alpha, beta, depth):

        minv = 2

        qx = None
        qy = None

        result = self.is_end()

        if result == 'X':
            return (-1, 0, 0)
        elif result == 'O':
            return (1, 0, 0)
        elif result == '.':
            return (0, 0, 0)

        if depth == 0:
            return (0, 0, 0)

        for pos in self.freePos():
            (i, j) = pos
            self.current_state[i, j] = 'X'
            (m, max_i, max_j) = self.max_alpha_beta(alpha, beta, depth - 1)
            #m = m / (self.depth - depth + 1)
            self.current_state[i, j] = '.'
            if m < minv:
                minv = m
                qx = i
                qy = j

            if minv <= alpha:
                return (minv, qx, qy)

            if minv < beta:
                beta = minv

        return (minv, qx, qy)

    def play_alpha_beta(self):
        while True:
            self.draw_board()
            self.result = self.is_end()

            if self.result != None:
                if self.result == 'X':
                    print('The winner is X!')
                elif self.result == 'O':
                    print('The winner is O!')
                elif self.result == '.':
                    print("It's a tie!")

                self.initialize_game()
                return

            if self.player_turn == 'X':

                #start = time.time()
                #(m, qx, qy) = self.min_alpha_beta(-2, 2, 0)
                #print('Evaluation time: {:.2f}s'.format(time.time() - start))
                #print('Recommended move: i = {}, j = {}, score = {}'.format(
                #    qx, qy, m))
                while True:
                    px = int(input('Insert the i coordinate: '))
                    py = int(input('Insert the j coordinate: '))

                    qx = px
                    qy = py

                    if self.is_valid(px, py):
                        self.current_state[px, py] = 'X'
                        self.player_turn = 'O'
                        break
                    else:
                        print('The move is not valid! Try again.')

            else:
                start_time = time.time()
                (m, px, py) = self.max_alpha_beta(-2, 2, self.depth)
                self.current_state[px, py] = 'O'
                self.player_turn = 'X'
                print('Move: i = {}, j = {}, score = {}'.format(px, py, m))
                print('Evaluation time: {:.2f}'.format(time.time() -
                                                       start_time))


def main():
    g = Game()
    #g.current_state[4, 4] = 'O'
    g.player_turn = 'O'
    g.play_alpha_beta()


if __name__ == "__main__":
    main()