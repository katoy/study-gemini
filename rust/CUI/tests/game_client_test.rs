use cui::game_client::GameClient;
use cui::models::{Agents, ErrorDetail, GameState};
use httpmock::prelude::*;

#[tokio::test]
async fn test_get_available_agents_success() {
    let server = MockServer::start();
    let agents_response = Agents {
        agents: vec!["Human".to_string(), "Random".to_string()],
    };

    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&agents_response);
    });

    let mut client = GameClient::new(server.base_url());
    let agents = client.get_available_agents().await.unwrap();

    assert_eq!(agents, vec!["Human", "Random"]);
    // Test caching
    let agents_cached = client.get_available_agents().await.unwrap();
    assert_eq!(agents_cached, vec!["Human", "Random"]);
}

#[tokio::test]
async fn test_get_available_agents_server_error() {
    let server = MockServer::start();

    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(500);
    });

    let mut client = GameClient::new(server.base_url());
    // On error, it should return the fallback list
    let agents = client.get_available_agents().await.unwrap();

    let fallback_agents = vec![
        "Human",
        "Random",
        "Minimax",
        "Database",
        "QLearning",
        "Perfect",
    ];
    assert_eq!(agents, fallback_agents);
}

fn mock_game_state() -> GameState {
    GameState {
        board: vec![vec![" ".to_string(); 3]; 3],
        current_player: "X".to_string(),
        game_over: false,
        winner: None,
    }
}

#[tokio::test]
async fn test_start_game_success() {
    let server = MockServer::start();
    let game_state_response = mock_game_state();

    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&game_state_response);
    });

    let client = GameClient::new(server.base_url());
    let game_state = client.start_game("X", "Human", "Random").await.unwrap();

    assert_eq!(game_state.board, game_state_response.board);
    assert_eq!(game_state.current_player, "X");
}

#[tokio::test]
async fn test_start_game_no_human() {
    let server = MockServer::start();
    let game_state_response = GameState {
        board: vec![vec![" ".to_string(); 3]; 3],
        current_player: "X".to_string(),
        game_over: false,
        winner: None,
    };

    server.mock(|when, then| {
        when.method(POST).path("/game/start")
            .json_body_obj(&serde_json::json!({
                "human_player_symbol": null, // Expect null
                "player_x_type": "Random",
                "player_o_type": "Minimax"
            }));
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&game_state_response);
    });

    let client = GameClient::new(server.base_url());
    // Pass empty string for human_player_symbol
    let game_state = client.start_game("", "Random", "Minimax").await.unwrap();
    
    assert_eq!(game_state.board, game_state_response.board);
}

#[tokio::test]
async fn test_make_move_success() {
    let server = MockServer::start();
    let game_state_response = mock_game_state();

    server.mock(|when, then| {
        when.method(POST).path("/game/move");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&game_state_response);
    });

    let client = GameClient::new(server.base_url());
    let game_state = client.make_move(1, 1).await.unwrap();

    assert_eq!(game_state.board, game_state_response.board);
}

#[tokio::test]
async fn test_get_game_status_success() {
    let server = MockServer::start();
    let game_state_response = mock_game_state();

    server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&game_state_response);
    });

    let client = GameClient::new(server.base_url());
    let game_state = client.get_game_status().await.unwrap();

    assert_eq!(game_state.board, game_state_response.board);
}

#[tokio::test]
async fn test_send_request_error_with_detail() {
    let server = MockServer::start();
    let error_response = ErrorDetail {
        detail: "Invalid move".to_string(),
    };

    server.mock(|when, then| {
        when.method(POST).path("/game/move");
        then.status(400)
            .header("content-type", "application/json")
            .json_body_obj(&error_response);
    });

    let client = GameClient::new(server.base_url());
    let result = client.make_move(0, 0).await;

    assert!(result.is_err());
    let error = result.err().unwrap();
    assert!(error
        .to_string()
        .contains("HTTP Error 400 Bad Request: Invalid move"));
}

#[tokio::test]
async fn test_send_request_error_no_detail() {
    let server = MockServer::start();

    server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(404);
    });

    let client = GameClient::new(server.base_url());
    let result = client.get_game_status().await;

    assert!(result.is_err());
    let error = result.err().unwrap();
    assert!(error.to_string().contains("HTTP Error 404 Not Found"));
}

#[tokio::test]
async fn test_get_available_agents_timeout() {
    let server = MockServer::start();

    // Mock the server to cause a timeout
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        // Simulate a delay longer than the client's timeout
        then.status(200)
            .body("")
            .delay(std::time::Duration::from_secs(2));
    });

    let mut client = GameClient::with_client(
        server.base_url(),
        reqwest::Client::builder()
            .timeout(std::time::Duration::from_millis(100))
            .build()
            .unwrap(),
    );

    let result = client.get_available_agents().await;
    assert!(result.is_ok()); // get_available_agents has fallback, so it should be Ok
    let agents = result.unwrap();
    let fallback_agents = vec![
        "Human",
        "Random",
        "Minimax",
        "Database",
        "QLearning",
        "Perfect",
    ];
    assert_eq!(agents, fallback_agents);
}

#[tokio::test]
async fn test_get_available_agents_invalid_json_response() {
    let server = MockServer::start();

    // Mock the server to return invalid JSON
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200).body("this is not json");
    });

    let mut client = GameClient::new(server.base_url());
    let result = client.get_available_agents().await;
    assert!(result.is_ok()); // get_available_agents has fallback, so it should be Ok
    let agents = result.unwrap();
    let fallback_agents = vec![
        "Human",
        "Random",
        "Minimax",
        "Database",
        "QLearning",
        "Perfect",
    ];
    assert_eq!(agents, fallback_agents);
}
