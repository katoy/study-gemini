// rust/tic_tac_toe_server_rust/src/agents.rs

#![allow(unused_imports)] // anyhow の unused import 警告を無視

use async_trait::async_trait;
use crate::game_logic::{Board, Move, Player};
use rand::seq::SliceRandom; // ランダムエージェント用
use anyhow::{Result, anyhow};
use std::collections::HashMap; // PerfectAgent, QLearningAgent用
use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;
// use serde::{Deserialize, Serialize}; // ダミーエージェントでは不要
// use reqwest; // ダミーエージェントでは不要
// use regex::Regex; // ダミーエージェントでは不要
use log::{info, warn, error, debug}; // ロギング
use rand::{Rng, thread_rng}; // QLearningAgentの乱数生成用


//==============================================================================
// Agent Trait (BaseAgent相当)
//==============================================================================

#[async_trait]
pub trait Agent: Send + Sync {
    fn get_player(&self) -> Player;
    async fn get_move(&self, board: &Board) -> Result<Option<Move>>;
    fn box_clone(&self) -> Box<dyn Agent + Send + Sync>; // Cloneメソッドを追加
}




//==============================================================================
// HumanAgent (GameManagerから参照されるが、実体は存在しないためダミー)
//==============================================================================
#[derive(Debug, Clone)]
pub struct HumanAgent {
    player: Player,
}

impl HumanAgent {
    pub fn new(player: Player) -> Self {
        HumanAgent { player }
    }
}

#[async_trait]
impl Agent for HumanAgent {
    fn get_player(&self) -> Player {
        self.player.clone()
    }
    async fn get_move(&self, _board: &Board) -> Result<Option<Move>> {
        Ok(None)
    }
    fn box_clone(&self) -> Box<dyn Agent + Send + Sync> { // box_clone を実装
        Box::new(self.clone())
    }
}


//==============================================================================
// RandomAgent
//==============================================================================

#[derive(Debug, Clone)]
pub struct RandomAgent {
    player: Player,
}

impl RandomAgent {
    pub fn new(player: Player) -> Self {
        RandomAgent { player }
    }
}

#[async_trait]
impl Agent for RandomAgent {
    fn get_player(&self) -> Player {
        self.player.clone()
    }

    async fn get_move(&self, board: &Board) -> Result<Option<Move>> {
        let mut available_moves = Vec::new();
        for r in 0..3 {
            for c in 0..3 {
                if board[r][c] == Player::None {
                    available_moves.push((r, c));
                }
            }
        }

        if available_moves.is_empty() {
            Ok(None)
        } else {
            let mut rng = rand::thread_rng();
            Ok(available_moves.choose(&mut rng).copied())
        }
    }
    fn box_clone(&self) -> Box<dyn Agent + Send + Sync> { // box_clone を実装
        Box::new(self.clone())
    }
}