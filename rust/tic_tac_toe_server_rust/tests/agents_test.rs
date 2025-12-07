// rust/tic_tac_toe_server_rust/tests/agents_test.rs

#![allow(unused_imports)] // Board の unused import 警告を無視

use tic_tac_toe_server_rust::game_logic::{Board, Player, TicTacToe};
use tic_tac_toe_server_rust::agents::{Agent, HumanAgent, RandomAgent};

// Agentトレイトのテスト (get_player, box_clone)
#[tokio::test]
async fn test_human_agent_get_player_and_box_clone() {
    let agent = HumanAgent::new(Player::X);
    assert_eq!(agent.get_player(), Player::X);

    let cloned_agent = agent.box_clone();
    assert_eq!(cloned_agent.get_player(), Player::X);
}

#[tokio::test]
async fn test_random_agent_get_player_and_box_clone() {
    let agent = RandomAgent::new(Player::O);
    assert_eq!(agent.get_player(), Player::O);

    let cloned_agent = agent.box_clone();
    assert_eq!(cloned_agent.get_player(), Player::O);
}

#[tokio::test]
async fn test_agent_trait_box_clone_coverage() {
    let agent: Box<dyn Agent + Send + Sync> = Box::new(HumanAgent::new(Player::X));
    let cloned_agent = agent.box_clone(); // agent.clone() から agent.box_clone() に変更
    assert_eq!(cloned_agent.get_player(), Player::X);

    let random_agent: Box<dyn Agent + Send + Sync> = Box::new(RandomAgent::new(Player::O));
    let cloned_random_agent = random_agent.box_clone(); // random_agent.clone() から random_agent.box_clone() に変更
    assert_eq!(cloned_random_agent.get_player(), Player::O);
}


// HumanAgent のテスト
#[tokio::test]
async fn test_human_agent_get_move() {
    let agent = HumanAgent::new(Player::X);
    let board = [[Player::None; 3]; 3];
    let result = agent.get_move(&board).await;
    assert!(result.is_ok());
    assert!(result.unwrap().is_none()); // HumanAgentは手番を返さない
}


// RandomAgent のテスト
#[tokio::test]
async fn test_random_agent_get_move_empty_board() {
    let agent = RandomAgent::new(Player::O);
    let board = [[Player::None; 3]; 3];
    let result = agent.get_move(&board).await;
    assert!(result.is_ok());
    let chosen_move = result.unwrap();
    assert!(chosen_move.is_some());

    let (row, col) = chosen_move.unwrap();
    assert!(row < 3 && col < 3); // 範囲内であること
    // TicTacToeのget_available_movesを使って有効な手であることを確認
    let game = TicTacToe::new(None, None, None);
    let available_moves = game.get_available_moves();
    assert!(available_moves.contains(&(row, col)));
}

#[tokio::test]
async fn test_random_agent_get_move_partial_board() {
    let agent = RandomAgent::new(Player::X);
    let mut board = [[Player::None; 3]; 3];
    board[0][0] = Player::O;
    board[1][1] = Player::X;

    let result = agent.get_move(&board).await;
    assert!(result.is_ok());
    let chosen_move = result.unwrap();
    assert!(chosen_move.is_some());

    let (row, col) = chosen_move.unwrap();
    assert!(board[row][col] == Player::None); // 空のマスに手番を打つこと
}

#[tokio::test]
async fn test_random_agent_get_move_full_board() {
    let agent = RandomAgent::new(Player::O);
    let board = [
        [Player::X, Player::O, Player::X],
        [Player::O, Player::X, Player::O],
        [Player::O, Player::X, Player::O],
    ];
    let result = agent.get_move(&board).await;
    assert!(result.is_ok());
    assert!(result.unwrap().is_none()); // フルボードでは手番を返さない
}

#[tokio::test]
async fn test_random_agent_get_move_empty_board_explicit() {
    let agent = RandomAgent::new(Player::O);
    // ボードは空だが、全てのマスが埋まっているかのように見せかける
    let board = [
        [Player::X, Player::O, Player::X],
        [Player::O, Player::X, Player::O],
        [Player::X, Player::O, Player::X],
    ]; // 全てのマスが埋まっているボード

    let result = agent.get_move(&board).await;
    assert!(result.is_ok());
    assert!(result.unwrap().is_none()); // available_moves が空なので None を返す
}
