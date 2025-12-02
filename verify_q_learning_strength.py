import argparse
from tqdm import tqdm
from game_logic import TicTacToe
from agents.q_learning_agent import QLearningAgent
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.perfect_agent import PerfectAgent


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Verify the strength of a Q-learning agent."
    )
    parser.add_argument(
        "--num_games",
        type=int,
        default=10,
        help="Number of games to play for each evaluation.",
    )
    return parser.parse_args()


def evaluate(q_agent_player: str, opponent_class, opponent_name: str, num_games: int):
    """
    Evaluates the Q-learning agent against an opponent.

    Args:
        q_agent_player (str): The player symbol for the Q-learning agent ('X' or 'O').
        opponent_class: The class of the opponent agent.
        opponent_name (str): The name of the opponent agent.
        num_games (int): The number of games to play.
    """
    wins = draws = losses = 0
    q_agent = QLearningAgent(player=q_agent_player, is_training=False)
    opponent_player = "O" if q_agent_player == "X" else "X"
    opponent_agent = opponent_class(player=opponent_player)

    if q_agent_player == "X":
        agent_x, agent_o = q_agent, opponent_agent
    else:
        agent_x, agent_o = opponent_agent, q_agent

    for _ in tqdm(
        range(num_games),
        desc=f"Q-Agent({q_agent_player}) vs {opponent_name}({opponent_player})",
    ):
        game = TicTacToe(agent_x=agent_x, agent_o=agent_o)

        while not game.game_over:
            current_agent = game.get_current_agent()
            move = current_agent.get_move(game.board)

            if move is None:
                if game.current_player == q_agent_player:
                    losses += 1
                else:
                    wins += 1
                break

            game.make_move(row=move[0], col=move[1])
            winner = game.check_winner()
            if winner:
                if winner == q_agent_player:
                    wins += 1
                elif winner == "draw":
                    draws += 1
                else:
                    losses += 1
                break

            game.switch_player()

    print(f"\n--- Q-Agent({q_agent_player}) vs {opponent_name}({opponent_player}) ---")
    print(f"勝ち: {wins} ({wins/num_games*100:.1f}%)")
    print(f"負け: {losses} ({losses/num_games*100:.1f}%)")
    print(f"引き分け: {draws} ({draws/num_games*100:.1f}%)")


def main():
    """Main function to run the evaluation."""
    args = parse_args()
    print("=== 強さ検証レポート ===")
    print(f"総エピソード数: {args.num_games}回/対戦")

    print("\n\n--- Q-Agentが先手 ('X') の場合 ---")
    evaluate("X", RandomAgent, "RandomAgent", args.num_games)
    evaluate("X", MinimaxAgent, "MinimaxAgent", args.num_games)
    evaluate("X", PerfectAgent, "PerfectAgent", args.num_games)

    print("\n\n--- Q-Agentが後手 ('O') の場合 ---")
    evaluate("O", RandomAgent, "RandomAgent", args.num_games)
    evaluate("O", MinimaxAgent, "MinimaxAgent", args.num_games)
    evaluate("O", PerfectAgent, "PerfectAgent", args.num_games)


if __name__ == "__main__":
    main()
