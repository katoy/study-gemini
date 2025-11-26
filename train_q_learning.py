import argparse
from tqdm import tqdm
import os
from game_logic import TicTacToe
from agents.q_learning_agent import QLearningAgent
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.perfect_agent import PerfectAgent
# fast_trainer is used by QLearningAgent internally

def train_q_learning_agent(num_episodes, continue_training):
    """Trains the Q-learning agent using the fast Cython module."""
    q_agent = QLearningAgent(player='X', is_training=True) # This is a wrapper
    if not continue_training and not os.getenv('PYTEST_CURRENT_TEST'):
        print("Starting new training. Resetting Q-table.")
        q_agent.q_table = {}

    for episode in tqdm(range(num_episodes), desc="Training Q-Agent", unit="episode"):
        player_symbol = 'X' if episode % 2 == 0 else 'O'
        q_agent.player = player_symbol
        
        opponent_player = 'O' if player_symbol == 'X' else 'X'
        opponent = PerfectAgent(player=opponent_player)
        
        # --- Start of inlined train_episode ---
        if player_symbol == 'X':
            game = TicTacToe(agent_x=q_agent, agent_o=opponent)
        else:
            game = TicTacToe(agent_x=opponent, agent_o=q_agent)

        while not game.game_over:
            current_agent = game.get_current_agent()
            is_q_agent_turn = (current_agent is q_agent)

            if is_q_agent_turn:
                state_str = "".join(cell for row in game.board for cell in row)
                move = q_agent.get_move(game.board) 
                if move is None: break
                action = move[0] * 3 + move[1]
                
                game.make_move(move[0], move[1])
                winner = game.check_winner()

                reward = 0
                intermediate_reward = -0.1 # 中間報酬の導入
                if winner:
                    if winner == q_agent.player: reward = 100
                    elif winner == 'draw': reward = 75
                    else: reward = -200
                reward += intermediate_reward # 中間報酬を加算
                
                next_state_str = "".join(cell for row in game.board for cell in row)
                # Delegate to the fast update method
                q_agent.update_q_table(state_str, action, reward, next_state_str, bool(winner))

            else: # Opponent's turn
                move = opponent.get_move(game.board)
                if move is None: break
                game.make_move(move[0], move[1])
                winner = game.check_winner()
            
            if winner:
                break
            
            game.switch_player()
        # --- End of inlined train_episode ---

        q_agent.decay_exploration_rate(episode, num_episodes)

    q_agent.save_q_table()
    print("\n✅ Training complete.")
    print(f"  - Q-table size: {len(q_agent.q_table)} states")
    print(f"  - Final exploration rate: {q_agent.exploration_rate:.4f}")

def main():
    parser = argparse.ArgumentParser(description="Train Q-Learning agent for Tic Tac Toe.")
    parser.add_argument("--episodes", type=int, default=100000, help="Number of training episodes.") # 5000 -> 100000
    parser.add_argument("--continue_training", action="store_true", help="Continue training from existing Q-table.")
    args = parser.parse_args()
    train_q_learning_agent(args.episodes, args.continue_training)

if __name__ == "__main__":
    main()
