// The main.rs file needs to be included as a module to be tested
// However, it contains a `main` function which is not allowed in a library crate.
// To solve this, we can use a conditional compilation flag.
// In main.rs, you would wrap the main function like this:
// #[cfg(not(test))]
// fn main() { ... }
// For now, we will test the public functions we refactored.

// Since the functions are in the main binary, we use `super::*` if this were a module,
// but for an integration-style test in the `tests` directory, we need to import the crate.
use cui::*;
use cui::game_client::GameClient;
use httpmock::prelude::*;

#[test]
fn test_get_play_again_choice() {
    let mut input = "y\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_play_again_choice(&mut input, &mut output).unwrap(), true);

    let mut input = "Y\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_play_again_choice(&mut input, &mut output).unwrap(), true);

    let mut input = "n\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_play_again_choice(&mut input, &mut output).unwrap(), false);

    let mut input = "yes\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_play_again_choice(&mut input, &mut output).unwrap(), false);

    let mut input = "\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_play_again_choice(&mut input, &mut output).unwrap(), false);
}

#[test]
fn test_get_player_symbol_choice() {
    let mut input = "x\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_player_symbol_choice(&mut input, &mut output).unwrap(), "X");

    let mut input = "O\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_player_symbol_choice(&mut input, &mut output).unwrap(), "O");
    
    // Test with extra whitespace
    let mut input = "  x  \n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_player_symbol_choice(&mut input, &mut output).unwrap(), "X");

    // Test looping with invalid input first
    let mut input = "z\nx\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_player_symbol_choice(&mut input, &mut output).unwrap(), "X");
}

#[test]
fn test_get_user_move() {
    let mut input = "5\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), Some((1, 1)));

    let mut input = "1\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), Some((0, 0)));

    let mut input = "9\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), Some((2, 2)));

    let mut input = "q\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), None);

    let mut input = "quit\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), None);

    // Test looping with invalid input
    let mut input = "10\ninvalid\n2\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), Some((0, 1)));
}

#[tokio::test]
async fn test_get_agent_type_choice() {
    // Start a mock server.
    let server = MockServer::start();

    // Create a mock for the /agents endpoint.
    let mock = server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "agents": ["Human", "Random", "Minimax"]
            }));
    });

    let mut client = GameClient::new(server.base_url());
    let mut input = "2\n".as_bytes(); // "Random"
    let mut output = Vec::new();
    let choice = get_agent_type_choice(&mut client, "X", &mut input, &mut output)
        .await
        .unwrap();

    // Assert that the mock was called.
    mock.assert();
    assert_eq!(choice, "Random");
}

#[tokio::test]
async fn test_get_agent_type_choice_invalid_input() {
    let server = MockServer::start();
    let mock = server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "agents": ["Human", "Random", "Minimax"]
            }));
    });

    let mut client = GameClient::new(server.base_url());
    let mut input = "4\ninvalid\n1\n".as_bytes(); // "Human"
    let mut output = Vec::new();
    let choice = get_agent_type_choice(&mut client, "O", &mut input, &mut output)
        .await
        .unwrap();

    mock.assert();
    assert_eq!(choice, "Human");
}

#[tokio::test]
async fn test_get_agent_type_choice_no_agents_fallback() {
    let server = MockServer::start();
    let mock = server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(500);
    });

    let mut client = GameClient::new(server.base_url());
    // Server fails, so it uses the fallback list.
    let mut input = "2\n".as_bytes(); // "Random" from fallback
    let mut output = Vec::new();
    let choice = get_agent_type_choice(&mut client, "X", &mut input, &mut output)
        .await
        .unwrap();

    mock.assert();
    assert_eq!(choice, "Random");
}

#[tokio::test]
async fn test_get_agent_type_choice_empty_agents() {
    let server = MockServer::start();
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": [] }));
    });

    let mut client = GameClient::new(server.base_url());
    let mut input = "".as_bytes(); // No input needed, it should return default
    let mut output = Vec::new();
    let choice = get_agent_type_choice(&mut client, "X", &mut input, &mut output)
        .await
        .unwrap();

    assert_eq!(choice, "Human");
}

