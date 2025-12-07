// rust/tic_tac_toe_server_rust/tests/game_logic_test.rs

#![allow(unused_imports)] // Move と WinnerLine の unused import 警告を無視

use tic_tac_toe_server_rust::game_logic::{Player, TicTacToe, Board, Move, WinnerLine};
use std::str::FromStr; // 追加
use tic_tac_toe_server_rust::agents::{self, Agent}; // Agentトレイトのbox_cloneを使うため

// Player enum のテスト
#[test]
fn test_player_from_str() {
    assert_eq!("X".parse::<Player>().ok(), Some(Player::X));
    assert_eq!("O".parse::<Player>().ok(), Some(Player::O));
    assert_eq!(" ".parse::<Player>().ok(), Some(Player::None));
    assert_eq!(".".parse::<Player>().ok(), Some(Player::None));
    assert_eq!("".parse::<Player>().ok(), Some(Player::None));
    assert_eq!("Z".parse::<Player>().ok(), None);
}

#[test]
fn test_player_opponent() {
    assert_eq!(Player::X.opponent(), Player::O);
    assert_eq!(Player::O.opponent(), Player::X);
    assert_eq!(Player::None.opponent(), Player::None);
}

#[test]
fn test_player_display() {
    assert_eq!(format!("{}", Player::X), "X");
    assert_eq!(format!("{}", Player::O), "O");
    assert_eq!(format!("{}", Player::None), " ");
}

// TicTacToe 構造体のテスト
#[test]
fn test_new_game() {
    let game = TicTacToe::new(None, None, None);
    assert_eq!(game.board, [[Player::None; 3]; 3]);
    assert_eq!(game.current_player, Player::X);
    assert_eq!(game.winner, None);
    assert_eq!(game.winner_line, None);
    assert!(!game.game_over);
    assert!(game.agent_x.is_none());
    assert!(game.agent_o.is_none());
    assert!(game.human_player.is_none());
}

#[test]
fn test_make_valid_move() {
    let mut game = TicTacToe::new(None, None, None);
    let result = game.make_move(0, 0);
    assert!(result.is_ok());
    assert_eq!(game.board[0][0], Player::X);
    assert_eq!(game.current_player, Player::O); // 手番が切り替わる
    assert!(!game.game_over);
}

#[test]
fn test_make_invalid_move_out_of_bounds() {
    let mut game = TicTacToe::new(None, None, None);
    let result = game.make_move(3, 0);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Move is out of board bounds.");
    assert_eq!(game.current_player, Player::X); // 手番は切り替わらない
}

#[test]
fn test_make_invalid_move_occupied() {
    let mut game = TicTacToe::new(None, None, None);
    game.make_move(0, 0).unwrap(); // X が (0,0) に打つ
    let result = game.make_move(0, 0); // O が (0,0) に打とうとする
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Cell is already occupied.");
    assert_eq!(game.current_player, Player::O); // Oの手番のまま
}

#[test]
fn test_make_move_game_over() {
    let mut game = TicTacToe::new(None, None, None);
    game.game_over = true;
    let result = game.make_move(0, 0);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), "Game is already over.");
    assert_eq!(game.current_player, Player::X); // 手番は切り替わらない
}

#[test]
fn test_switch_player() {
    let mut game = TicTacToe::new(None, None, None);
    assert_eq!(game.current_player, Player::X);
    game.switch_player();
    assert_eq!(game.current_player, Player::O);
    game.switch_player();
    assert_eq!(game.current_player, Player::X);
}

#[test]
fn test_check_winner_logic_row_x() {
    let board: Board = [
        [Player::X, Player::X, Player::X],
        [Player::O, Player::None, Player::None],
        [Player::None, Player::None, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::X));
    assert_eq!(winner_line, Some([(0, 0), (0, 1), (0, 2)]));
}

#[test]
fn test_check_winner_logic_col_o() {
    let board: Board = [
        [Player::X, Player::O, Player::None],
        [Player::X, Player::O, Player::None],
        [Player::None, Player::O, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::O));
    assert_eq!(winner_line, Some([(0, 1), (1, 1), (2, 1)]));
}

#[test]
fn test_check_winner_logic_diag_x() {
    let board: Board = [
        [Player::X, Player::O, Player::None],
        [Player::None, Player::X, Player::O],
        [Player::None, Player::None, Player::X],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::X));
    assert_eq!(winner_line, Some([(0, 0), (1, 1), (2, 2)]));
}

#[test]
fn test_check_winner_logic_anti_diag_o() {
    let board: Board = [
        [Player::X, Player::X, Player::O],
        [Player::X, Player::O, Player::None],
        [Player::O, Player::None, Player::X],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::O));
    assert_eq!(winner_line, Some([(0, 2), (1, 1), (2, 0)]));
}

