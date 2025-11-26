# distutils: language=c
# cython: boundscheck=False, wraparound=False, nonecheck=False, cdivision=True

import numpy as np
cimport numpy as np
import random

# Helper to get available move indices from a board string
cdef list _get_available_moves_indices(str board_str):
    cdef list available_indices = []
    cdef int i
    for i in range(9):
        if board_str[i] == ' ':
            available_indices.append(i)
    return available_indices

# C-level struct to hold Q-table data for performance
ctypedef struct QTableEntry:
    double values[9]

# A simple dictionary-like structure for the Q-table at C-level
# This is a basic implementation. For massive state spaces, a proper hash map is better.
cdef class C_QTable:
    cdef public dict table

    def __cinit__(self):
        self.table = {}

    def __len__(self):
        return len(self.table)

    def get_table(self):
        return self.table
        
    def set_table(self, dict new_table):
        self.table = new_table

# We are moving the performance-critical parts of QLearningAgent here.
# The main QLearningAgent class will hold an instance of this fast agent.
cdef class FastQLearningAgent:
    cdef public C_QTable q_table
    cdef public double learning_rate
    cdef public double discount_factor
    cdef public double exploration_rate
    cdef public double initial_exploration_rate
    cdef public double min_exploration_rate
    cdef public double optimistic_initial_value
    cdef public str player
    
    def __cinit__(self, str player, double learning_rate, double discount_factor, double exploration_rate, double min_exploration_rate, double optimistic_initial_value=0.0, bint is_training=True):
        self.player = player
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate if is_training else 0.0
        self.initial_exploration_rate = exploration_rate if is_training else 0.0
        self.min_exploration_rate = min_exploration_rate
        self.optimistic_initial_value = optimistic_initial_value
        self.q_table = C_QTable()

    # The get_move logic remains in Python for now as it's less of a bottleneck
    # and interacts more with Python objects (the board).

    cpdef void update_q_table(self, str state, int action, double reward, str next_state, bint is_terminal):
        cdef np.ndarray values_array
        if state not in self.q_table.table:
            # Initialize Q-values for all moves as negative infinity, then set available moves to optimistic_initial_value
            values_array = np.full(9, -1e9, dtype=np.float64)
            for idx in _get_available_moves_indices(state):
                values_array[idx] = self.optimistic_initial_value
            self.q_table.table[state] = values_array
        values_array = self.q_table.table[state]
        cdef double current_q = values_array[action]
        cdef double max_next_q = 0.0
        cdef np.ndarray next_values_array # 関数の先頭に移動
        
        if not is_terminal:
            if next_state not in self.q_table.table:
                # Initialize Q-values for all moves as negative infinity, then set available moves to optimistic_initial_value
                next_values_array = np.full(9, -1e9, dtype=np.float64)
                for idx in _get_available_moves_indices(next_state):
                    next_values_array[idx] = self.optimistic_initial_value
                self.q_table.table[next_state] = next_values_array
            next_values_array = self.q_table.table[next_state]
            max_next_q = np.max(next_values_array)
            
        cdef double new_q = (1.0 - self.learning_rate) * current_q + self.learning_rate * (reward + self.discount_factor * max_next_q)
        values_array[action] = new_q

    cpdef void decay_exploration_rate(self, int episode, int total_episodes):
        cdef double decay_span = total_episodes * 0.75
        cdef double new_rate # 関数の先頭に移動
        if episode < decay_span:
            new_rate = self.initial_exploration_rate - (self.initial_exploration_rate - self.min_exploration_rate) * (episode / decay_span)
            if new_rate < self.min_exploration_rate:
                self.exploration_rate = self.min_exploration_rate
            else:
                self.exploration_rate = new_rate

# The train_episode function, now optimized.
# We pass Python objects (game, agents) but the inner logic can be faster.
def train_episode_fast(FastQLearningAgent q_agent, opponent):
    # This function will interact with Python objects, so it's a 'def' function.
    # The heavy lifting (update_q_table) is now a 'cdef' method.
    from game_logic import TicTacToe

    if q_agent.player == 'X':
        game = TicTacToe(agent_x=q_agent, agent_o=opponent)
    else:
        game = TicTacToe(agent_x=opponent, agent_o=q_agent)

    while not game.game_over:
        current_agent = game.get_current_agent()
        is_q_agent_turn = (current_agent is q_agent)

        if is_q_agent_turn:
            board_str = "".join(cell for row in game.board for cell in row)
            # get_move is still a Python method. We need to call it from Python space.
            move = get_move_py(q_agent, game.board) # Use the helper function directly
            if move is None: break
            action = move[0] * 3 + move[1]
            
            game.make_move(move[0], move[1])
            winner = game.check_winner()

            reward = 0
            if winner:
                if winner == q_agent.player: reward = 100
                elif winner == 'draw': reward = 75
                else: reward = -200
            
            next_board_str = "".join(cell for row in game.board for cell in row)
            q_agent.update_q_table(board_str, action, reward, next_board_str, bool(winner))

        else: # Opponent's turn
            move = opponent.get_move(game.board)
            if move is None: break
            game.make_move(move[0], move[1])
            winner = game.check_winner()
        
        if winner:
            break
        
        game.switch_player()

# Helper to expose get_move to Python
def get_move_py(FastQLearningAgent agent, list board):
    state = "".join(cell for row in board for cell in row)
    
    # Exploration
    if random.uniform(0, 1) < agent.exploration_rate:
        available_moves = []
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    available_moves.append((r, c))
        if not available_moves: return None
        return random.choice(available_moves)

    # Exploitation
    cdef np.ndarray q_values_array
    if state not in agent.q_table.table:
        # Initialize Q-values for all moves as negative infinity, then set available moves to optimistic_initial_value
        q_values_array = np.full(9, -1e9, dtype=np.float64)
        for idx in _get_available_moves_indices(state):
            q_values_array[idx] = agent.optimistic_initial_value
        agent.q_table.table[state] = q_values_array
    q_values_array = agent.q_table.table[state]

    cdef double max_q = -1e9 # A very small number
    
    # Find max_q for available moves
    best_moves = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == " ":
                idx = r * 3 + c
                if q_values_array[idx] > max_q:
                    max_q = q_values_array[idx]
                    best_moves = [(r, c)]
                elif q_values_array[idx] == max_q:
                    best_moves.append((r,c))
    
    if not best_moves: return None
    return random.choice(best_moves)