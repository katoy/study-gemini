pub mod display;
pub mod game_client;
pub mod models;

use anyhow::Result;
use game_client::GameClient;
use std::io::{BufRead, Write};
use tokio::time::{sleep, Duration};



pub async fn run_main<R: BufRead, W: Write>(
    client: &mut GameClient,
    reader: &mut R,
    writer: &mut W,
) {
    loop {
        if let Err(e) = play_single_game(client, reader, writer).await {
            writeln!(writer, "An error occurred during the game: {}", e).unwrap();
        }

        if !get_play_again_choice(reader, writer).unwrap_or(false) {
            break;
        }
    }
}


pub fn get_play_again_choice<R: BufRead, W: Write>(reader: &mut R, writer: &mut W) -> Result<bool> {
    write!(writer, "Game over. Play again? (y/n): ")?;
    writer.flush()?;
    let mut choice = String::new();
    reader.read_line(&mut choice)?;
    Ok(choice.trim().to_lowercase() == "y")
}

pub async fn play_single_game<R: BufRead, W: Write>(client: &mut GameClient, reader: &mut R, writer: &mut W) -> Result<()> {
    writeln!(writer, "\n--- Start New Tic Tac Toe Game ---")?;

    let human_player_symbol = get_player_symbol_choice(reader, writer)?;
    let player_x_type = get_agent_type_choice(client, "X", reader, writer).await?;
    let player_o_type = get_agent_type_choice(client, "O", reader, writer).await?;

    writeln!(writer, "\nStarting new Tic Tac Toe game...")?;

    let mut game_state = client
        .start_game(&human_player_symbol, &player_x_type, &player_o_type)
        .await?;
            display::display_board(&game_state, writer)?;

    while !game_state.game_over {
        let current_player = &game_state.current_player;

        let is_human_turn = (current_player == "X" && player_x_type == "Human")
            || (current_player == "O" && player_o_type == "Human");

        if is_human_turn {
            if let Some((row, col)) = get_user_move(reader, writer)? {
                match client.make_move(row, col).await {
                    Ok(new_state) => {
                        game_state = new_state;

                                display::display_board(&game_state, writer)?;
                    }
                    Err(e) => {
                        writeln!(writer, "Error: {}", e)?;
                        continue; // Ask for move again
                    }
                }
            } else {
                // User chose to quit
                writeln!(writer, "Game interrupted by user.")?;
                return Ok(());
            }
        } else {
            writeln!(writer, "Player {} (Agent) is thinking...", current_player)?;
            sleep(Duration::from_secs(1)).await; // Simulate agent thinking
            game_state = client.make_agent_move().await?;

                    display::display_board(&game_state, writer)?;
        }
    }

    Ok(())
}

pub fn get_player_symbol_choice<R: BufRead, W: Write>(reader: &mut R, writer: &mut W) -> Result<String> {
    loop {
        write!(writer, "Choose your player (X/O): ")?;
        writer.flush()?;
        let mut choice = String::new();
        reader.read_line(&mut choice)?;
        let choice = choice.trim().to_uppercase();
        if choice == "X" || choice == "O" {
            return Ok(choice);
        } else {
            writeln!(writer, "Invalid choice. Please enter 'X' or 'O'.")?;
        }
    }
}

pub async fn get_agent_type_choice<R: BufRead, W: Write>(
    client: &mut GameClient,
    player_char: &str,
    reader: &mut R,
    writer: &mut W,
) -> Result<String> {
    let agent_types = client.get_available_agents().await?;

    if agent_types.is_empty() {
        writeln!(writer, "Error: No agents available. Defaulting to Human.")?;
        return Ok("Human".to_string());
    }

    loop {
        writeln!(writer, "\nChoose agent type for player {}:", player_char)?;
        for (i, agent_type) in agent_types.iter().enumerate() {
            writeln!(writer, "{}. {}", i + 1, agent_type)?;
        }
        write!(writer, "Enter number (1-{}): ", agent_types.len())?;
        writer.flush()?;

        let mut choice_num_str = String::new();
        reader.read_line(&mut choice_num_str)?;

        match choice_num_str.trim().parse::<usize>() {
            Ok(choice_num) if (1..=agent_types.len()).contains(&choice_num) => {
                return Ok(agent_types[choice_num - 1].clone());
            }
            _ => {
                writeln!(
                    writer,
                    "Invalid number. Please enter a number between 1 and {}.",
                    agent_types.len()
                )?;
            }
        }
    }
}

pub fn get_user_move<R: BufRead, W: Write>(reader: &mut R, writer: &mut W) -> Result<Option<(usize, usize)>> {
    loop {
        write!(writer, "Enter your move (1-9) or 'q' to quit: ")?;
        writer.flush()?;
        let mut user_input = String::new();
        reader.read_line(&mut user_input)?;
        let user_input = user_input.trim().to_lowercase();

        if user_input == "q" || user_input == "quit" {
            return Ok(None);
        }

        match user_input.parse::<usize>() {
            Ok(move_num) if (1..=9).contains(&move_num) => {
                let row = (move_num - 1) / 3;
                let col = (move_num - 1) % 3;
                return Ok(Some((row, col)));
            }
            _ => {
                writeln!(writer, "Invalid input. Please enter a number between 1 and 9.")?;
            }
        }
    }
}
