// rust/tic_tac_toe_server_rust/src/schemas.rs

use serde::{Deserialize, Serialize};
use validator::Validate;
use crate::game_logic::Player;
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, Clone, ToSchema)]
pub struct StartGameRequest {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub human_player_symbol: Option<Player>,
    pub player_x_type: String,
    pub player_o_type: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, ToSchema)]
pub struct BoardState {
    #[serde(with = "crate::schemas::board_serializer")]
    pub board: [[Player; 3]; 3],
    pub current_player: Player,
    pub winner: Option<Player>,
    pub winner_line: Option<[(usize, usize); 3]>,
    pub game_over: bool,
}

// BoardState の board フィールドのカスタムシリアライザ/デシリアライザ
pub mod board_serializer {
    use serde::{Serializer, Deserializer, Deserialize, Serialize};
    use crate::game_logic::{Board, Player};

    pub fn serialize<S>(board: &Board, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let vec_board: Vec<Vec<Player>> = board.iter().map(|row| row.to_vec()).collect();
        vec_board.serialize(serializer)
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<Board, D::Error>
    where
        D: Deserializer<'de>,
    {
        let vec_board = Vec::<Vec<Player>>::deserialize(deserializer)?;
        if vec_board.len() != 3 {
            return Err(serde::de::Error::custom("Board must have 3 rows"));
        }
        let mut board_array = [[Player::None; 3]; 3];
        for (i, row) in vec_board.into_iter().enumerate() {
            if row.len() != 3 {
                return Err(serde::de::Error::custom("Each row of the board must have 3 elements"));
            }
            for (j, cell) in row.into_iter().enumerate() {
                board_array[i][j] = cell;
            }
        }
        Ok(board_array)
    }
}


#[derive(Debug, Serialize, Deserialize, Validate, ToSchema)]
pub struct MoveRequest {
    #[validate(range(min = 0, max = 2))]
    pub row: usize,
    #[validate(range(min = 0, max = 2))]
    pub col: usize,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct AvailableAgentsResponse {
    pub agents: Vec<String>,
}

#[derive(Serialize, ToSchema)]
pub struct ErrorResponse {
    pub detail: String,
}
