use cui::display::display_board;
use cui::models::GameState;
use std::io::Write;

fn create_game_state(
    board: Vec<Vec<String>>,
    current_player: &str,
    game_over: bool,
    winner: Option<&str>,
) -> GameState {
    GameState {
        board,
        current_player: current_player.to_string(),
        game_over,
        winner: winner.map(|s| s.to_string()),
    }
}

#[test]
fn test_display_board_ongoing() {
    let game_state = create_game_state(
        vec![
            vec!["X".to_string(), " ".to_string(), "O".to_string()],
            vec![" ".to_string(), "X".to_string(), " ".to_string()],
            vec![" ".to_string(), " ".to_string(), "O".to_string()],
        ],
        "X",
        false,
        None,
    );
    // Just call the function to ensure it doesn't panic.
    // Capturing and asserting stdout is more complex and brittle.
    println!(); // Add a newline to separate test output
    display_board(&game_state, &mut Vec::new()).unwrap();
}

#[test]
fn test_display_board_winner() {
    let game_state = create_game_state(
        vec![
            vec!["X".to_string(), "X".to_string(), "X".to_string()],
            vec![" ".to_string(), "O".to_string(), " ".to_string()],
            vec!["O".to_string(), " ".to_string(), " ".to_string()],
        ],
        "X",
        true,
        Some("X"),
    );
    println!();
    display_board(&game_state, &mut Vec::new()).unwrap();
}

#[test]
fn test_display_board_draw() {
    let game_state = create_game_state(
        vec![
            vec!["X".to_string(), "O".to_string(), "X".to_string()],
            vec!["X".to_string(), "O".to_string(), "O".to_string()],
            vec!["O".to_string(), "X".to_string(), "X".to_string()],
        ],
        "X", // Player doesn't matter on draw
        true,
        Some("draw"),
    );
    println!();
    display_board(&game_state, &mut Vec::new()).unwrap();
}

#[test]
fn test_display_board_empty() {
    let game_state = create_game_state(
        vec![
            vec![" ".to_string(), " ".to_string(), " ".to_string()],
            vec![" ".to_string(), " ".to_string(), " ".to_string()],
            vec![" ".to_string(), " ".to_string(), " ".to_string()],
        ],
        "X",
        false,
        None,
    );
    println!();
    display_board(&game_state, &mut Vec::new()).unwrap();
}

#[test]
fn test_display_board_game_over_no_winner() {
    let game_state = create_game_state(
        vec![
            vec!["X".to_string(), "O".to_string(), "X".to_string()],
            vec!["X".to_string(), "O".to_string(), "O".to_string()],
            vec!["O".to_string(), "X".to_string(), " ".to_string()],
        ],
        "X",
        true, // Game over
        None, // No winner
    );
    let mut output = Vec::new();
    display_board(&game_state, &mut output).unwrap();
    let output_str = String::from_utf8(output).unwrap();
    assert!(output_str.contains("Game Over."));
}

struct ErrorWriter;

impl Write for ErrorWriter {
    fn write(&mut self, _buf: &[u8]) -> std::io::Result<usize> {
        Err(std::io::Error::new(std::io::ErrorKind::Other, "write error"))
    }

    fn flush(&mut self) -> std::io::Result<()> {
        Err(std::io::Error::new(std::io::ErrorKind::Other, "flush error"))
    }
}

#[test]
fn test_display_board_write_error() {
    let game_state = create_game_state(
        vec![
            vec![" ".to_string(), " ".to_string(), " ".to_string()],
            vec![" ".to_string(), " ".to_string(), " ".to_string()],
            vec![" ".to_string(), " ".to_string(), " ".to_string()],
        ],
        "X",
        false,
        None,
    );
    let mut error_writer = ErrorWriter;
    let result = display_board(&game_state, &mut error_writer);
    assert!(result.is_err());
}
