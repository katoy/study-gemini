use cui::display::display_board;
use cui::models::GameState;
use std::io::{self, Write}; // io をインポート

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

struct CountingErrorWriter {
    writes_before_error: usize,
    writes_count: usize,
}

impl CountingErrorWriter {
    fn new(writes_before_error: usize) -> Self {
        CountingErrorWriter {
            writes_before_error,
            writes_count: 0,
        }
    }
}

impl Write for CountingErrorWriter {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        self.writes_count += 1;
        if self.writes_count > self.writes_before_error {
            Err(io::Error::new(
                io::ErrorKind::Other,
                "simulated write error",
            ))
        } else {
            // Simulate successful write by returning the buffer length
            Ok(buf.len())
        }
    }

    fn flush(&mut self) -> io::Result<()> {
        // Flush doesn't typically fail on its own in simple cases, but can be mocked if needed
        Ok(())
    }
}

#[test]
fn test_display_board_write_error_first_writeln() {
    let game_state = create_game_state(vec![vec![" ".to_string(); 3]; 3], "X", false, None);
    // Error on the very first writeln! (header)
    let mut error_writer = CountingErrorWriter::new(0);
    let result = display_board(&game_state, &mut error_writer);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().kind(), io::ErrorKind::Other);
}

#[test]
fn test_display_board_write_error_board_row_writeln() {
    let game_state = create_game_state(vec![vec![" ".to_string(); 3]; 3], "X", false, None);
    // Error on the third writeln! (first board row)
    // There are 3 writeln! calls for the board rows, and 1 for the header
    let mut error_writer = CountingErrorWriter::new(1); // Error after the first writeln (header)
    let result = display_board(&game_state, &mut error_writer);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().kind(), io::ErrorKind::Other);
}

#[test]
fn test_display_board_write_error_final_writeln() {
    let game_state = create_game_state(vec![vec![" ".to_string(); 3]; 3], "X", false, None);
    // Error on a later writeln! (e.g., current player)
    // Header (1), 3 board rows (3), separator (1) = 5 writes before error
    let mut error_writer = CountingErrorWriter::new(5);
    let result = display_board(&game_state, &mut error_writer);
    assert!(result.is_err());
    assert_eq!(result.unwrap_err().kind(), io::ErrorKind::Other);
}
