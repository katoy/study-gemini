
use actix_web::{test, App, web};
use std::sync::Arc;
use tic_tac_toe_server_rust::{
    game_logic::Player,
    schemas::{StartGameRequest, MoveRequest, BoardState, AvailableAgentsResponse},
    configure_app,
    server,
};

#[actix_web::test]
async fn test_get_available_agents() {
    let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
    let app = test::init_service(
        App::new()
            .app_data(game_manager.clone())
            .configure(configure_app)
    ).await;

    let req = test::TestRequest::get().uri("/agents").to_request();
    let resp: AvailableAgentsResponse = test::call_and_read_body_json(&app, req).await;

    assert_eq!(resp.agents, vec!["Human", "Random"]);
}

#[actix_web::test]
async fn test_game_flow() {
    let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
    let app = test::init_service(
        App::new()
            .app_data(game_manager.clone())
            .configure(configure_app)
    ).await;

    // 1. Start a new game
    let start_req = StartGameRequest {
        player_x_type: "Human".to_string(),
        player_o_type: "Human".to_string(),
        human_player_symbol: Some(Player::X),
    };
    let req = test::TestRequest::post()
        .uri("/game/start")
        .set_json(&start_req)
        .to_request();
    let resp: BoardState = test::call_and_read_body_json(&app, req).await;

    assert_eq!(resp.current_player, Player::X);
    assert!(!resp.game_over);
    assert_eq!(resp.board[0][0], Player::None);


    // 2. Get game status
    let req = test::TestRequest::get().uri("/game/status").to_request();
    let resp: BoardState = test::call_and_read_body_json(&app, req).await;

    assert_eq!(resp.current_player, Player::X);

    // 3. Make a valid move
    let move_req = MoveRequest { row: 0, col: 0 };
    let req = test::TestRequest::post()
        .uri("/game/move")
        .set_json(&move_req)
        .to_request();
    let resp: BoardState = test::call_and_read_body_json(&app, req).await;
    
    assert_eq!(resp.board[0][0], Player::X);
    assert_eq!(resp.current_player, Player::O);


    // 4. Make an invalid move
    let move_req = MoveRequest { row: 0, col: 0 }; // Same cell
    let req = test::TestRequest::post()
        .uri("/game/move")
        .set_json(&move_req)
        .to_request();
    let resp = test::call_service(&app, req).await;

    assert_eq!(resp.status(), 400);
}

#[actix_web::test]
async fn test_ai_game_flow() {
    let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
    let app = test::init_service(
        App::new()
            .app_data(game_manager.clone())
            .configure(configure_app)
    ).await;

    // 1. Start a new game: Human (X) vs. AI (O)
    let start_req = StartGameRequest {
        player_x_type: "Human".to_string(),
        player_o_type: "Random".to_string(),
        human_player_symbol: Some(Player::X),
    };
    let req = test::TestRequest::post()
        .uri("/game/start")
        .set_json(&start_req)
        .to_request();
    let resp: BoardState = test::call_and_read_body_json(&app, req).await;

    // AI does not move first if it's O
    assert_eq!(resp.current_player, Player::X);
    let moves_on_board = resp.board.iter().flatten().filter(|&&p| p != Player::None).count();
    assert_eq!(moves_on_board, 0);

    // 2. Human makes a move
    let move_req = MoveRequest { row: 0, col: 0 };
    let req = test::TestRequest::post()
        .uri("/game/move")
        .set_json(&move_req)
        .to_request();
    let resp: BoardState = test::call_and_read_body_json(&app, req).await;

    // After human's move, it should be human's turn again (as AI plays instantly)
    // or the game could be over.
    // The AI's move is automatic, so the board should have 2 moves.
    let moves_on_board = resp.board.iter().flatten().filter(|&&p| p != Player::None).count();
    assert_eq!(moves_on_board, 2);
    assert_eq!(resp.board[0][0], Player::X); // Human's move
    assert_eq!(resp.current_player, Player::X); // Back to human's turn
}

#[actix_web::test]
async fn test_start_game_handler_error_invalid_agent_type() {
    let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
    let app = test::init_service(
        App::new()
            .app_data(game_manager.clone())
            .configure(configure_app)
    ).await;

    let start_req = StartGameRequest {
        player_x_type: "UnknownAgent".to_string(), // 存在しないエージェントタイプ
        player_o_type: "Human".to_string(),
        human_player_symbol: Some(Player::X),
    };
    let req = test::TestRequest::post()
        .uri("/game/start")
        .set_json(&start_req)
        .to_request();
    let resp = test::call_service(&app, req).await;

    assert_eq!(resp.status(), 500); // Internal Server Error
    let body = test::read_body(resp).await;
    assert!(String::from_utf8_lossy(&body).contains(r#"detail":"Error: Unknown agent type: UnknownAgent"#));
}

#[actix_web::test]
async fn test_get_game_status_handler_error_no_game() {
    let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
    let app = test::init_service(
        App::new()
            .app_data(game_manager.clone())
            .configure(configure_app)
    ).await;

    let req = test::TestRequest::get().uri("/game/status").to_request();
    let resp = test::call_service(&app, req).await;

    assert_eq!(resp.status(), 404); // Not Found
    let body = test::read_body(resp).await; // この行を追加
    assert!(String::from_utf8_lossy(&body).contains(r#"detail":"Error: Game not started"#));
}

#[actix_web::test]
async fn test_make_move_handler_error_no_game() {
    let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
    let app = test::init_service(
        App::new()
            .app_data(game_manager.clone())
            .configure(configure_app)
    ).await;

    let move_req = MoveRequest { row: 0, col: 0 };
    let req = test::TestRequest::post()
        .uri("/game/move")
        .set_json(&move_req)
        .to_request();
    let resp = test::call_service(&app, req).await;

    assert_eq!(resp.status(), 400); // Bad Request
    let body = test::read_body(resp).await;
    assert!(String::from_utf8_lossy(&body).contains(r#"detail":"Game not started"#));
}
