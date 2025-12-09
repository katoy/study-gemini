use crate::models::{Agents, ErrorDetail, GameState, MoveRequest};
use anyhow::{anyhow, Result};
use reqwest::Client;
use serde::de::DeserializeOwned;
use serde::Serialize;
use std::collections::HashMap;

pub struct GameClient {
    client: Client,
    server_url: String,
    available_agents: Option<Vec<String>>,
}

impl GameClient {
    pub fn new(server_url: String) -> Self {
        Self::with_client(server_url, Client::new())
    }
    
    pub fn with_client(server_url: String, client: Client) -> Self {
        GameClient {
            client,
            server_url,
            available_agents: None,
        }
    }
    async fn send_request<T: DeserializeOwned, B: Serialize>(
        &self,
        method: reqwest::Method,
        endpoint: &str,
        body: Option<B>,
    ) -> Result<T> {
        let url = format!("{}/{}", self.server_url, endpoint);
        let mut request = self.client.request(method, &url);
        if let Some(body) = body {
            request = request.json(&body);
        }

        let response = request.send().await?;

        if !response.status().is_success() {
            let status = response.status();
            let error_body = response.json::<ErrorDetail>().await;
            if let Ok(error_detail) = error_body {
                return Err(anyhow!(
                    "HTTP Error {}: {}",
                    status,
                    error_detail.detail
                ));
            }
            return Err(anyhow!("HTTP Error {}", status));
        }

        let response_body = response.json::<T>().await?;
        Ok(response_body)
    }

    pub async fn get_available_agents(&mut self) -> Result<Vec<String>> {
        if let Some(agents) = &self.available_agents {
            return Ok(agents.clone());
        }

        match self.send_request::<Agents, ()>(reqwest::Method::GET, "available_agents", None).await {
            Ok(agents_response) => {
                let agents = agents_response.agents;
                self.available_agents = Some(agents.clone());
                Ok(agents)
            }
            Err(e) => {
                eprintln!("Warning: Could not fetch agent list from server: {}", e);
                eprintln!("Using fallback list.");
                let fallback_agents = vec![
                    "Human".to_string(),
                    "Random".to_string(),
                    "Minimax".to_string(),
                    "Database".to_string(),
                    "QLearning".to_string(),
                    "Perfect".to_string(),
                ];
                self.available_agents = Some(fallback_agents.clone());
                Ok(fallback_agents)
            }
        }
    }
    
    pub async fn start_game(&self, human_player_symbol: &str, player_x_type: &str, player_o_type: &str) -> Result<GameState> {
        let mut body = HashMap::new();
        body.insert("human_player_symbol", human_player_symbol);
        body.insert("player_x_type", player_x_type);
        body.insert("player_o_type", player_o_type);
        self.send_request(reqwest::Method::POST, "start_game", Some(&body)).await
    }

    pub async fn make_move(&self, row: usize, col: usize) -> Result<GameState> {
        let body = MoveRequest { row, col };
        self.send_request(reqwest::Method::POST, "make_move", Some(&body)).await
    }

    pub async fn get_game_status(&self) -> Result<GameState> {
        self.send_request::<GameState, ()>(reqwest::Method::GET, "game_status", None).await
    }

    pub async fn make_agent_move(&self) -> Result<GameState> {
        self.send_request::<GameState, ()>(reqwest::Method::POST, "game_agent_move", None).await
    }
}
