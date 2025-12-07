// rust/tic_tac_toe_server_rust/src/game_logic.rs

use std::fmt;
use std::str::FromStr; // 追加
use serde::{Deserialize, Serialize};
use crate::agents; // 追加
use utoipa::ToSchema; // 追加

#[derive(Debug, Clone, Copy, PartialEq, ToSchema)] // ToSchema を追加
pub enum Player {
    X,
    O,
    None, // 空のセルや勝者がいない場合
}

// ... (fmt::Display, Player::from_str, Player::opponent, Board, Move, WinnerLine)


// Player の手動 Serialize 実装
impl Serialize for Player {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

// Player の手動 Deserialize 実装
impl<'de> Deserialize<'de> for Player {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let s = String::deserialize(deserializer)?;
        s.parse().map_err(serde::de::Error::custom)
    }
}

impl fmt::Display for Player {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Player::X => write!(f, "X"),
            Player::O => write!(f, "O"),
            Player::None => write!(f, " "), // 空のセルはスペースで表示
        }
    }
}

impl FromStr for Player {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "X" => Ok(Player::X),
            "O" => Ok(Player::O),
            " " | "." | "" => Ok(Player::None),
            _ => Err(format!("Invalid player string: {}", s)),
        }
    }
}

impl Player {
    pub fn opponent(&self) -> Player {
        match self {
            Player::X => Player::O,
            Player::O => Player::X,
            Player::None => Player::None, // Noneの相手はNone
        }
    }
}

pub type Board = [[Player; 3]; 3];
pub type Move = (usize, usize);
pub type WinnerLine = Option<[(usize, usize); 3]>;


// #[derive(Debug, Clone)] // Debug と Clone を手動実装するため削除
pub struct TicTacToe {
    pub board: Board,
    pub current_player: Player,
    pub winner: Option<Player>,
    pub winner_line: WinnerLine,
    pub game_over: bool,
    pub agent_x: Option<Box<dyn agents::Agent + Send + Sync>>,
    pub agent_o: Option<Box<dyn agents::Agent + Send + Sync>>,
    pub human_player: Option<Player>,
}

impl fmt::Debug for TicTacToe {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("TicTacToe")
            .field("board", &self.board)
            .field("current_player", &self.current_player)
            .field("winner", &self.winner)
            .field("winner_line", &self.winner_line)
            .field("game_over", &self.game_over)
            .field("human_player", &self.human_player)
            // agent_x と agent_o は Debug を実装していないのでフィールドに含めない
            .finish()
    }
}

impl Clone for TicTacToe {
    fn clone(&self) -> Self {
        TicTacToe {
            board: self.board,
            current_player: self.current_player,
            winner: self.winner,
            winner_line: self.winner_line,
            game_over: self.game_over,
            agent_x: self.agent_x.as_ref().map(|agent| agent.box_clone()),
            agent_o: self.agent_o.as_ref().map(|agent| agent.box_clone()),
            human_player: self.human_player,
        }
    }
}


impl TicTacToe {
    pub fn new(
        agent_x: Option<Box<dyn agents::Agent + Send + Sync>>,
        agent_o: Option<Box<dyn agents::Agent + Send + Sync>>,
        human_player: Option<Player>,
    ) -> Self {
        TicTacToe {
            board: [[Player::None; 3]; 3],
            current_player: Player::X, // Xが先手
            winner: None,
            winner_line: None,
            game_over: false,
            agent_x,
            agent_o,
            human_player,
        }
    }

    pub fn make_move(&mut self, row: usize, col: usize) -> Result<(), String> {
        if self.game_over {
            return Err("Game is already over.".to_string());
        }
        if row >= 3 || col >= 3 {
            return Err("Move is out of board bounds.".to_string());
        }
        if self.board[row][col] != Player::None {
            return Err("Cell is already occupied.".to_string());
        }

        self.board[row][col] = self.current_player;
        self.check_game_state(); // 手を打った後にゲームの状態をチェック
        if !self.game_over { // ゲームオーバーでなければプレイヤーを切り替える
            self.switch_player();
        }
        Ok(())
    }

    pub fn switch_player(&mut self) {
        self.current_player = self.current_player.opponent();
    }

    pub fn check_game_state(&mut self) {
        let (winner_player, winner_coords) = TicTacToe::check_winner_logic(&self.board);

        if let Some(player) = winner_player {
            self.winner = Some(player);
            self.winner_line = winner_coords;
            self.game_over = true;
        } else if self.is_board_full() {
            self.winner = Some(Player::None); // 引き分け
            self.game_over = true;
        }
    }

    pub fn check_winner_logic(board: &Board) -> (Option<Player>, WinnerLine) {
        let lines: [[(usize, usize); 3]; 8] = [
            // Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            // Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            // Diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ];

        for line in &lines {
            let p1 = board[line[0].0][line[0].1];
            let p2 = board[line[1].0][line[1].1];
            let p3 = board[line[2].0][line[2].1];

            if p1 != Player::None && p1 == p2 && p2 == p3 {
                return (Some(p1), Some(*line));
            }
        }
        (None, None)
    }

    pub fn is_board_full(&self) -> bool {
        self.board.iter().all(|row| row.iter().all(|&cell| cell != Player::None))
    }

    pub fn get_available_moves(&self) -> Vec<Move> {
        let mut moves = Vec::new();
        for r in 0..3 {
            for c in 0..3 {
                if self.board[r][c] == Player::None {
                    moves.push((r, c));
                }
            }
        }
        moves
    }

    pub fn get_current_agent(&self) -> Option<&(dyn agents::Agent + Send + Sync)> {
        match self.current_player {
            Player::X => self.agent_x.as_deref(),
            Player::O => self.agent_o.as_deref(),
            Player::None => None,
        }
    }
}