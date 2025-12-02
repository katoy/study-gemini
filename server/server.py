import logging  # Added import
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional  # Add this import
from .schemas import StartGameRequest, BoardState, MoveRequest, AvailableAgentsResponse
from .game_manager import GameManager  # Import the class, not the instance

PLAYER_X = "X"
PLAYER_O = "O"
DB_PATH = "tictactoe.db"
Q_TABLE_PATH = "q_table.json"
PERFECT_MOVES_FILE = "perfect_moves.json"

# Configure logging to a file
logging.basicConfig(
    level=logging.INFO,  # Set desired log level (e.g., DEBUG, INFO, WARNING, ERROR)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to app.log
        logging.StreamHandler(),  # Also log to console (stdout/stderr)
    ],
)
# Suppress uvicorn's default handler to avoid duplicate logs if StreamHandler is added
# For uvicorn logs specifically, you might configure its loggers later or disable its default
# However, the above basicConfig will set up a root logger which most things will use.
# To specifically capture uvicorn's access logs and ensure they go to file:
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = [
    logging.FileHandler("app.log"),
    logging.StreamHandler(),
]
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.handlers = [
    logging.FileHandler("app.log"),
    logging.StreamHandler(),
]


app = FastAPI()

# CORS設定（必ずFastAPIインスタンス作成直後に追加）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# GameManagerのシングルトンインスタンスを保持
_game_manager_instance: Optional[GameManager] = None


def get_game_manager() -> GameManager:
    global _game_manager_instance
    if _game_manager_instance is None:
        _game_manager_instance = GameManager()
    return _game_manager_instance


@app.post("/game/start", response_model=BoardState)
async def start_game(
    request: StartGameRequest, game_manager: GameManager = Depends(get_game_manager)
):
    game_instance = game_manager.start_new_game(
        request.player_x_type, request.player_o_type, request.human_player_symbol
    )
    return BoardState(
        board=game_instance.board,
        current_player=game_instance.current_player,
        winner=game_instance.check_winner(),
        winner_line=game_instance.winner_line,
        game_over=game_instance.game_over,
    )


@app.get("/game/status", response_model=BoardState)
async def get_game_status(game_manager: GameManager = Depends(get_game_manager)):
    game_state = game_manager.get_current_game_state()
    return BoardState(**game_state)


@app.post("/game/move", response_model=BoardState)
async def make_move(
    move_request: MoveRequest, game_manager: GameManager = Depends(get_game_manager)
):
    game_instance = game_manager.make_player_move(move_request.row, move_request.col)
    winner = game_instance.check_winner()
    return BoardState(
        board=game_instance.board,
        current_player=game_instance.current_player,
        winner=winner,
        winner_line=game_instance.winner_line,
        game_over=game_instance.game_over,
    )


@app.get("/agents", response_model=AvailableAgentsResponse)
async def get_available_agents(game_manager: GameManager = Depends(get_game_manager)):
    agents = game_manager.get_available_agents()
    return AvailableAgentsResponse(agents=agents)