#[tokio::test]
async fn test_play_single_game_human_vs_agent() {
    let server = MockServer::start();

    // Mock for get_available_agents
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "agents": ["Human", "Random"]
            }));
    });

    // Mock for start_game
    let start_game_mock = server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
                "current_player": "X",
                "game_over": false,
                "winner": null
            }));
    });

    // Mock for make_move (human)
    let make_move_mock = server.mock(|when, then| {
        when.method(POST).path("/game/move");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]],
                "current_player": "O",
                "game_over": false,
                "winner": null
            }));
    });

    // Mock for get_game_status (agent's turn)
    let agent_move_mock = server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [["X", " ", " "], [" ", "O", " "], [" ", " ", " "]],
                "current_player": "X",
                "game_over": true,
                "winner": "O" // Agent wins
            }));
    });

    let mut client = GameClient::new(server.base_url());
    // player symbol, agent for X, agent for O, human move
    let mut input = "X\n1\n2\n1\n".as_bytes(); 
    let mut output = Vec::new();
    let result = play_single_game(&mut client, &mut input, &mut output).await;

    assert!(result.is_ok());
    start_game_mock.assert();
    make_move_mock.assert();
    agent_move_mock.assert();
}

#[tokio::test]
async fn test_play_single_game_move_error() {
    let server = MockServer::start();

    // Mock for get_available_agents
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });

    // Mock for start_game
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
                "current_player": "X", "game_over": false, "winner": null
            }));
    });

    // Mock for make_move (human) - fails
    server.mock(|when, then| {
        when.method(POST).path("/game/move");
        then.status(400);
    });

    let mut client = GameClient::new(server.base_url());
    // symbol, agentX, agentO, move1 (invalid), quit
    let mut input = "X\n1\n2\n1\nq\n".as_bytes();
    let mut output = Vec::new();
    let result = play_single_game(&mut client, &mut input, &mut output).await;

    assert!(result.is_ok());
}

#[tokio::test]
async fn test_play_single_game_quit() {
    let server = MockServer::start();
    // Mocks...
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200).json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
            "current_player": "X", "game_over": false, "winner": null
        }));
    });

    let mut client = GameClient::new(server.base_url());
    // symbol, agentX, agentO, quit
    let mut input = "X\n1\n2\nq\n".as_bytes(); 
    let mut output = Vec::new();
    let result = play_single_game(&mut client, &mut input, &mut output).await;
    assert!(result.is_ok());
}

#[tokio::test]
async fn test_run_main_test_call() { // Renamed from test_run_cui_app
    let server = MockServer::start();

    // Mock for get_available_agents - always returns human and random
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "agents": ["Human", "Random"]
            }));
    });

    // Mock for start_game - always returns a fresh board
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
                "current_player": "X",
                "game_over": false,
                "winner": null
            }));
    });

    // Mock for make_move - always makes a move
    server.mock(|when, then| {
        when.method(POST).path("/game/move");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]],
                "current_player": "O",
                "game_over": false,
                "winner": null
            }));
    });

    // Mock for get_game_status - agent makes a move, leading to game over
    server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "board": [["X", " ", " "], [" ", "O", " "], [" ", " ", " "]],
                "current_player": "X",
                "game_over": true,
                "winner": "O" // Agent wins
            }));
    });

    let mut client = GameClient::new(server.base_url());
    // Simulate user input: player X, agent for X (Human), agent for O (Random), Human move (1), play again (n)
    let mut input = "X\n1\n2\n1\nn\n".as_bytes(); 
    let mut output = Vec::new(); // Capture stdout

    cui::run_main(&mut client, &mut input, &mut output).await; // Call cui::run_main

    let output_str = String::from_utf8(output).unwrap();
    assert!(output_str.contains("--- Start New Tic Tac Toe Game ---"));
    assert!(output_str.contains("Game over. Play again? (y/n): "));
    assert!(output_str.contains("Game Over: Player O wins!"));
}

#[tokio::test]
async fn test_run_main_play_single_game_error() { // Renamed from test_run_cui_app_play_single_game_error
    let server = MockServer::start();

    // Mock for get_available_agents - always returns human and random
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .header("content-type", "application/json")
            .json_body_obj(&serde_json::json!({
                "agents": ["Human", "Random"]
            }));
    });

    // Mock for start_game - always returns an error
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(500); // Internal server error
    });

    let mut client = GameClient::new(server.base_url());
    // Simulate user input: player X, agent for X (Human), agent for O (Random), play again (n)
    let mut input = "X\n1\n2\nn\n".as_bytes(); 
    let mut output = Vec::new(); // Capture stdout

    cui::run_main(&mut client, &mut input, &mut output).await; // Call cui::run_main

    let output_str = String::from_utf8(output).unwrap();
    assert!(output_str.contains("An error occurred during the game: HTTP Error 500"));
    assert!(output_str.contains("Game over. Play again? (y/n): "));
}