import logging
from server.game_manager import GameManager
from game_logic import TicTacToe

class GameAdapter:
    """
    Adapts the GameManager for stateless use with the BLE Tic-Tac-Toe client (micro:bit).
    Handles string-based protocol conversion.

    A stateless protocol is defined for communication:

    Client -> Server:
    - START:<HUMAN_SYMBOL>
      - Description: Starts a new game.
      - HUMAN_SYMBOL: 'X' (Human goes first) or 'O' (AI goes first).
      - Example: "START:X"

    - MOVE:<MOVE_INDEX>:<HUMAN_SYMBOL>:<BOARD_STATE>
      - Description: Human makes a move.
      - MOVE_INDEX: 0-8 index of the move.
      - HUMAN_SYMBOL: The symbol ('X' or 'O') the human is playing.
      - BOARD_STATE: 9-char string representing the board (e.g., "X.O....").
      - Example: "MOVE:4:X:X.O...."

    - RESET
      - Description: Requests a board reset.

    Server -> Client:
    - <BOARD_STATE>:<GAME_RESULT>:<WIN_LINE>
      - Description: The response after a start or move.
      - BOARD_STATE: The updated 9-char board string.
      - GAME_RESULT: 'ONGOING', 'WIN', 'LOSE', or 'DRAW'.
      - WIN_LINE: Comma-separated indices of the winning line (e.g., "0,4,8"), or empty.
      - Example: "X.O.X..O.:WIN:0,4,8"
    """
    def __init__(self, default_ai_agent="Random"):
        # GameManager is used for its agent-loading and stateless logic capabilities.
        self.game_manager = GameManager()
        self.default_ai_agent = default_ai_agent
        self.logger = logging.getLogger(__name__)

    def handle_command(self, command: str) -> str:
        """
        Process a stateless command from the micro:bit.
        Returns: A single string response for the client.
        """
        command = command.strip()
        self.logger.info(f"Received command: {command}")
        parts = command.split(':')
        cmd = parts[0] if parts else ""

        try:
            if cmd == "START":
                human_symbol = parts[1]
                return self._start_game(human_symbol)

            if cmd == "MOVE":
                move_index = int(parts[1])
                human_symbol = parts[2]
                board_state_str = parts[3]
                
                # The logic of _make_move is now integrated here
                row, col = move_index // 3, move_index % 3

                # 1. Recreate game instance
                game_instance = self._recreate_game_from_str(board_state_str, human_symbol)
                if game_instance.game_over:
                    self.logger.warning("Move received for a finished game.")
                    return self._format_response(game_instance)

                # Force the current player to be the one specified by the client
                game_instance.current_player = human_symbol

                # 2. Execute human move
                try:
                    self.logger.info(f"Applying human move for '{human_symbol}' at ({row}, {col})")
                    game_instance = self.game_manager.execute_move(game_instance, row, col)
                except ValueError as e:
                    self.logger.warning(f"Invalid human move: {e}")
                    return self._format_response(game_instance)

                # 3. If game isn't over, let the AI move
                if not game_instance.game_over and game_instance.get_current_agent() is not None:
                    self.logger.info("Running AI move.")
                    game_instance = self.game_manager.run_ai_move(game_instance)

                # 4. Format response (2-step for game over)
                if game_instance.game_over:
                    # First response: Final board, but marked as "ONGOING"
                    ongoing_response = self._format_response(game_instance, force_ongoing=True)
                    
                    # Second response: The actual result message
                    result_str, line_str = self._get_game_result(game_instance)
                    result_response = f"RESULT:{result_str}:{line_str}"
                    
                    return ongoing_response, result_response
                else:
                    return self._format_response(game_instance)


            if cmd == "RESET":
                return ".........:ONGOING:"

        except (IndexError, ValueError) as e:
            self.logger.error(f"Invalid command format '{command}': {e}")
        except Exception as e:
            self.logger.error(f"Error processing command '{command}': {e}", exc_info=True)

        # Return a default safe state on error
        return ".........:ONGOING:"

    def _start_game(self, human_symbol: str) -> str:
        """Starts a new game, possibly with an initial AI move."""
        self.logger.info(f"Starting new game for human as '{human_symbol}'")
        player_x_type = "Human" if human_symbol == "X" else self.default_ai_agent
        player_o_type = "Human" if human_symbol == "O" else self.default_ai_agent

        game_instance = self.game_manager.create_game_instance(
            player_x_type, player_o_type, human_symbol
        )

        # If AI is 'X' (the first player), it moves immediately.
        if game_instance.get_current_agent() is not None:
            self.logger.info("AI is starting first.")
            game_instance = self.game_manager.run_ai_move(game_instance)

        return self._format_response(game_instance)

    def _recreate_game_from_str(self, board_state_str: str, human_symbol: str) -> TicTacToe:
        """Creates a TicTacToe instance from a board string and human player symbol."""
        player_x_type = "Human" if human_symbol == "X" else self.default_ai_agent
        player_o_type = "Human" if human_symbol == "O" else self.default_ai_agent
        
        game_instance = self.game_manager.create_game_instance(
            player_x_type=player_x_type,
            player_o_type=player_o_type,
            human_player_symbol=human_symbol
        )

        # Reconstruct board state
        board = [list(board_state_str[i:i+3]) for i in range(0, 9, 3)]
        for r in range(3):
            for c in range(3):
                board[r][c] = board[r][c] if board[r][c] != '.' else ' '
        game_instance.board = board

        # Re-evaluate game state
        x_count = sum(row.count('X') for row in board)
        o_count = sum(row.count('O') for row in board)
        game_instance.current_player = 'O' if x_count > o_count else 'X'
        game_instance.check_winner() # This updates game_over, winner, and winner_line

        return game_instance

    def _format_response(self, game_instance: TicTacToe, force_ongoing: bool = False) -> str:
        """Converts a TicTacToe instance to the protocol response string."""
        board_str = self._get_board_string(game_instance)
        
        if force_ongoing:
            result_str, line_str = "ONGOING", ""
        else:
            result_str, line_str = self._get_game_result(game_instance)
            
        return f"{board_str}:{result_str}:{line_str}"

    def _get_board_string(self, game_instance: TicTacToe) -> str:
        """Converts the board state to a 9-char string."""
        return "".join(cell if cell != ' ' else "." for row in game_instance.board for cell in row)

    def _get_game_result(self, game_instance: TicTacToe) -> tuple[str, str]:
        """Returns game result ('WIN', 'LOSE', 'DRAW', 'ONGOING') and winning line."""
        if not game_instance.game_over:
            return "ONGOING", ""

        winner = game_instance.winner
        human_symbol = game_instance.human_player

        line_str = ""
        if game_instance.winner_line:
            indices = [r * 3 + c for r, c in game_instance.winner_line]
            line_str = ",".join(map(str, indices))

        if winner == "draw":
            return "DRAW", line_str
        elif winner == human_symbol:
            return "WIN", line_str
        else: # AI won
            return "LOSE", line_str
