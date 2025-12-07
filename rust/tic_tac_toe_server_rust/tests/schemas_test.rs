// rust/tic_tac_toe_server_rust/tests/schemas_test.rs

use tic_tac_toe_server_rust::schemas::{StartGameRequest, BoardState, MoveRequest, AvailableAgentsResponse};
use tic_tac_toe_server_rust::game_logic::Player;
use serde_json;

#[test]
fn test_start_game_request_serialization() {
    let req = StartGameRequest {
        human_player_symbol: Some(Player::X),
        player_x_type: "Human".to_string(),
        player_o_type: "Random".to_string(),
    };
    let json = serde_json::to_string(&req).unwrap();
    assert_eq!(json, r#"{"human_player_symbol":"X","player_x_type":"Human","player_o_type":"Random"}"#);

    let req_none = StartGameRequest {
        human_player_symbol: None,
        player_x_type: "Random".to_string(),
        player_o_type: "Human".to_string(),
    };
    let json_none = serde_json::to_string(&req_none).unwrap();
    // human_player_symbol が None の場合、フィールドが省略されることを期待
    assert_eq!(json_none, r#"{"player_x_type":"Random","player_o_type":"Human"}"#);
}

#[test]
fn test_start_game_request_deserialization() {
    let json = r#"{"human_player_symbol":"O","player_x_type":"Minimax","player_o_type":"Human"}"#;
    let req: StartGameRequest = serde_json::from_str(json).unwrap();
    assert_eq!(req.human_player_symbol, Some(Player::O));
    assert_eq!(req.player_x_type, "Minimax");
    assert_eq!(req.player_o_type, "Human");

    let json_no_human = r#"{"player_x_type":"Random","player_o_type":"Minimax"}"#;
    let req_no_human: StartGameRequest = serde_json::from_str(json_no_human).unwrap();
    assert_eq!(req_no_human.human_player_symbol, None);
    assert_eq!(req_no_human.player_x_type, "Random");
    assert_eq!(req_no_human.player_o_type, "Minimax");
}

#[test]
fn test_board_state_serialization() {
    let board_array = [
        [Player::X, Player::None, Player::O],
        [Player::None, Player::X, Player::None],
        [Player::O, Player::None, Player::X],
    ];
    let bs = BoardState {
        board: board_array,
        current_player: Player::O,
        winner: Some(Player::X),
        winner_line: Some([(0,0), (1,1), (2,2)]),
        game_over: true,
    };
    let json = serde_json::to_string(&bs).unwrap();
    // BoardStateのboardフィールドが固定配列[[Player;3];3]なので、json出力はネストした配列になる
    // Player::None は " " にシリアライズされる
    assert_eq!(json, r#"{"board":[["X"," ","O"],[" ","X"," "],["O"," ","X"]],"current_player":"O","winner":"X","winner_line":[[0,0],[1,1],[2,2]],"game_over":true}"#);
}

#[test]
fn test_board_state_deserialization() {
    let json = r#"{
        "board":[["X"," ","O"],[" ","X"," "],["O"," ","X"]],
        "current_player":"O",
        "winner":"X",
        "winner_line":[[0,0],[1,1],[2,2]],
        "game_over":true
    }"#;
    let bs: BoardState = serde_json::from_str(json).unwrap();
    assert_eq!(bs.board[0][0], Player::X);
    assert_eq!(bs.board[0][1], Player::None);
    assert_eq!(bs.board[0][2], Player::O);
    assert_eq!(bs.current_player, Player::O);
    assert_eq!(bs.winner, Some(Player::X));
    assert_eq!(bs.winner_line, Some([(0,0), (1,1), (2,2)]));
    assert_eq!(bs.game_over, true);

    let json_draw = r#"{
        "board":[["X","O","X"],["X","O","O"],["O","X","X"]],
        "current_player":"O",
        "winner":" ",
        "winner_line":null,
        "game_over":true
    }"#;
    let bs_draw: BoardState = serde_json::from_str(json_draw).unwrap();
    assert_eq!(bs_draw.winner, Some(Player::None));
}

#[test]
fn test_board_state_deserialization_invalid_row_count() {
    let json = r#"{
        "board":[["X"," ","O"],[" ","X"," "]],
        "current_player":"O",
        "winner":"X",
        "winner_line":[[0,0],[1,1],[2,2]],
        "game_over":true
    }"#;
    let result: Result<BoardState, _> = serde_json::from_str(json);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Board must have 3 rows"));
}

#[test]
fn test_board_state_deserialization_invalid_col_count() {
    let json = r#"{
        "board":[["X"," ","O"],[" ","X"],["O"," ","X"]],
        "current_player":"O",
        "winner":"X",
        "winner_line":[[0,0],[1,1],[2,2]],
        "game_over":true
    }"#;
    let result: Result<BoardState, _> = serde_json::from_str(json);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Each row of the board must have 3 elements"));
}

#[test]
fn test_move_request_serialization() {
    let req = MoveRequest { row: 0, col: 1 };
    let json = serde_json::to_string(&req).unwrap();
    assert_eq!(json, r#"{"row":0,"col":1}"#);
}

#[test]
fn test_move_request_deserialization() {
    let json = r#"{"row":2,"col":2}"#;
    let req: MoveRequest = serde_json::from_str(json).unwrap();
    assert_eq!(req.row, 2);
    assert_eq!(req.col, 2);
}

#[test]
fn test_available_agents_response_serialization() {
    let resp = AvailableAgentsResponse { agents: vec!["Human".to_string(), "Random".to_string()] };
    let json = serde_json::to_string(&resp).unwrap();
    assert_eq!(json, r#"{"agents":["Human","Random"]}"#);
}

#[test]
fn test_available_agents_response_deserialization() {
    let json = r#"{"agents":["Human","Minimax"]}"#;
    let resp: AvailableAgentsResponse = serde_json::from_str(json).unwrap();
    assert_eq!(resp.agents, vec!["Human","Minimax"]);
}
