from ble_pico_server.tic_tac_toe import TicTacToe
from ble_pico_server.agents.random_agent import RandomAgent
import gc # For garbage collection, useful in MicroPython

class GameAdapter:
    """
    Adapts the TicTacToe game logic for stateless use with the BLE Tic-Tac-Toe client (micro:bit).
    Handles string-based protocol conversion.
    This version is simplified for MicroPython on Pico W.

    A stateless protocol is defined for communication:

    Client -> Server (Pico W):
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

    Server (Pico W) -> Client:
    - <BOARD_STATE>:<GAME_RESULT>:<WIN_LINE>
      - Description: The response after a start or move.
      - BOARD_STATE: The updated 9-char board string.
      - GAME_RESULT: 'ONGOING', 'WIN', 'LOSE', or 'DRAW'.
      - WIN_LINE: Comma-separated indices of the winning line (e.g., "0,4,8"), or empty.
      - Example: "X.O.X..O.:WIN:0,4,8"
    """
    def __init__(self, default_ai_agent="Random"):
        # For simplicity, we directly manage the game state within the adapter
        # and create agents directly. GameManager is too complex for Pico W.
        self.default_ai_agent = default_ai_agent
        self.current_game: TicTacToe = None # Stores the current game instance
        print(f"GameAdapter initialized with AI: {self.default_ai_agent}")

    def _create_agent(self, agent_type, symbol):
        if agent_type == "Random":
            return RandomAgent(symbol)
        # Add other agents here as they are implemented for MicroPython
        return None

    def handle_command(self, command: str) -> tuple | str:
        """
        Process a stateless command from the micro:bit.
        Returns: A single string response for the client,
                 or a tuple (ongoing_response, result_response) for game over.
        """
        command = command.strip()
        print(f"Received command: {command}")
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
                
                # Recreate game instance based on the received board state
                # This makes the adapter stateless from the perspective of the *client*
                # but keeps a current_game instance for internal logic.
                self.current_game = self._recreate_game_from_str(board_state_str, human_symbol)
                
                if self.current_game.game_over:
                    print("Move received for a finished game.")
                    # Return game over sequence if already finished
                    ongoing_response = self._format_response(self.current_game, force_ongoing=True)
                    result_str, line_str = self._get_game_result(self.current_game)
                    result_response = f"RESULT:{result_str}:{line_str}"
                    return ongoing_response, result_response


                # Force the current player to be the one specified by the client (human)
                self.current_game.current_player = human_symbol

                # Execute human move
                row, col = move_index // 3, move_index % 3
                if not self.current_game.make_move(row, col):
                    print(f"Invalid human move at ({row}, {col}).")
                    return self._format_response(self.current_game) # Return current state, perhaps with error?

                self.current_game.check_winner()
                self.current_game.switch_player() # Switch to AI after human move

                # If game isn't over, let the AI move
                if not self.current_game.game_over:
                    ai_agent = self.current_game.get_current_agent()
                    if ai_agent:
                        print(f"Running AI ({ai_agent.symbol}) move.")
                        ai_move = ai_agent.choose_move(self.current_game)
                        if ai_move:
                            self.current_game.make_move(ai_move[0], ai_move[1])
                            self.current_game.check_winner()
                            self.current_game.switch_player() # Switch back to human for next turn
                        else:
                            print("AI could not make a move (board full or error).")
                    else:
                        print("No AI agent configured for current player.")

                # Format response (2-step for game over)
                if self.current_game.game_over:
                    # First response: Final board, but marked as "ONGOING"
                    ongoing_response = self._format_response(self.current_game, force_ongoing=True)
                    
                    # Second response: The actual result message
                    result_str, line_str = self._get_game_result(self.current_game)
                    result_response = f"RESULT:{result_str}:{line_str}"
                    
                    return ongoing_response, result_response
                else:
                    return self._format_response(self.current_game)

            if cmd == "RESET":
                self.current_game = None # Clear current game
                gc.collect() # Trigger garbage collection
                return ".........:ONGOING:"

        except (IndexError, ValueError) as e:
            print(f"Error: Invalid command format '{command}': {e}")
        except Exception as e:
            print(f"Error processing command '{command}': {e}")

        # Return a default safe state on error or if current_game is not set
        if not self.current_game:
            return ".........:ONGOING:"
        else:
            return self._format_response(self.current_game)

    def _start_game(self, human_symbol: str) -> str:
        """Starts a new game, possibly with an initial AI move."""
        print(f"Starting new game for human as '{human_symbol}'")
        player_x_type = "Human" if human_symbol == "X" else self.default_ai_agent
        player_o_type = "Human" if human_symbol == "O" else self.default_ai_agent

        agent_x_instance = self._create_agent(player_x_type, "X") if player_x_type != "Human" else None
        agent_o_instance = self._create_agent(player_o_type, "O") if player_o_type != "Human" else None

        self.current_game = TicTacToe(agent_x=agent_x_instance, agent_o=agent_o_instance, human_player=human_symbol)

        # If AI is 'X' (the first player), it moves immediately.
        if self.current_game.get_current_agent():
            print("AI is starting first.")
            ai_agent = self.current_game.get_current_agent()
            ai_move = ai_agent.choose_move(self.current_game)
            if ai_move:
                self.current_game.make_move(ai_move[0], ai_move[1])
                self.current_game.check_winner()
                self.current_game.switch_player() # Switch to human for next turn
            else:
                print("AI could not make a move (board full or error).")

        return self._format_response(self.current_game)

    def _recreate_game_from_str(self, board_state_str: str, human_symbol: str) -> TicTacToe:
        """Creates a TicTacToe instance from a board string and human player symbol."""
        player_x_type = "Human" if human_symbol == "X" else self.default_ai_agent
        player_o_type = "Human" if human_symbol == "O" else self.default_ai_agent
        
        agent_x_instance = self._create_agent(player_x_type, "X") if player_x_type != "Human" else None
        agent_o_instance = self._create_agent(player_o_type, "O") if player_o_type != "Human" else None
        
        game_instance = TicTacToe(
            agent_x=agent_x_instance,
            agent_o=agent_o_instance,
            human_player=human_symbol
        )

        # Reconstruct board state
        board = [list(board_state_str[i:i+3]) for i in range(0, 9, 3)]
        for r in range(3):
            for c in range(3):
                board[r][c] = board[r][c] if board[r][c] != '.' else ' '
        game_instance.board = board

        # Determine current player and check winner based on reconstructed board
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

    def _get_game_result(self, game_instance: TicTacToe) -> tuple:
        """Returns game result ('WIN', 'LOSE', 'DRAW', 'ONGOING') and winning line."""
        if not game_instance.game_over:
            return "ONGOING", ""

        winner = game_instance.winner
        human_symbol = game_instance.human_player

        line_str = ""
        if game_instance.winner_line:
            # Convert (r, c) tuples to single index 0-8
            indices = [r * 3 + c for r, c in game_instance.winner_line]
            line_str = ",".join(map(str, indices))

        if winner == "draw":
            return "DRAW", line_str
        elif winner == human_symbol:
            return "WIN", line_str
        else: # AI won
            return "LOSE", line_str
