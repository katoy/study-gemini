// rust/tic_tac_toe_server_rust/src/server.rs

use actix_web::{web, HttpResponse};
// use actix_cors::Cors; // main.rs に移動
use std::sync::Arc;
use log::{error, info}; // info を追加
use anyhow::Result;
use utoipa::OpenApi; // 追加

use crate::game_logic::{TicTacToe, Player};
use crate::schemas::{StartGameRequest, BoardState, MoveRequest, AvailableAgentsResponse, ErrorResponse, HTTPValidationError, ValidationError};
use crate::agents::{Agent, RandomAgent};
use crate::agents;

// API定義
#[derive(OpenApi)]
#[openapi(

    components(
        schemas(
            StartGameRequest,
            BoardState,
            MoveRequest,
            AvailableAgentsResponse,
            HTTPValidationError,
            ValidationError,
            Player // Enumもスキーマとして認識させる
        )
    ),
    tags(
        (name = "Tic Tac Toe", description = "Tic Tac Toe game API")
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
        info!("create_agent_instance: Creating agent of type '{}' for player {:?}", agent_type, player);
        if let Some(factory) = self.agent_factories.get(agent_type) {
            factory(player, None)
        } else {
            error!("create_agent_instance: Unknown agent type: {}", agent_type);
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
        info!("start_new_game: self.game set. Human player: {:?}, Current player: {:?}", self.game.as_ref().unwrap().human_player, self.game.as_ref().unwrap().current_player);
        self._make_agent_move_if_needed().await; // 最初のプレイヤーがエージェントの場合、手を打たせる
        info!("start_new_game: After _make_agent_move_if_needed. Human player: {:?}, Current player: {:?}", self.game.as_ref().unwrap().human_player, self.game.as_ref().unwrap().current_player);
        Ok(self.game.clone().unwrap())
    }

    async fn _make_agent_move_if_needed(&mut self) {
        info!("_make_agent_move_if_needed: Function entered.");
        if self.game.is_none() {
            info!("_make_agent_move_if_needed: self.game is None, returning.");
            return;
        }
        let game = self.game.as_mut().unwrap(); // gameが存在することは is_none でチェック済み

        while !game.game_over && game.human_player != Some(game.current_player) {
            info!("_make_agent_move_if_needed: While loop condition check: !game.game_over={}, game.human_player != Some(game.current_player)={}",
                !game.game_over, game.human_player != Some(game.current_player));
            info!("_make_agent_move_if_needed: START LOOP - human_player={:?}, current_player={:?}, game_over={}",
                game.human_player, game.current_player, game.game_over);
            info!("_make_agent_move_if_needed: Board before AI move: {:?}", game.board);

            // 現在のプレイヤーがAIの場合
            if let Some(agent) = game.get_current_agent() {
                info!("_make_agent_move_if_needed: Agent {:?} is getting move.", agent.get_player());
                // Agentトレイトのget_moveはResult<Option<Move>>を返す
                match agent.get_move(&game.board).await {
                    Ok(Some((row, col))) => {
                        info!("_make_agent_move_if_needed: AI ({:?}) chose move: ({}, {})", game.current_player, row, col);
                        // 手番を実行
                        if let Err(e) = game.make_move(row, col) {
                            error!("_make_agent_move_if_needed: AI made an invalid move: {}", e);
                            break; // エラーが発生したらループを抜ける
                        }
                        info!("_make_agent_move_if_needed: Board after AI move: {:?}", game.board);
                    },
                    Ok(None) => {
                        // AIが手番を返さなかった場合 (例えば、引き分け)
                        info!("_make_agent_move_if_needed: AI ({:?}) returned no move (e.g., draw).", game.current_player);
                        game.check_game_state(); // ゲームの状態を更新
                        break;
                    },
                    Err(e) => {
                        error!("_make_agent_move_if_needed: Error getting move from AI: {}", e);
                        break; // エラーが発生したらループを抜ける
                    }
                }
            } else {
                // Humanプレイヤーまたはエージェントが設定されていない場合 (should not happen in this loop branch)
                info!("_make_agent_move_if_needed: No agent found for current_player={:?}. Breaking loop.", game.current_player);
                break;
            }
            info!("_make_agent_move_if_needed: END LOOP - human_player={:?}, current_player={:?}, game_over={}",
                game.human_player, game.current_player, game.game_over);
        }
    }

    pub async fn make_agent_move(&mut self) -> Result<BoardState> {
        if self.game.is_none() {
            return Err(anyhow::anyhow!("Game not started"));
        }
        self._make_agent_move_if_needed().await;
        self.get_current_game_state()
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
    path = "/game/start",
    request_body = StartGameRequest,
    responses(
        (status = 200, description = "Successful Response", body = BoardState),
        (status = 422, description = "Validation Error", body = HTTPValidationError)
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

    match game_result {
        Ok(game) => {
            info!("start_game_handler: Sending game state to client: board={:?}, current_player={:?}", game.board, game.current_player);
            HttpResponse::Ok().json(BoardState {
                board: game.board,
                current_player: game.current_player,
                winner: game.winner,
                winner_line: game.winner_line,
                game_over: game.game_over,
            })
        },
        Err(e) => {
            error!("Failed to start new game: {}", e);
            // Convert anyhow::Error to HTTPValidationError for 422
            let validation_error = ValidationError {
                loc: vec!["request".to_string()], // Generic location
                msg: format!("{}", e),
                r#type: "value_error".to_string(), // Generic type
            };
            HttpResponse::UnprocessableEntity().json(HTTPValidationError {
                detail: vec![validation_error],
            })
        },
    }
}

#[utoipa::path(
    get,
    path = "/game_status",
    responses(
        (status = 200, description = "Successful Response", body = BoardState)
    ),
    tag = "Tic Tac Toe"
)]
pub async fn get_game_status_handler(
    game_manager_data: web::Data<Arc<tokio::sync::Mutex<GameManager>>>,
) -> HttpResponse {
    let game_manager = game_manager_data.lock().await;
    match game_manager.get_current_game_state() { // デリファレンスしてメソッドを呼び出す
        Ok(board_state) => HttpResponse::Ok().json(board_state),
        Err(_) => {
            // If no game is in progress, return a default/empty BoardState as per Python API expectation (no 404)
            HttpResponse::Ok().json(BoardState {
                board: [[Player::None; 3]; 3],
                current_player: Player::X, // Default starting player
                winner: None,
                winner_line: None,
                game_over: true, // If no game, then it's effectively over
            })
        },
    }
}

