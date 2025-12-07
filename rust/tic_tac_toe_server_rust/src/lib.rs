// rust/tic_tac_toe_server_rust/src/lib.rs

pub mod game_logic;
pub mod schemas;
pub mod agents;
pub mod server;

use actix_web::{dev::Server, web, App, HttpServer};
use actix_cors::Cors;
use env_logger::{Builder, Target};
use log::LevelFilter;
use std::net::{SocketAddr, TcpListener};
use std::sync::{Arc, Mutex};

/// Configures the Actix-web application services and routes.
pub fn configure_app(cfg: &mut web::ServiceConfig) {
    cfg.route("/game/start", web::post().to(server::start_game_handler))
        .route("/game/status", web::get().to(server::get_game_status_handler))
        .route("/game/move", web::post().to(server::make_move_handler))
        .route("/agents", web::get().to(server::get_available_agents_handler));
}

/// Sets up the server and returns the `Server` handle and its listening address.
/// Binds to a random available port.
pub fn bootstrap() -> std::io::Result<(Server, SocketAddr)> {
    let listener = TcpListener::bind("127.0.0.1:8000")?;
    let addr = listener.local_addr()?;

    log::info!("Starting Actix-web server on http://{}", addr);

    let game_manager_arc = Arc::new(Mutex::new(server::GameManager::new())); // GameManager を一度だけ作成

    let server = HttpServer::new(move || {
        App::new()
            .wrap(Cors::permissive())
            .app_data(web::Data::new(game_manager_arc.clone()))
            .configure(configure_app)
    })
    .listen(listener)?
    .run();

    Ok((server, addr))
}

pub async fn run_with_bootstrap_fn(
    bootstrap_fn: impl Fn() -> std::io::Result<(Server, SocketAddr)> + Send + Sync + 'static,
) -> std::io::Result<()> {
    // ロギングの初期化 (try_initでテスト実行時の重複エラーを回避)
    let _ = Builder::new()
        .filter_level(LevelFilter::Info)
        .target(Target::Stdout)
        .try_init();

    let (server, _) = bootstrap_fn()?;
    server.await
}

pub async fn run() -> std::io::Result<()> {
    run_with_bootstrap_fn(bootstrap).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::{test, web, App};
    use crate::schemas::AvailableAgentsResponse;
    use std::sync::{Arc, Mutex};

    #[actix_web::test]
    async fn test_app_configuration() {
        // GIVEN: A test app with a GameManager instance, configured with our app's logic
        let game_manager = web::Data::new(Arc::new(Mutex::new(server::GameManager::new())));
        let app = test::init_service(
            App::new()
                .app_data(game_manager.clone())
                .configure(configure_app)
        ).await;
        
        // WHEN: A request is made to one of the configured routes
        let req = test::TestRequest::get().uri("/agents").to_request();
        let resp = test::call_service(&app, req).await;

        // THEN: The response should be successful
        assert!(resp.status().is_success());
    }

    #[tokio::test]
    async fn test_server_startup_and_shutdown() {
        // GIVEN: A running server instance
        let (server, addr) = bootstrap().expect("Failed to bootstrap server");
        let server_handle = server.handle();
        let server_task = tokio::spawn(server);

        // WHEN: A request is made to the server
        let client = reqwest::Client::new();
        let url = format!("http://{}/agents", addr);
        // Allow for a short delay for the server to be fully up
        tokio::time::sleep(std::time::Duration::from_millis(100)).await;
        let response = client.get(&url).send().await.expect("Failed to send request");

        // THEN: The response is successful and contains the expected data
        assert!(response.status().is_success());
        let body: AvailableAgentsResponse = response.json().await.expect("Failed to parse json body");
        assert_eq!(body.agents, vec!["Human".to_string(), "Random".to_string()]);

        // FINALLY: The server is shut down gracefully
        server_handle.stop(true).await;
        assert!(server_task.await.is_ok());
    }

    #[tokio::test]
    async fn test_run_error_handling() {
        // GIVEN: A mock bootstrap function that always returns an error
        let mock_bootstrap_fn = || {
            Err(std::io::Error::new(std::io::ErrorKind::Other, "Mock bootstrap error"))
        };

        // WHEN: `run_with_bootstrap_fn` is called with the mock function
        let result = run_with_bootstrap_fn(mock_bootstrap_fn).await;

        // THEN: The function should return an error, indicating proper error propagation
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().kind(), std::io::ErrorKind::Other);
    }
}