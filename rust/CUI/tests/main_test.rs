// The main.rs file needs to be included as a module to be tested
// However, it contains a `main` function which is not allowed in a library crate.
// To solve this, we can use a conditional compilation flag.
// In main.rs, you would wrap the main function like this:
// #[cfg(not(test))]
// fn main() { ... }
// For now, we will test the public functions we refactored.

// Since the functions are in the main binary, we use `super::*` if this were a module,
// but for an integration-style test in the `tests` directory, we need to import the crate.
use cui::game_client::GameClient;
use cui::*;
use httpmock::prelude::*;

use std::io;

struct CountingErrorWriter {
    writes_count: usize,
    writes_before_error: usize,
}

impl CountingErrorWriter {
    fn new(writes_before_error: usize) -> Self {
        CountingErrorWriter {
            writes_count: 0,
            writes_before_error,
        }
    }
}

impl io::Write for CountingErrorWriter {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        self.writes_count += 1;
        if self.writes_count > self.writes_before_error {
            Err(io::Error::other(
                "simulated write error",
            ))
        } else {
            Ok(buf.len())
        }
    }

    fn flush(&mut self) -> io::Result<()> {
        Ok(())
    }
}

struct ErrorReader;

impl io::Read for ErrorReader {
    fn read(&mut self, _buf: &mut [u8]) -> io::Result<usize> {
        Err(io::Error::other("simulated read error"))
    }
}

impl io::BufRead for ErrorReader {
    fn fill_buf(&mut self) -> io::Result<&[u8]> {
        Ok(&[])
    }
    fn consume(&mut self, _amt: usize) {}
    fn read_line(&mut self, _buf: &mut String) -> io::Result<usize> {
        Err(io::Error::other("simulated read error"))
    }
}

#[test]
fn test_get_play_again_choice() {
    let mut input = "y\n".as_bytes();
    let mut output = Vec::new();
    assert!(
        get_play_again_choice(&mut input, &mut output).unwrap()
    );

    let mut input = "Y\n".as_bytes();
    let mut output = Vec::new();
    assert!(
        get_play_again_choice(&mut input, &mut output).unwrap()
    );

    let mut input = "n\n".as_bytes();
    let mut output = Vec::new();
    assert!(
        !get_play_again_choice(&mut input, &mut output).unwrap()
    );

    let mut input = "yes\n".as_bytes();
    let mut output = Vec::new();
    assert!(
        !get_play_again_choice(&mut input, &mut output).unwrap()
    );

    let mut input = "\n".as_bytes();
    let mut output = Vec::new();
    assert!(
        !get_play_again_choice(&mut input, &mut output).unwrap()
    );
}

#[test]
fn test_get_play_again_choice_write_error() {
    let mut input = "y\n".as_bytes();
    let mut output = CountingErrorWriter::new(0); // Error on first write
    assert!(get_play_again_choice(&mut input, &mut output).is_err());
}

#[test]
fn test_get_play_again_choice_read_error() {
    let mut input = ErrorReader;
    let mut output = Vec::new();
    assert!(get_play_again_choice(&mut input, &mut output).is_err());
}

#[test]
fn test_get_play_again_choice_eof() {
    let mut input = "".as_bytes();
    let mut output = Vec::new();
    // EOF returns Ok(false)
    assert!(!get_play_again_choice(&mut input, &mut output).unwrap());
}

#[tokio::test]
async fn test_run_main_play_again_error() {
    // Test that run_main breaks loop if get_play_again_choice returns error (unwrap_or(false))
    let server = MockServer::start();
    // Start game mocks (success)
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
    let mut input = ErrorReader; // Error on read input (e.g. play again choice)
    // But play_single_game needs input too.
    // Wait, play_single_game uses reader. If reader errors immediately, play_single_game errors.
    // If play_single_game errors, run_main prints error and calls get_play_again_choice.
    // get_play_again_choice uses same reader, so it also errors.
    // unwrap_or(false) -> false -> break loop.
    
    let mut output = Vec::new();
    
    let _ = cui::run_main(&mut client, &mut input, &mut output).await;
    
    let output_str = String::from_utf8(output).unwrap();
    assert!(output_str.contains("An error occurred during the game"));
}

#[tokio::test]
async fn test_run_main_play_again_success() {
    let server = MockServer::start();

    // Mock for get_available_agents (called twice)
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });

    // Mock for start_game (called twice)
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
            "current_player": "X", "game_over": true, "winner": "O" // Game over immediately
        }));
    });

    let mut client = GameClient::new(server.base_url());
    
    // Input:
    // Game 1: Agent X (2), Agent O (2). Game ends immediately.
    // Play again? y
    // Game 2: Agent X (2), Agent O (2). Game ends immediately.
    // Play again? n
    let mut input = "2\n2\ny\n2\n2\nn\n".as_bytes();
    let mut output = Vec::new();

    let _ = cui::run_main(&mut client, &mut input, &mut output).await;

    let output_str = String::from_utf8(output).unwrap();
    // Count how many times "Start New Tic Tac Toe Game" appears
    let start_count = output_str.matches("--- Start New Tic Tac Toe Game ---").count();
    assert_eq!(start_count, 2);
}

