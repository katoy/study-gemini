// rust/tic_tac_toe_server_rust/src/main.rs

use tic_tac_toe_server_rust::run;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    run().await
}
