from typing import Optional
from fastapi import HTTPException
from game_logic import TicTacToe
from agent_discovery import get_agent_details, AGENT_ALIASES

PLAYER_X = "X"
PLAYER_O = "O"
DB_PATH = "tictactoe.db"
Q_TABLE_PATH = "q_table.json"
PERFECT_MOVES_FILE = "perfect_moves.json"


class GameManager:
    """Manages the game state and agent interactions."""

    def __init__(self):
        self.game: Optional[TicTacToe] = None

        # 共通モジュールからエージェント詳細を取得
        self.agent_display_names, self.AGENT_CLASSES = get_agent_details()

        # Human エージェントを手動で追加
        self.AGENT_CLASSES["Human"] = None
        self.agent_display_names.insert(0, "Human")

    def get_available_agents(self):
        """
        利用可能な agent のリストを返す

        Returns:
            list: agent 名のリスト
        """
        return self.agent_display_names

    def _create_agent(self, agent_type: str, player_symbol: str):
        # エイリアスがあれば解決する (例: "Random" -> "ランダム")
        if agent_type in AGENT_ALIASES:  # pragma: no cover
            agent_type = AGENT_ALIASES[agent_type]

        agent_class = self.AGENT_CLASSES.get(agent_type)

        if agent_class is None:  # Humanの場合
            return None

        if agent_type == "Perfect":
            return agent_class(player_symbol, PERFECT_MOVES_FILE)

        elif agent_type == "QLearning":
            try:
                return agent_class(player_symbol, q_table_file=Q_TABLE_PATH)
            except FileNotFoundError:
                raise HTTPException(  # pragma: no cover
                    status_code=500,
                    detail=f"Q-learning table not found at {Q_TABLE_PATH}. Please train the Q-learning agent first.",
                )
        else:
            return agent_class(player_symbol)

    def _check_winner(self, board):
        """Stateless winner check, returns (winner, winner_line)."""
        # Use the static method from TicTacToe class
        return TicTacToe._check_winner_logic(board)

    def _make_agent_move_if_needed(self):
        if self.game is None:
            return
        while not self.game.game_over and self.game.get_current_agent() is not None:
            self.game = self.run_ai_move(self.game)

    def create_game_instance(self, player_x_type: str, player_o_type: str, human_player_symbol: Optional[str] = None) -> TicTacToe:
        """Statelessly creates a new game instance."""
        agent_x = self._create_agent(player_x_type, PLAYER_X)
        agent_o = self._create_agent(player_o_type, PLAYER_O)
        game = TicTacToe(agent_x=agent_x, agent_o=agent_o, human_player=human_player_symbol)
        return game

    def start_new_game(
        self,
        player_x_type: str,
        player_o_type: str,
        human_player_symbol: Optional[str] = None,
    ) -> TicTacToe:
        """Starts a new game and stores it in the instance (stateful)."""
        self.game = self.create_game_instance(player_x_type, player_o_type, human_player_symbol)
        # 最初のプレイヤーがエージェントの場合、手を打たせる
        self._make_agent_move_if_needed()
        return self.game

    def get_current_game_state(self):
        if self.game is None:
            raise HTTPException(status_code=404, detail="Game not started")
        return {
            "board": self.game.board,
            "current_player": self.game.current_player,
            "winner": self.game.check_winner(),
            "winner_line": self.game.winner_line,
            "game_over": self.game.game_over,
        }

    def execute_move(self, game: TicTacToe, row: int, col: int) -> TicTacToe:
        """Statelessly executes a move on a given game instance."""
        if not game.make_move(row, col):
            raise ValueError("Invalid move")  # pragma: no cover
        game.check_winner()
        if not game.game_over:
            game.switch_player()
        return game

    def run_ai_move(self, game: TicTacToe) -> TicTacToe:
        """Statelessly runs an AI move on a given game instance."""
        if game.game_over or game.get_current_agent() is None:
            return game
        
        agent = game.get_current_agent()
        try:
            move = agent.get_move([row[:] for row in game.board])
        except (KeyError, IndexError):
             # Agent might indicate game over, so we re-check winner
            game.check_winner()
            return game

        if move:
            row, col = move
            # The agent's move is executed.
            game = self.execute_move(game, row, col)
        else: # No move from AI, probably a draw
            game.check_winner() # Update winner status
        return game

    def make_player_move(self, row: int, col: int) -> TicTacToe:
        """Makes a human player move in the stored game (stateful)."""
        if self.game is None:
            raise HTTPException(status_code=404, detail="Game not started")

        current_agent = self.game.get_current_agent()
        if current_agent is not None:
            # Allow move even if it's AI's turn, for simplicity. Client should prevent this.
            pass

        try:
            self.game = self.execute_move(self.game, row, col)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid move")

        # After human move, let AI move if it's their turn.
        self._make_agent_move_if_needed()
        return self.game