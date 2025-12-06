from server.game_manager import GameManager
import logging

class GameAdapter:
    """
    Adapts the GameManager for use with the BLE Tic-Tac-Toe client (micro:bit).
    Handles string-based protocol conversion.
    """
    def __init__(self, default_ai_agent="Random"):
        self.game_manager = GameManager()
        self.game_instance = None
        self.default_ai_agent = default_ai_agent
        self.logger = logging.getLogger(__name__)

    def start_game(self, player_x_type="Human", player_o_type="Random", human_symbol="X"):
        """
        Starts a new game.
        """
        self.logger.info(f"Starting game: X={player_x_type}, O={player_o_type}, Human={human_symbol}")
        self.game_instance = self.game_manager.start_new_game(
            player_x_type=player_x_type,
            player_o_type=player_o_type,
            human_player_symbol=human_symbol
        )
        return self.get_board_string()

    def handle_command(self, command: str) -> tuple[str, str]:
        """
        Process a command from the micro:bit.
        Returns: (board_string, result_status)
        """
        command = command.strip()
        self.logger.info(f"Received command: {command}")

        # Reset / Start Game Commands
        if command == "RESET":
             # We want to go back to the menu.
            return "RESET", ""

        if command == "START_P1":
            # Human is First (X), AI is Second (O, default_ai_agent)
            return self.start_game(player_x_type="Human", player_o_type=self.default_ai_agent, human_symbol="X"), ""

        if command == "START_P2":
            # Human is Second (O), AI is First (X, default_ai_agent)
            return self.start_game(player_x_type=self.default_ai_agent, player_o_type="Human", human_symbol="O"), ""

        if command.startswith("MOVE:"):
            try:
                index = int(command.split(":")[1])
                row = index // 3
                col = index % 3
                return self.make_move(row, col)
            except (ValueError, IndexError):
                self.logger.error(f"Invalid move command: {command}")
                return self.get_board_string(), ""

        # Unknown command
        return self.get_board_string(), ""

    def make_move(self, row: int, col: int) -> tuple[str, str]:
        """
        Executes a move for the human player.
        """
        if not self.game_instance or self.game_instance.game_over:
             return self.get_board_string(), self.get_game_result()

        # Human Move
        try:
            self.game_instance = self.game_manager.make_player_move(row, col)
        except Exception as e:
            self.logger.warning(f"Move failed: {e}")
            # Return current state without change if move is invalid
            return self.get_board_string(), self.get_game_result()

        # Check game state
        result = self.get_game_result()
        return self.get_board_string(), result

    def get_board_string(self) -> str:
        """
        Converts the board state to a 9-char string.
        X -> 'X'
        O -> 'O'
        Empty -> '.'
        """
        if not self.game_instance:
            return "........."

        board_str = ""
        for row in self.game_instance.board:
            for cell in row:
                if cell == "X":
                    board_str += "X"
                elif cell == "O":
                    board_str += "O"
                else:
                    board_str += "."
        return board_str

    def get_game_result(self) -> str:
        """
        Returns 'WIN:a,b,c', 'LOSE:a,b,c', 'DRAW', or '' if ongoing.
        """
        if not self.game_instance or not self.game_instance.game_over:
            return ""

        winner = self.game_instance.check_winner()
        human_symbol = self.game_instance.human_player

        # Get winner line indices if exist
        line_str = ""
        if self.game_instance.winner_line:
            indices = []
            for r, c in self.game_instance.winner_line:
                indices.append(str(r * 3 + c))
            line_str = ":" + ",".join(indices)

        if winner == "draw":
            return "DRAW"
        elif winner == human_symbol:
            return f"WIN{line_str}"
        elif winner is not None:
             # Opponent won
            return f"LOSE{line_str}"

        return ""
