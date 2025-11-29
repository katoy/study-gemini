import argparse
from tqdm import tqdm
from game_logic import TicTacToe
from agents.q_learning_agent import QLearningAgent


def evaluate_models(q_table_file1, q_table_file2, num_games):
    """
    Evaluates the strength of two Q-learning agents against each other.
    """
    print("=== モデル評価レポート ===")
    print(f"総ゲーム数: {num_games}回/対戦")

    agent1_wins = 0
    agent2_wins = 0
    draws = 0

    # --- Agent1が先手 ('X') の場合 ---
    print("\n--- Agent1 (X) vs Agent2 (O) ---")
    agent1 = QLearningAgent(player='X', q_table_file=q_table_file1, is_training=False)
    agent2 = QLearningAgent(player='O', q_table_file=q_table_file2, is_training=False)

    for _ in tqdm(range(num_games), desc="Agent1(X) vs Agent2(O)"):
        game = TicTacToe(agent_x=agent1, agent_o=agent2)
        while not game.game_over:
            current_agent = game.get_current_agent()
            move = current_agent.get_move(game.board)
            if move is None:
                break
            game.make_move(move[0], move[1])
            winner = game.check_winner()
            if winner:
                break
            game.switch_player()

        winner = game.check_winner()
        if winner == agent1.player:
            agent1_wins += 1
        elif winner == agent2.player:
            agent2_wins += 1
        else:
            draws += 1

    print(f"Agent1 ({q_table_file1}) の勝利: {agent1_wins} ({agent1_wins/num_games:.1%})")
    print(f"Agent2 ({q_table_file2}) の勝利: {agent2_wins} ({agent2_wins/num_games:.1%})")
    print(f"引き分け: {draws} ({draws/num_games:.1%})")

    # --- Agent2が先手 ('X') の場合 ---
    agent1_wins_as_o = 0
    agent2_wins_as_x = 0
    draws_as_o = 0

    print("\n--- Agent2 (X) vs Agent1 (O) ---")
    agent2_as_x = QLearningAgent(player='X', q_table_file=q_table_file2, is_training=False)
    agent1_as_o = QLearningAgent(player='O', q_table_file=q_table_file1, is_training=False)

    for _ in tqdm(range(num_games), desc="Agent2(X) vs Agent1(O)"):
        game = TicTacToe(agent_x=agent2_as_x, agent_o=agent1_as_o)
        while not game.game_over:
            current_agent = game.get_current_agent()
            move = current_agent.get_move(game.board)
            if move is None:
                break
            game.make_move(move[0], move[1])
            winner = game.check_winner()
            if winner:
                break
            game.switch_player()

        winner = game.check_winner()
        if winner == agent1_as_o.player:
            agent1_wins_as_o += 1
        elif winner == agent2_as_x.player:
            agent2_wins_as_x += 1
        else:
            draws_as_o += 1

    print(f"Agent1 ({q_table_file1}) の勝利: {agent1_wins_as_o} ({agent1_wins_as_o/num_games:.1%})")
    print(f"Agent2 ({q_table_file2}) の勝利: {agent2_wins_as_x} ({agent2_wins_as_x/num_games:.1%})")
    print(f"引き分け: {draws_as_o} ({draws_as_o/num_games:.1%})")

    # --- 総合結果 ---
    total_agent1_wins = agent1_wins + agent1_wins_as_o
    total_agent2_wins = agent2_wins + agent2_wins_as_x
    total_draws = draws + draws_as_o
    total_games = num_games * 2

    print("\n--- 総合結果 ---")
    print(f"Agent1 ({q_table_file1}) の総勝利数: {total_agent1_wins} ({total_agent1_wins/total_games:.1%})")
    print(f"Agent2 ({q_table_file2}) の総勝利数: {total_agent2_wins} ({total_agent2_wins/total_games:.1%})")
    print(f"総引き分け数: {total_draws} ({total_draws/total_games:.1%})")


def main():
    parser = argparse.ArgumentParser(description="Evaluate two Q-learning models against each other.")
    parser.add_argument("--model1", type=str, required=True, help="Path to the first Q-table JSON file.")
    parser.add_argument("--model2", type=str, required=True, help="Path to the second Q-table JSON file.")
    parser.add_argument("--num_games", type=int, default=100, help="Number of games to play for each matchup.")
    args = parser.parse_args()

    evaluate_models(args.model1, args.model2, args.num_games)


if __name__ == "__main__":
    main()
