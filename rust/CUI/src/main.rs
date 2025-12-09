use cui::{run_main, game_client::GameClient};
use std::io;

const SERVER_URL: &str = "http://127.0.0.1:8000";

#[tokio::main]
async fn main() {
    let mut client = GameClient::new(SERVER_URL.to_string());
    let mut stdin = io::stdin().lock();
    let mut stdout = io::stdout();
    run_main(&mut client, &mut stdin, &mut stdout).await;
}