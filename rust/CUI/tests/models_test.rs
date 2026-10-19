use cui::models::{GameState, MoveRequest};

#[test]
fn test_game_state_deserialization() {
    let json_str = r#"
    {
        "board": [["X", " ", " "], [" ", "O", " "], [" ", " ", " "]],
        "current_player": "X",
        "game_over": false,
        "winner": null
    }
    "#;
    let game_state: GameState = serde_json::from_str(json_str).unwrap();
    assert_eq!(game_state.board[0][0], "X");
    assert_eq!(game_state.current_player, "X");
    assert!(!game_state.game_over);
    assert!(game_state.winner.is_none());
}

#[test]
fn test_move_request_serialization() {
    let move_req = MoveRequest { row: 1, col: 2 };
    let json_str = serde_json::to_string(&move_req).unwrap();
    assert_eq!(json_str, r#"{"row":1,"col":2}"#);
}
