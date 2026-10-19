use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct GameState {
    pub board: Vec<Vec<String>>,
    pub current_player: String,
    pub game_over: bool,
    pub winner: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Agents {
    pub agents: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ErrorDetail {
    pub detail: String,
}

#[derive(Serialize)]

pub struct MoveRequest {
    pub row: usize,

    pub col: usize,
}

#[derive(Serialize)]

pub struct StartGameRequest {
    pub human_player_symbol: Option<String>,

    pub player_x_type: String,

    pub player_o_type: String,
}
