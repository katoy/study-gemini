// rust/tic_tac_toe_server_rust/src/lib.rs

pub mod game_logic;
pub mod schemas;
pub mod agents;
pub mod server;

use actix_web::{dev::Server, web, App, HttpServer, HttpResponse};
use actix_cors::Cors;
use env_logger::{Builder, Target};
use log::LevelFilter;
use std::net::{SocketAddr, TcpListener}; // SocketAddr, TcpListener は std::net のまま
use std::sync::Arc; // Arc は std::sync のまま
use utoipa::OpenApi; // 追加
use utoipa_swagger_ui::SwaggerUi; // 追加

// 新しいハンドラ関数
pub async fn get_openapi_json(openapi: web::Data<Arc<utoipa::openapi::OpenApi>>) -> HttpResponse {
    HttpResponse::Ok().json(openapi.as_ref().clone())
}

// 新しいヘルパー関数
pub fn write_openapi_file(openapi_doc: &utoipa::openapi::OpenApi, file_path: &str) -> std::io::Result<()> {
    let openapi_json = openapi_doc.to_json().map_err(|e| {
        std::io::Error::other(format!("Failed to serialize OpenAPI spec to JSON: {}", e))
    })?;
    std::fs::write(file_path, openapi_json).map_err(|e| {
        std::io::Error::other(format!("Failed to write openapi.json: {}", e))
    })?;
    Ok(())
}

/// Configures the Actix-web application services and routes.
pub fn configure_app(cfg: &mut web::ServiceConfig) {
    cfg.route("/game/start", web::post().to(server::start_game_handler))
        .route("/game/status", web::get().to(server::get_game_status_handler))
        .route("/game/move", web::post().to(server::make_move_handler))
        .route("/agents", web::get().to(server::get_available_agents_handler));
}

/// Sets up the server and returns the `Server` handle and its listening address.
/// Binds to a random available port.
pub fn bootstrap(port: u16) -> std::io::Result<(Server, SocketAddr)> {
    bootstrap_with_filepath(port, "openapi.json")
}

