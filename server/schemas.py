from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Tuple, Literal


class StartGameRequest(BaseModel):
    human_player_symbol: Literal["X", "O"]  # CUIの人間プレイヤーのシンボル
    player_x_type: str  # Xプレイヤーのタイプ (Human, Random, Minimax, QLearning, Perfect)
    player_o_type: str  # Oプレイヤーのタイプ (Human, Random, Minimax, QLearning, Perfect)


class BoardState(BaseModel):
    board: List[List[str]] = Field(min_length=3, max_length=3)  # Ensure 3 rows
    current_player: str
    winner: Optional[str]
    winner_line: Optional[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]
    game_over: bool

    @field_validator('board', mode='after')
    @classmethod
    def check_board_row_length(cls, v: List[List[str]]):
        for row in v:
            if not (isinstance(row, list) and len(row) == 3):
                raise ValueError('Each row of the board must have 3 elements')
        return v


class MoveRequest(BaseModel):
    row: int = Field(ge=0, le=2)  # row must be between 0 and 2
    col: int = Field(ge=0, le=2)  # col must be between 0 and 2
