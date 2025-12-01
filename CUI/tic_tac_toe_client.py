import requests
import time
from .cui_display import display_board  # Will create this module later


class TicTacToeClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.available_agents = None  # キャッシュ用

    def _send_request(self, method: str, endpoint: str, data: dict = None):
        url = f"{self.server_url}/{endpoint}"
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data)
            elif method.upper() == "GET":
                response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                error_detail = e.response.json().get("detail", "Invalid move")
                print(f"Error: {error_detail}")
                raise ValueError(error_detail)  # Raise a specific error for invalid moves
            elif e.response.status_code == 404:
                print("Error: Game not started or endpoint not found.")
                raise ValueError("Game not started")
            else:
                print(f"HTTP Error: {e}")
                raise
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Could not connect to the server at {self.server_url}. Is the server running?")
            raise
        except requests.exceptions.RequestException:
            print("An unexpected error occurred during request.")
            raise

    def get_player_symbol_choice(self):
        while True:
            choice = input("Choose your player (X/O): ").strip().upper()
            if choice in ["X", "O"]:
                return choice
            else:
                print("Invalid choice. Please enter 'X' or 'O'.")

    def get_available_agents(self):
        """
        サーバーから利用可能な agent のリストを取得
        
        Returns:
            list: agent 名のリスト、エラー時は None
        """
        if self.available_agents is not None:
            return self.available_agents  # キャッシュを返す
        
        try:
            response = self._send_request("GET", "agents")
            self.available_agents = response.get("agents", [])
            return self.available_agents
        except requests.exceptions.RequestException:
            print("Warning: Could not fetch agent list from server. Using fallback list.")
            # フォールバック: デフォルトのリスト
            self.available_agents = ["Human", "Random", "Minimax", "Database", "QLearning", "Perfect"]
            return self.available_agents

    def get_agent_type_choice(self, player_char):
        agent_types = self.get_available_agents()
        
        if not agent_types:
            print("Error: No agents available.")
            return "Human"  # フォールバック
        
        while True:
            print(f"\nChoose agent type for player {player_char}:")
            for i, agent_type in enumerate(agent_types):
                print(f"{i+1}. {agent_type}")
            try:
                choice_num = int(input(f"Enter number (1-{len(agent_types)}): "))
                if 1 <= choice_num <= len(agent_types):
                    return agent_types[choice_num - 1]
                else:
                    print(f"Invalid number. Please enter a number between 1 and {len(agent_types)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def get_user_move(self):
        while True:
            user_input = input("Enter your move (1-9) or 'q' to quit: ").strip().lower()
            if user_input in ["q", "quit"]:
                return None
            try:
                move_num = int(user_input)
                if 1 <= move_num <= 9:
                    row = (move_num - 1) // 3
                    col = (move_num - 1) % 3
                    return row, col
                else:
                    print("Invalid input. Please enter a number between 1 and 9.")
            except ValueError:
                print("Invalid input format. Please enter a single number or 'q'.")

    def play_single_game(self):
        print("\n--- Start New Tic Tac Toe Game ---")
        human_player_symbol = self.get_player_symbol_choice()

        player_x_type = self.get_agent_type_choice("X")
        player_o_type = self.get_agent_type_choice("O")

        start_game_data = {
            "human_player_symbol": human_player_symbol,
            "player_x_type": player_x_type,
            "player_o_type": player_o_type,
        }

        print("\nStarting new Tic Tac Toe game...")
        try:
            game_state = self._send_request("POST", "game/start", start_game_data)
            display_board(game_state)
        except (requests.exceptions.RequestException, ValueError):
            return  # Allow main loop to prompt for play again

        while not game_state["game_over"]:
            current_player = game_state["current_player"]

            is_human_turn = False
            if current_player == "X" and player_x_type == "Human":
                is_human_turn = True
            elif current_player == "O" and player_o_type == "Human":
                is_human_turn = True

            if is_human_turn:
                move = self.get_user_move()
                if move is None:  # User chose to quit
                    print("Game interrupted by user.")
                    return  # Exit current game
                row, col = move
                try:
                    game_state = self._send_request("POST", "game/move", {"row": row, "col": col})
                    display_board(game_state)
                except ValueError:  # Caught invalid move from _send_request
                    continue  # Prompt for move again
                except requests.exceptions.RequestException:
                    break  # Fatal error, exit game loop
            else:
                print(f"Player {current_player} (Agent) is thinking...")
                time.sleep(1)  # Simulate agent thinking
                try:
                    game_state = self._send_request("GET", "game/status")
                    display_board(game_state)
                except requests.exceptions.RequestException:
                    break  # Fatal error, exit game loop