#[test]
fn test_check_winner_logic_no_winner() {
    let board: Board = [
        [Player::X, Player::O, Player::X],
        [Player::O, Player::X, Player::O],
        [Player::None, Player::None, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, None);
    assert_eq!(winner_line, None);
}

#[test]
fn test_is_board_full_not_full() {
    let game = TicTacToe::new(None, None, None);
    assert!(!game.is_board_full());
}

#[test]
fn test_is_board_full_full() {
    let mut game = TicTacToe::new(None, None, None);
    game.board = [
        [Player::X, Player::O, Player::X],
        [Player::O, Player::X, Player::O],
        [Player::O, Player::X, Player::O],
    ];
    assert!(game.is_board_full());
}

#[test]
fn test_get_available_moves_empty_board() {
    let game = TicTacToe::new(None, None, None);
    let moves = game.get_available_moves();
    assert_eq!(moves.len(), 9);
    assert!(moves.contains(&(0, 0)));
    assert!(moves.contains(&(2, 2)));
}

#[test]
fn test_get_available_moves_partial_board() {
    let mut game = TicTacToe::new(None, None, None);
    game.make_move(0, 0).unwrap(); // X
    game.make_move(1, 1).unwrap(); // O
    let moves = game.get_available_moves();
    assert_eq!(moves.len(), 7);
    assert!(!moves.contains(&(0, 0)));
    assert!(!moves.contains(&(1, 1)));
    assert!(moves.contains(&(0, 1)));
}

#[test]
fn test_get_available_moves_full_board() {
    let mut game = TicTacToe::new(None, None, None);
    game.board = [
        [Player::X, Player::O, Player::X],
        [Player::O, Player::X, Player::O],
        [Player::O, Player::X, Player::O],
    ];
    let moves = game.get_available_moves();
    assert!(moves.is_empty());
}

#[test]
fn test_get_current_agent() {
    let agent_x = Box::new(agents::HumanAgent::new(Player::X));
    let agent_o = Box::new(agents::RandomAgent::new(Player::O));
    let mut original_game = TicTacToe::new(Some(agent_x.box_clone()), Some(agent_o.box_clone()), Some(Player::X));

    assert!(original_game.get_current_agent().is_some());
    assert_eq!(original_game.get_current_agent().unwrap().get_player(), Player::X);

    original_game.switch_player();
    assert!(original_game.get_current_agent().is_some());
    assert_eq!(original_game.get_current_agent().unwrap().get_player(), Player::O);

    original_game.current_player = Player::None;
    assert!(original_game.get_current_agent().is_none());
}

#[test]
fn test_game_over_draw() {
    let mut game = TicTacToe::new(None, None, None);
    game.board = [
        [Player::X, Player::O, Player::X],
        [Player::X, Player::X, Player::O],
        [Player::O, Player::X, Player::O],
    ];
    game.current_player = Player::X; // 最終手は打たない
    game.check_game_state(); // 手動で状態をチェック
    assert!(game.game_over);
    assert_eq!(game.winner, Some(Player::None)); // 引き分け
}

#[test]
fn test_game_over_win() {
    let mut game = TicTacToe::new(None, None, None);
    game.board = [
        [Player::X, Player::X, Player::None],
        [Player::O, Player::O, Player::None],
        [Player::None, Player::None, Player::None],
    ];
    game.current_player = Player::X;
    game.make_move(0, 2).unwrap(); // Xが勝つ
    assert!(game.game_over);
    assert_eq!(game.winner, Some(Player::X));
}
// Additional win condition tests

#[test]
fn test_check_winner_logic_column_x() {
    let board: Board = [
        [Player::X, Player::O, Player::None],
        [Player::X, Player::O, Player::None],
        [Player::X, Player::None, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::X));
    assert_eq!(winner_line, Some([(0, 0), (1, 0), (2, 0)]));
}

#[test]
fn test_check_winner_logic_diagonal_o() {
    let board: Board = [
        [Player::O, Player::X, Player::None],
        [Player::X, Player::O, Player::None],
        [Player::None, Player::None, Player::O],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::O));
    assert_eq!(winner_line, Some([(0, 0), (1, 1), (2, 2)]));
}

#[test]
fn test_check_winner_logic_anti_diagonal_o() {
    let board: Board = [
        [Player::X, Player::None, Player::O],
        [Player::None, Player::O, Player::None],
        [Player::O, Player::None, Player::X],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::O));
    assert_eq!(winner_line, Some([(0, 2), (1, 1), (2, 0)]));
}

