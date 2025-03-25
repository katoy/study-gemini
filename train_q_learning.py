# train_q_learning.py
from agents.q_learning_agent import QLearningAgent
from game_logic import TicTacToe
import argparse
from tqdm import tqdm  # 追加
import sys # 追加

def train_q_learning_agent(num_episodes, continue_training):
    """強化学習エージェントを学習させる"""
    agent = QLearningAgent("O")  # エージェントを初期化
    if not continue_training:
        agent.q_table = {}  # Qテーブルを初期化

    # プログレスバーで学習の進捗を表示
    for episode in tqdm(range(num_episodes), desc="Training", unit="episode"):
        game = TicTacToe(False, "QLearning")  # 学習時はエージェント同士の対戦
        while not game.game_over:
            agent_turn_for_training(game, agent)
            # 相手のターンも処理する
            opponent_turn_for_training(game, agent)
        update_q_table_after_game(game, agent)

    agent.save_q_table()  # 学習結果を保存

def agent_turn_for_training(game, agent):
    """学習用のエージェントのターン"""
    if game.current_player == game.agent_player:
        current_state = agent.board_to_string(game.board)
        move = agent.get_move(game.board)
        if move is not None:
            row, col = move
            action = row * 3 + col
            game.make_move(row, col)
            game.switch_player()
            next_state = agent.board_to_string(game.board)
            winner = game.check_winner()
            if winner == game.agent_player:
                reward = 100
            elif winner == game.human_player:
                reward = -100
            elif winner == "draw":
                reward = 0
            else:
                reward = 0
            agent.update_q_table(current_state, action, reward, next_state)

def opponent_turn_for_training(game, agent):
    """学習用の相手エージェントのターン"""
    if game.current_player != game.agent_player:
        current_state = agent.board_to_string(game.board)
        # 相手エージェントも同じQLearningAgentを使用
        move = agent.get_move(game.board)
        if move is not None:
            row, col = move
            action = row * 3 + col
            game.make_move(row, col)
            game.switch_player()
            next_state = agent.board_to_string(game.board)
            winner = game.check_winner()
            if winner == game.agent_player:
                reward = -100
            elif winner == game.human_player:
                reward = 100
            elif winner == "draw":
                reward = 0
            else:
                reward = 0
            agent.update_q_table(current_state, action, reward, next_state)

def update_q_table_after_game(game, agent):
    """ゲーム終了後にQテーブルを更新する"""
    winner = game.check_winner()
    if winner == game.agent_player:
        reward = 100
    elif winner == game.human_player:
        reward = -100
    elif winner == "draw":
        reward = 0
    else:
        reward = 0

    # 最後の状態と行動に対する報酬を更新
    current_state = agent.board_to_string(game.board)
    if agent.get_available_moves(game.board):
        move = agent.get_move(game.board)
        if move is not None:
            row, col = move
            action = row * 3 + col
            agent.update_q_table(current_state, action, reward, current_state)

def main():
    parser = argparse.ArgumentParser(description="Train Q-Learning agent for Tic Tac Toe.")
    parser.add_argument("--episodes", type=int, default=10000, help="Number of training episodes.")
    parser.add_argument("--continue_training", action="store_true", help="Continue training from existing Q-table.")

    # 引数なしで実行された場合にヘルプを表示
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    train_q_learning_agent(args.episodes, args.continue_training)

if __name__ == "__main__":
    main()
