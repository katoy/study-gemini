# train_q_learning.py
from agents.q_learning_agent import QLearningAgent  # 修正
from agents.random_agent import RandomAgent  # 追加
from game_logic import TicTacToe  # 修正
import argparse
from tqdm import tqdm  # 追加
import sys  # 追加


def train_q_learning_agent(num_episodes, continue_training):
    """強化学習エージェントを学習させる"""
    agent = QLearningAgent("O")  # 修正
    if not continue_training:
        agent.q_table = {}  # Qテーブルを初期化

    # プログレスバーで学習の進捗を表示
    for episode in tqdm(range(num_episodes), desc="Training", unit="episode"):
        if episode % 2 == 0:  # 追加
            game = TicTacToe(False, "QLearning")  # 学習時はエージェント同士の対戦 # 修正
        else:  # 追加
            game = TicTacToe(False, "ランダム")  # 追加
        agent.decay_exploration_rate()  # 追加
        while not game.game_over:
            agent_turn_for_training(game, agent)
            # 相手のターンも処理する
            opponent_turn_for_training(game, agent)
        update_q_table_after_game(game, agent)

    agent.save_q_table()  # 学習結果を保存
    print("✅ 学習が完了しました。")  # 追加


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
            winner = game.check_winner()  # 修正
            if winner == game.agent_player:
                reward = 100
            elif winner != "draw" and winner is not None and winner != game.agent_player:  # 修正
                reward = -100
            elif winner == "draw":  # 修正
                reward = 0
            else:
                reward = 0
            agent.update_q_table(current_state, action, reward, next_state)


def opponent_turn_for_training(game, agent):
    """学習用の相手エージェントのターン"""
    if game.current_player != game.agent_player:
        current_state = agent.board_to_string(game.board)
        # 相手エージェントも同じQLearningAgentを使用
        if isinstance(game.agent, QLearningAgent):  # 修正
            move = agent.get_move(game.board)
        else:  # 追加
            move = game.agent.get_move(game.board)  # 追加
        if move is not None:
            row, col = move
            action = row * 3 + col
            game.make_move(row, col)
            game.switch_player()
            next_state = agent.board_to_string(game.board)
            winner = game.check_winner()
            if winner != "draw" and winner is not None and winner != game.agent_player:  # 修正
                reward = -100  # 修正
            elif winner == game.agent_player:  # 修正
                reward = 100  # 修正
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
    elif winner != "draw" and winner is not None and winner != game.agent_player:  # 修正
        reward = -100  # 修正
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
