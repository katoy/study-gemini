// rust/tic_tac_toe_server_rust/src/server.rs

use actix_web::{web, HttpResponse};
// use actix_cors::Cors; // main.rs に移動
use std::sync::Arc;
use log::{error, info}; // info を追加
use anyhow::Result;
use utoipa::OpenApi; // 追加

use crate::game_logic::{TicTacToe, Player};
use crate::schemas::{StartGameRequest, BoardState, MoveRequest, AvailableAgentsResponse, ErrorResponse};
use crate::agents::{Agent, RandomAgent};
use crate::agents;

// API定義
#[derive(OpenApi)]
#[openapi(
    paths(
        start_game_handler,
        get_game_status_handler,
        make_move_handler,
        get_available_agents_handler,
    ),
    components(
        schemas(
            StartGameRequest,
            BoardState,
            MoveRequest,
            AvailableAgentsResponse,
            ErrorResponse,
            Player // Enumもスキーマとして認識させる
        )
    ),
    tags(
        (name = "Tic Tac Toe", description = "三目並べゲームのAPI")
    )
)]
pub struct ApiDoc;

type AgentFactory = Box<dyn Fn(Player, Option<&str>) -> Result<Option<Box<dyn agents::Agent + Send + Sync>>> + Send + Sync>;

// GameManager の定義
pub struct GameManager {
    game: Option<TicTacToe>,
    agent_display_names: Vec<String>,
    // エージェントのインスタンスを保持するための HashMap
    // キー: エージェント名, 値: Box<dyn Agent> (トレイトオブジェクト)
    agent_factories: std::collections::HashMap<String, AgentFactory>,
}

impl GameManager {
    pub fn new() -> Self {
        let mut agent_display_names = Vec::new();
        let mut agent_factories: std::collections::HashMap<String, AgentFactory> = std::collections::HashMap::new();

        // HumanAgent を手動で追加
        agent_display_names.push("Human".to_string());
        agent_factories.insert(
            "Human".to_string(),
            Box::new(|_, _| Ok(None)) // Humanの場合はNoneを返す
        );

        // RandomAgent を手動で追加
        agent_display_names.push("Random".to_string());
        agent_factories.insert(
            "Random".to_string(),
            Box::new(|player, _| Ok(Some(Box::new(RandomAgent::new(player))))) // Optionでラップ
        );
        
        GameManager {
            game: None,
            agent_display_names,
            agent_factories,
        }
    }

    pub fn get_available_agents(&self) -> Vec<String> {
        self.agent_display_names.clone()
    }

    fn create_agent_instance(&self, agent_type: &str, player: Player, _file_path: Option<&str>) -> Result<Option<Box<dyn Agent + Send + Sync>>> {
        if let Some(factory) = self.agent_factories.get(agent_type) {
            factory(player, None)
        } else {
            Err(anyhow::anyhow!("Unknown agent type: {}", agent_type))
        }
    }

    async fn create_game_instance(&self, player_x_type: &str, player_o_type: &str, human_player_symbol: Option<Player>) -> Result<TicTacToe> {
        let agent_x = self.create_agent_instance(player_x_type, Player::X, None)?;
        let agent_o = self.create_agent_instance(player_o_type, Player::O, None)?;
        
        let game = TicTacToe::new(agent_x, agent_o, human_player_symbol);
        
        Ok(game)
    }

    pub async fn start_new_game(&mut self, request: StartGameRequest) -> Result<TicTacToe> {
        let game_instance = self.create_game_instance(
            &request.player_x_type,
            &request.player_o_type,
            request.human_player_symbol
        ).await?;
        self.game = Some(game_instance);
        self._make_agent_move_if_needed().await; // 最初のプレイヤーがエージェントの場合、手を打たせる
        Ok(self.game.clone().unwrap())
    }

    async fn _make_agent_move_if_needed(&mut self) {
        if self.game.is_none() {
            return;
        }
        let game = self.game.as_mut().unwrap(); // gameが存在することは is_none でチェック済み

        while !game.game_over && game.human_player != Some(game.current_player) {
            info!("_make_agent_move_if_needed: human_player={:?}, current_player={:?}, game_over={}",
                game.human_player, game.current_player, game.game_over);

            // 現在のプレイヤーがAIの場合
            if let Some(agent) = game.get_current_agent() {
                // Agentトレイトのget_moveはResult<Option<Move>>を返す
                match agent.get_move(&game.board).await {
                    Ok(Some((row, col))) => {
                        info!("AI ({:?}) chose move: ({}, {})", game.current_player, row, col);
                        // 手番を実行
                        if let Err(e) = game.make_move(row, col) {
                            error!("AI made an invalid move: {}", e);
                            break; // エラーが発生したらループを抜ける
                        }
                        // make_move内でswitch_playerが呼ばれているので、ここでは呼ばない
                    },
                    Ok(None) => {
                        // AIが手番を返さなかった場合 (例えば、引き分け)
                        game.check_game_state(); // ゲームの状態を更新
                        info!("AI ({:?}) returned no move. Game state checked.", game.current_player);
                        break;
                    },
                    Err(e) => {
                        error!("Error getting move from AI: {}", e);
                        break; // エラーが発生したらループを抜ける
                    }
                }
            } else {
                // Humanプレイヤーまたはエージェントが設定されていない場合 (should not happen in this loop branch)
                info!("_make_agent_move_if_needed: No agent found for current_player={:?}", game.current_player);
                break;
            }
        }
        info!("_make_agent_move_if_needed: Loop finished. human_player={:?}, current_player={:?}, game_over={}",
            game.human_player, game.current_player, game.game_over);
    }