#[utoipa::path(
    post,
    path = "/game/move",
    request_body = MoveRequest,
    responses(
        (status = 200, description = "Successful Response", body = BoardState),
        (status = 422, description = "Validation Error", body = HTTPValidationError)
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
                    HttpResponse::InternalServerError().json(ErrorResponse { detail: format!("Error: {}", e) })
                }
            }
        },
        Err(e) => {
            error!("Failed to make move: {}", e);
            let validation_error = ValidationError {
                loc: vec!["row".to_string(), "col".to_string()], // Generic location for move
                msg: format!("{}", e),
                r#type: "value_error".to_string(),
            };
            HttpResponse::UnprocessableEntity().json(HTTPValidationError {
                detail: vec![validation_error],
            })
        },
    }
}



#[utoipa::path(
    get,
    path = "/agents",
    responses(
        (status = 200, description = "Successful Response", body = AvailableAgentsResponse)
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

    #[tokio::test]
    async fn test_make_agent_move_no_game() {
        // GIVEN: A GameManager with no game started
        let mut gm = GameManager::new();

        // WHEN: make_agent_move is called
        let result = gm.make_agent_move().await;

        // THEN: It should return an error
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().to_string(), "Game not started");
    }

    #[tokio::test]
    async fn test_make_agent_move_with_game() {
        // GIVEN: A GameManager with a game started (X is Random, O is Human)
        let mut gm = GameManager::new();
        let start_req = StartGameRequest {
            human_player_symbol: Some(Player::O), // Oが人間プレイヤー
            player_x_type: "Random".to_string(), // XがAI
            player_o_type: "Human".to_string(),
        };
        gm.start_new_game(start_req).await.expect("Failed to start game");

        // Xが最初のMoveを行い、Current PlayerがOになっているはず
        let initial_board = gm.game.as_ref().unwrap().board;
        assert_eq!(gm.game.as_ref().unwrap().current_player, Player::O);
        assert!(!gm.game.as_ref().unwrap().game_over); // ゲームが終了していないことを確認

        // WHEN: make_agent_move is called (Current Playerが人間なので、何も起きないはず)
        let result = gm.make_agent_move().await;

        // THEN: The result should be successful, but the board should not have changed
        assert!(result.is_ok());
        let board_state_after_no_move = result.unwrap();
        assert_eq!(board_state_after_no_move.board, initial_board); // ボードが変化していないことを確認
        assert_eq!(board_state_after_no_move.current_player, Player::O); // プレイヤーも変わらない

        // FORCED: Current PlayerをAIに変更して、AIが動くことを確認するシナリオ
        // テストのためにCurrent Playerを一時的にXに戻す
        gm.game.as_mut().unwrap().current_player = Player::X;
        let board_before_ai_move = gm.game.as_ref().unwrap().board;
        assert_eq!(gm.game.as_ref().unwrap().current_player, Player::X);

        // WHEN: make_agent_move is called (Xが手を打つ)
        let result_ai_move = gm.make_agent_move().await;

        // THEN: The move should be successful, and the board should have changed
        assert!(result_ai_move.is_ok());
        let board_state_after_ai_move = result_ai_move.unwrap();
        assert_ne!(board_state_after_ai_move.board, board_before_ai_move); // ボードが変化していることを確認
        assert_eq!(board_state_after_ai_move.current_player, Player::O); // Xが一手打ったのでOがCurrent
    }

    #[tokio::test]
    async fn test_make_agent_move_game_over() {
        // GIVEN: A GameManager with a game that is already over
        let mut gm = GameManager::new();
        let start_req = StartGameRequest {
            human_player_symbol: Some(Player::O), // Oが人間プレイヤー
            player_x_type: "Random".to_string(), // XがAI
            player_o_type: "Human".to_string(),
        };
        gm.start_new_game(start_req).await.expect("Failed to start game");

        // Manually make the game over for testing purposes
        let game = gm.game.as_mut().unwrap();
        game.game_over = true;
        game.winner = Some(Player::X); // Simulate X winning
        
        // WHEN: make_agent_move is called
        let result = gm.make_agent_move().await;

        // THEN: The board state should be returned, but no move should be made (as game is over)
        assert!(result.is_ok());
        let board_state = result.unwrap();
        assert!(board_state.game_over);
        assert_eq!(board_state.winner, Some(Player::X));
        // No change in current player or board if already game over
        assert_eq!(board_state.current_player, Player::O); // Oのままであることを確認
    }
