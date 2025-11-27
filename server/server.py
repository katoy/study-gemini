from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple

from game_logic import TicTacToe

app = FastAPI()

# In-memory game state
game: Optional[TicTacToe] = None

class BoardState(BaseModel):
    board: List[List[str]]
    current_player: str
    winner: Optional[str]
    winner_line: Optional[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]
    game_over: bool

@app.post("/game/start", response_model=BoardState)
async def start_game():
    global game
    game = TicTacToe()
    return BoardState(
        board=game.board,
        current_player=game.current_player,
        winner=game.check_winner(),
        winner_line=game.winner_line,
        game_over=game.game_over
    )

@app.get("/game/status", response_model=BoardState)
async def get_game_status():
    if game is None:
        raise HTTPException(status_code=404, detail="Game not started")
    return BoardState(
        board=game.board,
        current_player=game.current_player,
        winner=game.check_winner(),
        winner_line=game.winner_line,
        game_over=game.game_over
    )

class MoveRequest(BaseModel):
    row: int
    col: int

@app.post("/game/move", response_model=BoardState)
async def make_move(move_request: MoveRequest):
    global game
    if game is None:
        raise HTTPException(status_code=404, detail="Game not started")

    if not game.make_move(move_request.row, move_request.col):
        raise HTTPException(status_code=400, detail="Invalid move")

    winner = game.check_winner()
    if winner is None:
        game.switch_player()

    return BoardState(
        board=game.board,
        current_player=game.current_player,
        winner=winner,
        winner_line=game.winner_line,
        game_over=game.game_over
    )
