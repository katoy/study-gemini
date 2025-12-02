from typing import Optional
from fastapi import HTTPException
from game_logic import TicTacToe
from agent_discovery import get_agent_details

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
        agent_class = self.AGENT_CLASSES.get(agent_type)

        if agent_class is None:  # Humanの場合
            return None

        if agent_type == "Perfect":
            return agent_class(player_symbol, PERFECT_MOVES_FILE)

        elif agent_type == "QLearning":
            try:
                return agent_class(player_symbol, q_table_file=Q_TABLE_PATH)
            except FileNotFoundError:
                raise HTTPException(
                    status_code=500,
                    detail=f"Q-learning table not found at {Q_TABLE_PATH}. Please train the Q-learning agent first.",
                )
        else:
            return agent_class(player_symbol)

    def _make_agent_move_if_needed(self):
        if self.game is None:
            return
        while not self.game.game_over and self.game.get_current_agent() is not None:
            agent = self.game.get_current_agent()
            try:
                move = agent.get_move([row[:] for row in self.game.board])
            except KeyError:
                # PerfectAgent raises KeyError when game is over or no perfect move found
                self.game.check_winner()  # Ensure game.game_over is updated
                break  # Break loop, as agent says game is over
            if move is None:
                # If agent returns None, it implies no valid moves are available (e.g., board full/draw)
                # Update game_over state based on current board.
                self.game.check_winner()  # This will update game.game_over and game.winner
                break
            row, col = move
            if self.game.make_move(row, col):
                # After a move, check if the game is over (win or draw)
                self.game.check_winner()  # Update game.game_over and game.winner immediately
                if not self.game.game_over:  # Only switch player if game is not over
                    self.game.switch_player()
            else:
                self.game.check_winner()  # Ensure game_over is updated even on an invalid move attempt
                break  # Break out to avoid infinite loop on invalid moves

    def start_new_game(
        self,
        player_x_type: str,
        player_o_type: str,
        human_player_symbol: Optional[str] = None,
    ):
        agent_x = self._create_agent(player_x_type, PLAYER_X)
        agent_o = self._create_agent(player_o_type, PLAYER_O)

        self.game = TicTacToe(
            agent_x=agent_x, agent_o=agent_o, human_player=human_player_symbol
        )

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

    def make_player_move(self, row: int, col: int):
        if self.game is None:
            raise HTTPException(status_code=404, detail="Game not started")

        # 人間プレイヤーのターンであることを確認
        current_agent = self.game.get_current_agent()
        if current_agent is not None:
            # 現在のプレイヤーがエージェントの場合、このエンドポイントは呼ばれるべきではない
            # ただし、二重の安全策として、ここではエラーとしないが、クライアント側で制御すべき
            pass  # エージェントのターンは_make_agent_move_if_neededで処理されるため、ここでは無視

        if not self.game.make_move(row, col):
            raise HTTPException(status_code=400, detail="Invalid move")

        winner = self.game.check_winner()
        if winner is None:
            self.game.switch_player()
            # 人間が手を打った後、次のプレイヤーがエージェントであれば、エージェントのターンを処理
            self._make_agent_move_if_needed()  # ここでエージェントのターンを処理
        return self.game
