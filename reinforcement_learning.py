import numpy as np
import pickle

SIZE = 5
SCORE = 3


class State:
    def __init__(self, p1, p2):
        self.current_state = np.full((SIZE, SIZE), '.')
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 'X'

    # get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.current_state.reshape(SIZE**2))
        return self.boardHash

    def winner(self):
        # check line for 5 elements in a row
        def checkLine(line):
            count = 0
            player = '.'
            for j in range(len(line)):
                if line[j] != '.':
                    if line[j] == player:
                        count += 1
                    else:
                        #if j > SIZE - SCORE:
                        #   break
                        player = line[j]
                        count = 1
                    if count == SCORE:
                        return player
                else:
                    count = 0
            return None

        # check rows
        for i in range(SIZE):
            row = self.current_state[i, :]
            player = checkLine(row)
            if player != None:
                self.isEnd = True
                return player

        # check columns
        for j in range(SIZE):
            column = self.current_state[:, j]
            player = checkLine(column)
            if player != None:
                self.isEnd = True
                return player

        for d in range(-SIZE + SCORE, SIZE - SCORE + 1):
            diagonal1 = self.current_state.diagonal(d)
            player = checkLine(diagonal1)
            if player != None:
                self.isEnd = True
                return player

            diagonal2 = np.fliplr(self.current_state).diagonal(d)
            player = checkLine(diagonal2)
            if player != None:
                self.isEnd = True
                return player

        for row in self.current_state:
            for el in row:
                if el == '.':
                    self.isEnd = False
                    return None
        self.isEnd = True
        return '.'

    def availablePositions(self):
        pos = []
        for i in range(SIZE):
            for j in range(SIZE):
                if self.current_state[i, j] == '.':
                    pos = pos + [(i, j)]
        return pos

    def updateState(self, position):
        self.current_state[position] = self.playerSymbol
        # switch to another player
        self.playerSymbol = 'O' if self.playerSymbol == 'X' else 'X'

    # only when game ends
    def giveReward(self, result):
        #result = self.winner()
        # backpropagate reward
        if result == 'X':
            self.p1.feedReward(1)
            self.p2.feedReward(0)
        elif result == 'O':
            self.p1.feedReward(0)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.3)
            self.p2.feedReward(0.3)

    # board reset
    def reset(self):
        self.current_state = np.full((SIZE, SIZE), '.')
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 'X'

    def play(self, rounds=100):
        for i in range(rounds):
            if i % 1000 == 0:
                print("Rounds {}".format(i))
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.current_state,
                                                 self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end

                win = self.winner()
                if win is not None:
                    # self.showBoard()
                    # ended with p1 either win or draw
                    self.giveReward(win)
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions,
                                                     self.current_state,
                                                     self.playerSymbol)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward(win)
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break

    # play with human
    def play2(self, first=2):
        firstP1 = False
        P1symbol = 'O'
        P2symbol = 'X'
        if first == 1:
            firstP1 = True
            P1symbol = 'X'
            P2symbol = 'O'

        while not self.isEnd:
            if firstP1:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.current_state,
                                                 self.playerSymbol)
                # take action and upate board state
                self.updateState(p1_action)
            else:
                firstP1 = True
            self.showBoard()
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == P1symbol:
                    print(self.p1.name, "wins!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    if win == P2symbol:
                        print(self.p2.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break

    def showBoard(self):
        print("\n   | ", end="")
        for i in range(0, SIZE):
            print('{} |'.format(i), end=" ")
        print('\n' + '-' * (SIZE * 4 + 4))
        for i in range(0, SIZE):
            print(' {} |'.format(i), end=" ")
            for j in range(0, SIZE):
                s = self.current_state[i, j]
                if s == '.':
                    s = " "
                print('{} |'.format(s), end=" ")
            print('\n' + '-' * (SIZE * 4 + 4))
        print()


class Player:
    def __init__(self, name, exp_rate=0.3):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_value = {}  # state -> value

    def getHash(self, board):
        boardHash = str(board.reshape(SIZE**2))
        return boardHash

    def chooseAction(self, positions, current_board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions:
                next_board = current_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(
                    next_boardHash) is None else self.states_value.get(
                        next_boardHash)
                # print("value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        # print("{} takes action {}".format(self.name, action))
        return action

    # append a hash state
    def addState(self, state):
        self.states.append(state)

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.lr * (self.decay_gamma * reward -
                                                self.states_value[st])
            reward = self.states_value[st]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_value = pickle.load(fr)
        fr.close()


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
            row = int(input("Input your action row:"))
            col = int(input("Input your action col:"))
            action = (row, col)
            if action in positions:
                return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass


if __name__ == "__main__":

    if False:
        # training
        p1 = Player("p1")
        p2 = Player("p2")

        st = State(p1, p2)
        print("training...")
        st.play(10000)
        p1.savePolicy()
        p2.savePolicy()

    # play with human
    p1 = Player("computer", exp_rate=0)
    p1.loadPolicy("policy_p2")

    p2 = HumanPlayer("human")

    st = State(p1, p2)
    st.play2(first=2)
