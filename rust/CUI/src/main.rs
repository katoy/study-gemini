use cui::{game_client::GameClient, run_main};
use std::io;

const SERVER_URL: &str = "http://127.0.0.1:8000";

#[tokio::main]
async fn main() {
    let mut client = GameClient::new(SERVER_URL.to_string());
    let mut stdin = io::stdin().lock();
    let mut stdout = io::stdout();
    if let Err(e) = run_main(&mut client, &mut stdin, &mut stdout).await {
        eprintln!("Application error: {}", e);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_server_url() {
        assert_eq!(SERVER_URL, "http://127.0.0.1:8000");
    }
}