#[tokio::test]
async fn test_run_main_write_fail() {
    let server = MockServer::start();
    // Start game mocks (fail immediately)
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(500); // Trigger fallback, but then...
    });
    
    let mut client = GameClient::new(server.base_url());
    
    // Reader fails immediately -> play_single_game fails.
    let mut input = ErrorReader;
    
    // Writer fails immediately -> run_main tries to print error -> returns Error instead of panic
    let mut output = CountingErrorWriter::new(0);
    
    let result = cui::run_main(&mut client, &mut input, &mut output).await;
    assert!(result.is_err());
    assert_eq!(result.err().unwrap().to_string(), "simulated write error");
}

#[test]
fn test_get_user_move() {
    let mut input = "5\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(
        get_user_move(&mut input, &mut output).unwrap(),
        Some((1, 1))
    );

    let mut input = "1\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(
        get_user_move(&mut input, &mut output).unwrap(),
        Some((0, 0))
    );

    let mut input = "9\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(
        get_user_move(&mut input, &mut output).unwrap(),
        Some((2, 2))
    );

    let mut input = "q\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), None);

    let mut input = "quit\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), None);

    // Test looping with invalid input
    let mut input = "10\ninvalid\n2\n".as_bytes();
    let mut output = Vec::new();
    assert_eq!(
        get_user_move(&mut input, &mut output).unwrap(),
        Some((0, 1))
    );
}

#[test]
fn test_get_user_move_write_error() {
    let mut input = "invalid\n".as_bytes(); // Invalid input triggers write
    // Prompt "Enter your move..." (1 write)
    // Then read input.
    // Then "Invalid input..." (1 write).
    // If we want to test error on "Invalid input...", we need CountingErrorWriter::new(1).
    // If we want to test error on prompt, new(0).
    // Either works to return Err.
    let mut output = CountingErrorWriter::new(0); 
    assert!(get_user_move(&mut input, &mut output).is_err());
}

#[test]
fn test_get_user_move_eof() {
    let mut input = "".as_bytes();
    let mut output = Vec::new();
    // EOF returns Ok(None)
    assert_eq!(get_user_move(&mut input, &mut output).unwrap(), None);
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
    // Empty input (EOF) now returns default Human
    let mut input = "".as_bytes(); 
    let mut output = Vec::new();
    let choice = get_agent_type_choice(&mut client, "X", &mut input, &mut output)
        .await
        .unwrap();

    assert_eq!(choice, "Human");
}

#[tokio::test]
async fn test_get_agent_type_choice_eof() {
    let server = MockServer::start();
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });

    let mut client = GameClient::new(server.base_url());
    let mut input = "".as_bytes(); // EOF
    let mut output = Vec::new();
    let choice = get_agent_type_choice(&mut client, "X", &mut input, &mut output)
        .await
        .unwrap();

    assert_eq!(choice, "Human");
}

#[tokio::test]
async fn test_play_single_game_human_vs_agent() {    let server = MockServer::start();

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
    // agent for X, agent for O, human move
    let mut input = "1\n2\n1\n".as_bytes();
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
    // agentX, agentO, move1 (invalid), quit
    let mut input = "1\n2\n1\nq\n".as_bytes();
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
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
            "current_player": "X", "game_over": false, "winner": null
        }));
    });

    let mut client = GameClient::new(server.base_url());
    // agentX, agentO, quit
    let mut input = "1\n2\nq\n".as_bytes();
    let mut output = Vec::new();
    let result = play_single_game(&mut client, &mut input, &mut output).await;
    assert!(result.is_ok());
}

#[tokio::test]
async fn test_get_agent_type_choice_write_error() {
    let server = MockServer::start();
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });
    
    let mut client = GameClient::new(server.base_url());
    let mut input = "invalid\n".as_bytes(); // Invalid input triggers write
    let mut output = CountingErrorWriter::new(0); // Error on first write
    // First write is "Choose agent type...", second is "1. Human", ...
    // Actually we want error on "Invalid number..." which happens AFTER read.
    // Writes before read: "Choose...", "1...", "2...", "Enter number...". = 4 writes.
    // So we want error on 5th write? No, CountingErrorWriter counts ALL writes.
    
    // If we want to test error propagation from writeln!("Invalid number..."), 
    // we need CountingErrorWriter to succeed for the prompts, and fail later.
    // Or, we can test error on the initial prompts too.
    // If error on initial prompts, get_agent_type_choice returns Err immediately.
    
    let result = get_agent_type_choice(&mut client, "X", &mut input, &mut output).await;
    assert!(result.is_err());
    assert_eq!(result.err().unwrap().to_string(), "simulated write error");
}

