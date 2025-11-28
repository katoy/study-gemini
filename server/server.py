from fastapi import FastAPI
from game_logic import TicTacToe # Removed this in previous step, should add back if needed.
from .schemas import StartGameRequest, BoardState, MoveRequest

from .schemas import StartGameRequest, BoardState, MoveRequest

PLAYER_X = "X"
PLAYER_O = "O"
DB_PATH = "tictactoe.db"
Q_TABLE_PATH = "q_table.json"
PERFECT_MOVES_FILE = "perfect_moves.json"

app = FastAPI()



from .game_manager import game_manager



@app.post("/game/start", response_model=BoardState)
async def start_game(request: StartGameRequest):
    game_instance = game_manager.start_new_game(
        request.player_x_type, request.player_o_type, request.human_player_symbol
    )
    return BoardState(
        board=game_instance.board,
        current_player=game_instance.current_player,
        winner=game_instance.check_winner(),
        winner_line=game_instance.winner_line,
        game_over=game_instance.game_over
    )

@app.get("/game/status", response_model=BoardState)
async def get_game_status():
    game_state = game_manager.get_current_game_state()
    return BoardState(**game_state)



@app.post("/game/move", response_model=BoardState)
async def make_move(move_request: MoveRequest):
    game_instance = game_manager.make_player_move(move_request.row, move_request.col)
    winner = game_instance.check_winner() # check_winner again for final state
    return BoardState(
        board=game_instance.board,
        current_player=game_instance.current_player,
        winner=winner,
        winner_line=game_instance.winner_line,
        game_over=game_instance.game_over
    )