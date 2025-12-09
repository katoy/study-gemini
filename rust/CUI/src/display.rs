use crate::models::GameState;
use std::io::Write;

pub fn display_board(game_state: &GameState, output: &mut impl Write) -> std::io::Result<()> {
    writeln!(output, "\n--- Tic Tac Toe Board ---")?;
    let mut display_cells = vec![vec![String::new(); 3]; 3];

    for (r_idx, row) in game_state.board.iter().enumerate() {
        for (c_idx, cell) in row.iter().enumerate() {
            if cell.trim().is_empty() {
                display_cells[r_idx][c_idx] = (r_idx * 3 + c_idx + 1).to_string();
            } else {
                display_cells[r_idx][c_idx] = cell.clone();
            }
        }
    }

    for row in display_cells {
        writeln!(output, "| {} | {} | {} |", row[0], row[1], row[2])?;
    }
    writeln!(output, "-------------------------")?;

    if let Some(winner) = &game_state.winner {
        if winner == "draw" {
            writeln!(output, "Game Over: It's a draw!")?;
        } else {
            writeln!(output, "Game Over: Player {} wins!", winner)?;
        }
    } else if game_state.game_over {
        writeln!(output, "Game Over.")?;
    } else {
        writeln!(output, "Current Player: {}", game_state.current_player)?;
    }
    Ok(())
}