#[tokio::test]
async fn test_run_main_play_single_game_error() {
    // Renamed from test_run_cui_app_play_single_game_error
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
    // Simulate user input: agent for X (Human), agent for O (Random), play again (n)
    let mut input = "1\n2\nn\n".as_bytes();
    let mut output = Vec::new(); // Capture stdout

    let _ = cui::run_main(&mut client, &mut input, &mut output).await; // Call cui::run_main

    let output_str = String::from_utf8(output).unwrap();
    assert!(output_str.contains("An error occurred during the game: HTTP Error 500"));
    assert!(output_str.contains("Game over. Play again? (y/n): "));
}

#[tokio::test]
async fn test_run_main_play_single_game_error_and_write_fail() {
    let server = MockServer::start();

    // Mock for get_available_agents
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200).json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });

    // Mock for start_game - returns error
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(500);
    });

    let mut client = GameClient::new(server.base_url());
    let mut input = "1\n2\nn\n".as_bytes();
    
    // Calculate writes:
    // 1. Header
    // 2. Agent X prompt
    // 3. Option 1
    // 4. Option 2
    // 5. Enter number
    // 6. Agent O prompt
    // 7. Option 1
    // 8. Option 2
    // 9. Enter number
    // 10. Starting game...
    // -> Error from start_game
    // 11. "An error occurred..." -> We want this to fail.
    
    let mut output = CountingErrorWriter::new(10); 

    let result = cui::run_main(&mut client, &mut input, &mut output).await;
    // run_main returns Err if writeln! fails
    assert!(result.is_err());
    assert_eq!(result.err().unwrap().to_string(), "simulated write error");
}

#[tokio::test]
async fn test_play_single_game_agent_vs_human() {
    let server = MockServer::start();

    // Agent vs Human
    // X: Random, O: Human
    // Mock agents response
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });
    
    // Mock start game
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [["", "", ""], ["", "", ""], ["", "", ""]],
            "current_player": "X",
            "game_over": false,
            "winner": null
        }));
    });

    // Mock move (Agent X makes a move - handled by server usually, but here we just need status update)
    // Actually, in the loop:
    // 1. is_human_turn? Current player X. X is Random. False.
    // 2. get_game_status.
    
    server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [["X", "", ""], ["", "", ""], ["", "", ""]],
            "current_player": "O",
            "game_over": false,
            "winner": null
        }));
    });

    // Now O (Human) turn.
    // User inputs move.
    server.mock(|when, then| {
        when.method(POST).path("/game/move");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [["X", "", ""], ["", "O", ""], ["", "", ""]],
            "current_player": "X",
            "game_over": false,
            "winner": null
        }));
    });

    // X (Agent) turn again
    server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [["X", "X", ""], ["", "O", ""], ["", "", ""]],
            "current_player": "O",
            "game_over": false,
            "winner": null
        }));
    });

    // O (Human) quits
    
    let mut client = GameClient::new(server.base_url());
    // Select Agent (Random) for X (2), Human for O (1), then O moves (5), then O quits (q)
    let mut input = "2\n1\n5\nq\n".as_bytes();
    let mut output = Vec::new();
    let result = play_single_game(&mut client, &mut input, &mut output).await;
    
    assert!(result.is_ok());
    let output_str = String::from_utf8(output).unwrap();
    assert!(output_str.contains("Player X (Agent) has made a move."));
}

#[tokio::test]
async fn test_play_single_game_agent_vs_agent() {
    let server = MockServer::start();

    // Mock agents response
    server.mock(|when, then| {
        when.method(GET).path("/agents");
        then.status(200)
            .json_body_obj(&serde_json::json!({ "agents": ["Human", "Random"] }));
    });
    
    // Mock start game
    server.mock(|when, then| {
        when.method(POST).path("/game/start");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [["", "", ""], ["", "", ""], ["", "", ""]],
            "current_player": "X",
            "game_over": false,
            "winner": null
        }));
    });

    // Agent X turn -> Game Over immediately to avoid infinite loop in test
    // due to static mock responses.
    server.mock(|when, then| {
        when.method(GET).path("/game/status");
        then.status(200).json_body_obj(&serde_json::json!({
            "board": [["X", "", ""], ["", "O", ""], ["", "", ""]],
            "current_player": "O",
            "game_over": true,
            "winner": "O"
        }));
    });

    let mut client = GameClient::new(server.base_url());
    // Select Random for X (2), Random for O (2)
    let mut input = "2\n2\n".as_bytes();
    let mut output = Vec::new();
    let result = play_single_game(&mut client, &mut input, &mut output).await;
    
    assert!(result.is_ok());
    let output_str = String::from_utf8(output).unwrap();
    // It enters the loop, prints the message, calls status, sees game over, loops exits.
    assert!(output_str.contains("Player X (Agent) has made a move."));
    assert!(output_str.contains("Game Over: Player O wins!"));
}
