from pydantic import BaseModel
from typing import List, Optional, Tuple, Literal

class StartGameRequest(BaseModel):
    human_player_symbol: Literal["X", "O"] # CUIの人間プレイヤーのシンボル
    player_x_type: str # Xプレイヤーのタイプ (Human, Random, Minimax, QLearning, Perfect)
    player_o_type: str # Oプレイヤーのタイプ (Human, Random, Minimax, QLearning, Perfect)

class BoardState(BaseModel):
    board: List[List[str]]
    current_player: str
    winner: Optional[str]
    winner_line: Optional[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]
    game_over: bool

class MoveRequest(BaseModel):
    row: int
    col: int