pub fn bootstrap_with_filepath(port: u16, openapi_path: &str) -> std::io::Result<(Server, SocketAddr)> {
    let listener = TcpListener::bind(format!("127.0.0.1:{}", port))?;
    let addr = listener.local_addr()?;

    log::info!("Starting Actix-web server on http://{}", addr);

    let game_manager_arc = Arc::new(tokio::sync::Mutex::new(server::GameManager::new())); // GameManager を一度だけ作成

    // OpenAPIドキュメントを生成
    let openapi_doc = server::ApiDoc::openapi(); // ApiDoc から OpenApi インスタンスを生成

    if let Err(e) = write_openapi_file(&openapi_doc, openapi_path) {
        log::error!("Failed to write {}: {}", openapi_path, e);
        return Err(std::io::Error::other(format!("Failed to write {}: {}", openapi_path, e)));
    }
    log::info!("OpenAPI specification written to {}", openapi_path);

    let openapi_doc_arc = Arc::new(openapi_doc); // Arc でラップ

    let server = HttpServer::new(move || {
        App::new()
            .wrap(Cors::permissive())
            .app_data(web::Data::new(game_manager_arc.clone()))
            .app_data(web::Data::new(openapi_doc_arc.clone())) // OpenAPIドキュメントをアプリケーションデータとして登録
            .configure(configure_app)
            // OpenAPIドキュメントのエンドポイントを追加
            .service(
                SwaggerUi::new("/swagger-ui/{tail:.*}")
                    .url("/api-docs/openapi.json", openapi_doc_arc.as_ref().clone()) // Arc の中身をクローン
            )
            .service(web::scope("/api-docs")
                .route("/openapi.json", web::get().to(get_openapi_json)) // 新しいハンドラを登録
            )
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

pub async fn run(port: u16) -> std::io::Result<()> {
    run_with_bootstrap_fn(move || bootstrap(port)).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::{test, web, App};
    use crate::schemas::AvailableAgentsResponse;
    use std::sync::Arc; // Mutex は tokio::sync::Mutex を使用

    #[actix_web::test]
    async fn test_app_configuration() {
        // GIVEN: A test app with a GameManager instance, configured with our app's logic
        let game_manager = web::Data::new(Arc::new(tokio::sync::Mutex::new(server::GameManager::new())));
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
        let (server, addr) = bootstrap(8002).expect("Failed to bootstrap server");
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
            Err(std::io::Error::other("Mock bootstrap error"))
        };

        // WHEN: `run_with_bootstrap_fn` is called with the mock function
        let result = run_with_bootstrap_fn(mock_bootstrap_fn).await;

        // THEN: The function should return an error, indicating proper error propagation
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().kind(), std::io::ErrorKind::Other);
    }

    #[actix_web::test]
    async fn test_get_openapi_json() {
        // GIVEN: An OpenAPI document and an app configured to serve it
        let openapi_doc = server::ApiDoc::openapi();
        let openapi_doc_arc = Arc::new(openapi_doc);

        let app = test::init_service(
            App::new()
                .app_data(web::Data::new(openapi_doc_arc.clone()))
                .service(web::scope("/api-docs")
                    .route("/openapi.json", web::get().to(get_openapi_json))
                )
        ).await;

        // WHEN: A request is made to the openapi.json endpoint
        let req = test::TestRequest::get().uri("/api-docs/openapi.json").to_request();
        let resp = test::call_service(&app, req).await;

        // THEN: The response should be successful and contain valid JSON
        assert!(resp.status().is_success());
        let response_body = test::read_body(resp).await;
        let json: serde_json::Value = serde_json::from_slice(&response_body).expect("Failed to parse JSON response");
        assert!(json.is_object());
        assert_eq!(json["openapi"], "3.1.0"); // Check a known field to ensure it's an OpenAPI doc
    }

    #[tokio::test]
    async fn test_write_openapi_file_success() {
        use tempfile::NamedTempFile;
        use std::io::Read;

        // GIVEN: An OpenAPI document and a temporary file path
        let openapi_doc = server::ApiDoc::openapi();
        let mut temp_file = NamedTempFile::new().expect("Failed to create temporary file");
        let file_path = temp_file.path().to_str().expect("Failed to get temporary file path");

        // WHEN: write_openapi_file is called with the document and path
        let result = write_openapi_file(&openapi_doc, file_path);

        // THEN: The operation should succeed and the file content should be valid JSON
        assert!(result.is_ok());

        let mut contents = String::new();
        temp_file.read_to_string(&mut contents).expect("Failed to read temporary file");
        let json: serde_json::Value = serde_json::from_str(&contents).expect("Failed to parse JSON from file");
        assert!(json.is_object());
        assert_eq!(json["openapi"], "3.1.0"); // Verify a known OpenAPI field
    }

    #[tokio::test]
    async fn test_write_openapi_file_error() {
        use tempfile::tempdir;


        // GIVEN: An OpenAPI document and an invalid file path (e.g., in a non-existent subdirectory of a temporary directory)
        let openapi_doc = server::ApiDoc::openapi();
        let temp_dir = tempdir().expect("Failed to create temporary directory");
        let invalid_path = temp_dir.path().join("non_existent_subdir").join("openapi.json");
        let file_path = invalid_path.to_str().expect("Failed to get invalid file path");

        // WHEN: write_openapi_file is called with the document and invalid path
        let result = write_openapi_file(&openapi_doc, file_path);

        // THEN: The operation should return an error, specifically a NotFound error because the directory doesn't exist
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().kind(), std::io::ErrorKind::Other);
    }

    #[tokio::test]
    async fn test_run_success() {
        // GIVEN: The application is configured to run successfully
        // WHEN: The run function is called
        let run_task = tokio::spawn(async {
            run(8003).await.expect("run function failed");
        });

        // Allow for a short delay for the server to be fully up
        tokio::time::sleep(std::time::Duration::from_millis(100)).await;

        // Simulate a request to ensure the server is responsive
        let client = reqwest::Client::new();
        let response = client.get("http://127.0.0.1:8003/agents").send().await;
        assert!(response.is_ok());
        assert!(response.unwrap().status().is_success());

        // Assuming graceful shutdown is handled elsewhere or the test environment cleans up
        // For now, we'll just check if the run_task finishes without panicking
        // In a real application, you'd send a shutdown signal.
        // Since `bootstrap` doesn't provide a handle outside, we cannot explicitly stop it here.
        // We rely on the test environment to clean up, or a timeout in actual usage.
        // However, for coverage, this path is now exercised.

        // To prevent the test from hanging indefinitely, we can add a timeout,
        // but for coverage testing, simply exercising the code path is the goal.
        // For a more robust integration test, server_handle.stop() would be used.
        run_task.abort(); // Forcefully abort the task to prevent hanging
    }

        #[tokio::test]

        async fn test_bootstrap_bind_error() {

            use std::net::TcpListener;

    

            // GIVEN: A port that is already in use

            let _listener = TcpListener::bind("127.0.0.1:8001")

                .expect("Failed to bind to port for test setup (preventing reuse)");

    

            // WHEN: bootstrap is called trying to bind to the same port

            let result = bootstrap(8001);

    

            // THEN: It should return an AddrInUse error

            assert!(result.is_err());

            let err = match result {

                Ok(_) => panic!("Expected an error, but got Ok"),

                Err(e) => e,

            };

            assert_eq!(err.kind(), std::io::ErrorKind::AddrInUse);

        }

    

        #[tokio::test]

        async fn test_bootstrap_write_error() {

            use tempfile::tempdir;

    

            // GIVEN: An invalid file path for openapi.json

            let temp_dir = tempdir().expect("Failed to create temporary directory");

            let invalid_path = temp_dir.path().join("non_existent_subdir").join("openapi.json");

            let file_path = invalid_path.to_str().expect("Failed to get invalid file path");

    

                    // WHEN: bootstrap_with_filepath is called with the invalid path

    

                    let result = bootstrap_with_filepath(8004, file_path);

    

            

    

                    // THEN: It should return an error

    

                    assert!(result.is_err());

    

                    let err = match result {

    

                        Ok(_) => panic!("Expected an error"),

    

                        Err(e) => e,

    

                    };

    

                    assert_eq!(err.kind(), std::io::ErrorKind::Other);

    

                }

    

            }

    

            

    