    pub async fn make_player_move(&mut self, row: usize, col: usize) -> Result<TicTacToe> {
        let game = self.game.as_mut().ok_or_else(|| anyhow::anyhow!("Game not started"))?;

        // プレイヤーの手を打つ
        game.make_move(row, col)
            .map_err(|e| anyhow::anyhow!("{}", e))?;

        // AIの手番が続く場合、AIに手を打たせる (ここは make_move_handler に移動)
        // self._make_agent_move_if_needed().await; // この行は削除されているべき

        Ok(game.clone())
    }

    pub fn get_current_game_state(&self) -> Result<BoardState> {
        let game = self.game.as_ref().ok_or_else(|| anyhow::anyhow!("Game not started"))?;
        Ok(BoardState {
            board: game.board,
            current_player: game.current_player,
            winner: game.winner,
            winner_line: game.winner_line,
            game_over: game.game_over,
        })
    }
}

impl Default for GameManager {
    fn default() -> Self {
        Self::new()
    }
}

// Global GameManager instance is removed.

// DI 用の GameManager getter is removed.

// エンドポイントハンドラ
#[utoipa::path(
    post,
    path = "/start_game",
    request_body = StartGameRequest,
    responses(
        (status = 200, description = "新しいゲームが開始されました", body = BoardState),
        (status = 500, description = "ゲームの開始に失敗しました", body = ErrorResponse)
    ),
    tag = "Tic Tac Toe"
)]
pub async fn start_game_handler(
    req: web::Json<StartGameRequest>,
    game_manager_data: web::Data<Arc<tokio::sync::Mutex<GameManager>>>,
) -> HttpResponse {
    let request = req.into_inner(); // まずリクエストデータを取得

    let game_result = { // MutexGuard のスコープを限定
        let mut gm_locked = game_manager_data.lock().await;
        // start_new_game は &mut self を取るので、gm_locked を直接使う
        gm_locked.start_new_game(request).await // この await の前に gm_locked がドロップされる必要がある
    }; // ここで gm_locked がドロップされる

    match game_result { // デリファレンスしてメソッドを呼び出す
        Ok(game) => HttpResponse::Ok().json(BoardState {
            board: game.board,
            current_player: game.current_player,
            winner: game.winner,
            winner_line: game.winner_line,
            game_over: game.game_over,
        }),
        Err(e) => {
            error!("Failed to start new game: {}", e);
            HttpResponse::InternalServerError().json(ErrorResponse { detail: format!("Error: {}", e) })
        },
    }
}

#[utoipa::path(
    get,
    path = "/game_status",
    responses(
        (status = 200, description = "現在のゲームの状態を取得", body = BoardState),
        (status = 404, description = "ゲームが開始されていません", body = ErrorResponse)
    ),
    tag = "Tic Tac Toe"
)]
pub async fn get_game_status_handler(
    game_manager_data: web::Data<Arc<tokio::sync::Mutex<GameManager>>>,
) -> HttpResponse {
    let game_manager = game_manager_data.lock().await;
    match game_manager.get_current_game_state() { // デリファレンスしてメソッドを呼び出す
        Ok(board_state) => HttpResponse::Ok().json(board_state),
        Err(e) => {
            error!("Failed to get game status: {}", e);
            HttpResponse::NotFound().json(ErrorResponse { detail: format!("Error: {}", e) })
        },
    }
}

#[utoipa::path(
    post,
    path = "/make_move",
    request_body = MoveRequest,
    responses(
        (status = 200, description = "移動が正常に実行され、最新のゲーム状態が返されました", body = BoardState),
        (status = 400, description = "不正な移動です", body = ErrorResponse),
        (status = 500, description = "サーバーエラー", body = ErrorResponse)
    ),
    tag = "Tic Tac Toe"
)]
pub async fn make_move_handler(
    req: web::Json<MoveRequest>,
    game_manager_data: web::Data<Arc<tokio::sync::Mutex<GameManager>>>,
) -> HttpResponse {
    let (row, col) = (req.row, req.col);

    let make_move_result = { // MutexGuard のスコープを限定
        let mut gm_locked = game_manager_data.lock().await;
        gm_locked.make_player_move(row, col).await
    }; // ここで gm_locked がドロップされる

    match make_move_result {
        Ok(_) => {
            let board_state = { // MutexGuard のスコープを再度限定
                let mut gm_locked_after_move = game_manager_data.lock().await;
                gm_locked_after_move._make_agent_move_if_needed().await;
                gm_locked_after_move.get_current_game_state().map_err(|e| anyhow::anyhow!("{}", e))
            }; // ここで gm_locked_after_move がドロップされる

            match board_state {
                Ok(bs) => HttpResponse::Ok().json(bs),
                Err(e) => {
                    error!("Failed to get game status after AI move: {}", e);
                    HttpResponse::InternalServerError().json(format!("Error: {}", e))
                }
            }
        },
        Err(e) => {
            error!("Failed to make move: {}", e);
            HttpResponse::BadRequest().json(ErrorResponse {
                detail: e.to_string(),
            })
        },
    }
}

#[utoipa::path(
    get,
    path = "/available_agents",
    responses(
        (status = 200, description = "利用可能なエージェントのリスト", body = AvailableAgentsResponse)
    ),
    tag = "Tic Tac Toe"
)]
pub async fn get_available_agents_handler(
    game_manager_data: web::Data<Arc<tokio::sync::Mutex<GameManager>>>,
) -> HttpResponse {
    let game_manager = game_manager_data.lock().await;
    let agents = game_manager.get_available_agents();
    HttpResponse::Ok().json(AvailableAgentsResponse { agents })
}

// テスト用にグローバルなGameManagerをリセットする関数 is removed.