#[test]
fn test_check_winner_logic_all_none() {
    let board: Board = [
        [Player::None, Player::None, Player::None],
        [Player::None, Player::None, Player::None],
        [Player::None, Player::None, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, None);
    assert_eq!(winner_line, None);
}

#[test]
fn test_check_winner_logic_row_o() {
    let board: Board = [
        [Player::O, Player::O, Player::O],
        [Player::X, Player::None, Player::None],
        [Player::None, Player::X, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::O));
    assert_eq!(winner_line, Some([(0, 0), (0, 1), (0, 2)]));
}

#[test]
fn test_check_winner_logic_column_o() {
    let board: Board = [
        [Player::O, Player::X, Player::None],
        [Player::O, Player::None, Player::X],
        [Player::O, Player::None, Player::None],
    ];
    let (winner, winner_line) = TicTacToe::check_winner_logic(&board);
    assert_eq!(winner, Some(Player::O));
    assert_eq!(winner_line, Some([(0, 0), (1, 0), (2, 0)]));
}



#[test]
fn test_player_from_str_invalid() {
    assert_eq!("INVALID".parse::<Player>().ok(), None);
}

#[test]
fn test_player_deserialize_invalid() {
    let json = r#""INVALID_PLAYER_STRING""#;
    let result: Result<Player, _> = serde_json::from_str(json);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Invalid player string"));
}

#[test]
fn test_player_serialization() {
    assert_eq!(serde_json::to_string(&Player::X).unwrap(), "\"X\"");
    assert_eq!(serde_json::to_string(&Player::O).unwrap(), "\"O\"");
    assert_eq!(serde_json::to_string(&Player::None).unwrap(), "\" \"");
}


#[test]
fn test_player_debug() {
    assert_eq!(format!("{:?}", Player::X), "X");
    assert_eq!(format!("{:?}", Player::O), "O");
    assert_eq!(format!("{:?}", Player::None), "None");
}

#[test]
fn test_player_display_fmt() {
    assert_eq!(format!("{}", Player::X), "X");
    assert_eq!(format!("{}", Player::O), "O");
    assert_eq!(format!("{}", Player::None), " ");
}


#[test]
fn test_player_clone() {
    let p = Player::X;
    let p2 = p.clone();
    assert_eq!(p, p2);
}

#[test]
fn test_tictactoe_debug() {
    // 初期状態のデバッグ出力
    let game = TicTacToe::new(None, None, None);
    let debug_str = format!("{:?}", game);
    assert!(debug_str.contains("TicTacToe"));
    assert!(debug_str.contains("human_player: None"));
    assert!(debug_str.contains("winner: None"));

    // 決着がついた状態のデバッグ出力 (WinnerLine, WinnerなどがSomeの場合)
    let mut game_finished = TicTacToe::new(None, None, None);
    game_finished.board = [
        [Player::X, Player::X, Player::X],
        [Player::O, Player::O, Player::None],
        [Player::None, Player::None, Player::None],
    ];
    game_finished.game_over = true;
    game_finished.winner = Some(Player::X);
    game_finished.winner_line = Some([(0, 0), (0, 1), (0, 2)]);
    game_finished.human_player = Some(Player::X);
    
    let debug_str_finished = format!("{:?}", game_finished);
    assert!(debug_str_finished.contains("winner: Some(X)"));
    assert!(debug_str_finished.contains("winner_line: Some(["));
    assert!(debug_str_finished.contains("human_player: Some(X)"));
}

#[test]
fn test_get_current_agent_none() {
    // Game with no agents and current player set to None
    let mut game = TicTacToe::new(None, None, None);
    game.current_player = Player::None;
    assert!(game.get_current_agent().is_none());
}

#[test]
fn test_check_game_state_no_winner_not_full() {
    // Board with no winner and not full
    let mut game = TicTacToe::new(None, None, None);
    game.board = [
        [Player::X, Player::None, Player::None],
        [Player::None, Player::O, Player::None],
        [Player::None, Player::None, Player::None],
    ];
    game.check_game_state();
    assert!(!game.game_over);
    assert_eq!(game.winner, None);
}



#[test]
fn test_tictactoe_clone() {
    // Agentを持つゲームを作成してCloneをテスト
    let agent_x = Box::new(agents::RandomAgent::new(Player::X));
    let agent_o = Box::new(agents::RandomAgent::new(Player::O));
    let mut game = TicTacToe::new(Some(agent_x), Some(agent_o), Some(Player::O));
    
    let cloned_game = game.clone();

    // 値が正しくコピーされているか
    assert_eq!(game.board, cloned_game.board);
    assert_eq!(game.current_player, cloned_game.current_player);
    
    // Agentが正しくクローンされているか (Deep Copy)
    assert!(cloned_game.agent_x.is_some());
    assert!(cloned_game.agent_o.is_some());
    
    // クローン元の状態を変更してもクローン先に影響しないか
    game.current_player = Player::O;
    assert_eq!(cloned_game.current_player, Player::X);
}
