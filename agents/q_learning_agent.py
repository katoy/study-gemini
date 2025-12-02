import json
import os
from agents.base_agent import BaseAgent
import fast_trainer  # Import the compiled Cython module
import numpy as np  # Add numpy import


class QLearningAgent(BaseAgent):
    """
    A wrapper for the optimized Cython Q-learning agent.
    This class handles the interface between the Python environment and the fast Cython module.
    """

    def __init__(
        self,
        player: str,
        learning_rate=0.1,
        discount_factor=0.9,
        exploration_rate=1.0,
        min_exploration_rate=0.05,
        optimistic_initial_value=0.0,
        q_table_file="q_table.json",
        is_training=True,
    ):
        super().__init__(player)
        self.q_table_file = q_table_file

        # Instantiate the fast agent from our Cython module
        self._fast_agent = fast_trainer.FastQLearningAgent(
            player,
            learning_rate,
            discount_factor,
            exploration_rate,
            min_exploration_rate,
            optimistic_initial_value,
            is_training,
        )
        self.load_q_table()

    @property
    def min_exploration_rate(self):
        return self._fast_agent.min_exploration_rate

    @min_exploration_rate.setter
    def min_exploration_rate(self, value):
        self._fast_agent.min_exploration_rate = value

    @property
    def exploration_rate(self):
        return self._fast_agent.exploration_rate

    @exploration_rate.setter
    def exploration_rate(self, value):
        self._fast_agent.exploration_rate = value

    @property
    def q_table(self):
        # Returns a copy of the q_table for external access
        return {
            state: self._fast_agent.q_table.table[state].tolist()
            for state in self._fast_agent.q_table.table
        }

    @q_table.setter
    def q_table(self, value: dict):
        # Expects a dict with lists and converts to ndarray for Cython
        converted_table = {
            state: np.array(q_values, dtype=np.float64)
            for state, q_values in value.items()
        }
        self._fast_agent.q_table.set_table(converted_table)

    def get_move(self, board: list) -> tuple[int, int] | None:
        """
        Uses the Cython-optimized get_move_py function.
        """
        return fast_trainer.get_move_py(self._fast_agent, board)

    def decay_exploration_rate(self, episode, total_episodes):
        """Delegates to the fast Cython method."""
        # The Cython method handles the decay.
        # Ensure the FastQLearningAgent's decay_exploration_rate is updated as well.
        self._fast_agent.decay_exploration_rate(episode, total_episodes)

    def update_q_table(self, state, action, reward, next_state, is_terminal=False):
        """Delegates to the fast Cython method."""
        self._fast_agent.update_q_table(state, action, reward, next_state, is_terminal)

    def save_q_table(self):
        """Saves the Q-table to a file."""
        with open(self.q_table_file, "w") as f:
            # self.q_table property already handles conversion to list
            json.dump(self.q_table, f)

    def load_q_table(self):
        """Loads the Q-table from a file."""
        if os.path.exists(self.q_table_file) and not os.getenv("PYTEST_CURRENT_TEST"):
            try:
                with open(self.q_table_file, "r") as f:
                    # json.load will return lists, which the q_table.setter handles
                    python_q_table = json.load(f)
                    self.q_table = python_q_table
            except (json.JSONDecodeError, IOError):
                print(
                    f"Warning: Could not read Q-table file '{self.q_table_file}'. Starting with an empty table."
                )
                self.q_table = {}
        else:
            self.q_table = {}
