import unittest
from unittest.mock import MagicMock, patch, call, PropertyMock
import sys
from train_q_learning import (
    train_q_learning_agent,
    main,
)
from agents.q_learning_agent import QLearningAgent


class TestTrainQLearning(unittest.TestCase):
    def setUp(self):
        """テストのセットアップ"""
        self.mock_game = MagicMock()
        self.mock_agent = MagicMock()

    @patch("train_q_learning.PerfectAgent")
    @patch("train_q_learning.TicTacToe")
    @patch("train_q_learning.QLearningAgent")
    @patch("train_q_learning.tqdm")
    def test_train_q_learning_agent_loop_and_reset(
        self, mock_tqdm, mock_agent_class, mock_game_class, mock_perfect_agent_class
    ):
        """学習ループが実行され、Qテーブルがリセットされることを確認"""
        mock_agent = MagicMock()
        mock_agent.exploration_rate = 0.05  # フォーマット可能な float 値を設定
        mock_agent_class.return_value = mock_agent
        mock_agent.q_table = {"initial": 1}  # 初期状態を模倣

        mock_game_instance = MagicMock()
        num_episodes = 2
        # game_over をプロパティとしてモックし、side_effectで複数回値を返す
        type(mock_game_instance).game_over = PropertyMock(
            side_effect=[False, False, True] * num_episodes
        )
        mock_game_instance.check_winner.return_value = None
        mock_game_class.return_value = mock_game_instance

        # get_current_agent が QAgent と Opponent を交互に返すように設定
        mock_opponent = MagicMock()
        mock_perfect_agent_class.return_value = mock_opponent
        mock_game_instance.get_current_agent.side_effect = [
            mock_agent,
            mock_opponent,
        ] * num_episodes

        # QAgent と Opponent の get_move が None でない値を返すように設定
        mock_agent.get_move.return_value = (0, 0)
        mock_opponent.get_move.return_value = (1, 1)

        mock_tqdm.return_value = range(num_episodes)

        train_q_learning_agent(num_episodes, continue_training=False)

        # Qテーブルがリセットされたことを確認
        self.assertEqual(mock_agent.q_table, {})

        # ループ内で各メソッドが呼ばれたかを確認
        # 各エピソードでq_agentのターンは1回なので、num_episodes回呼ばれる
        self.assertEqual(mock_agent.update_q_table.call_count, num_episodes)
        self.assertEqual(mock_agent.decay_exploration_rate.call_count, num_episodes)
        mock_agent.save_q_table.assert_called_once()

    @patch("train_q_learning.TicTacToe")
    @patch("train_q_learning.QLearningAgent")
    @patch("train_q_learning.tqdm")
    def test_train_q_learning_agent_continue(
        self, mock_tqdm, mock_agent_class, mock_game_class
    ):
        """continue_training=Trueの場合、Qテーブルを初期化しない"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        original_q_table = {"test": 1}
        mock_agent.q_table = original_q_table
        mock_agent.exploration_rate = 0.05  # 実数値を設定
        mock_agent.get_move.return_value = (0, 0)
        mock_agent.board_to_string.return_value = "         "
        mock_agent.get_available_moves.return_value = []

        mock_game = MagicMock()
        mock_game.game_over = True  # すぐに終了
        mock_game.check_winner.return_value = None
        mock_game.agent = mock_agent
        mock_game_class.return_value = mock_game

        mock_tqdm.return_value = range(2)  # 2エピソードだけテスト

        train_q_learning_agent(2, continue_training=True)  # num_episodes を 2 に変更

        # Qテーブルが初期化されていないことを確認
        self.assertNotEqual(mock_agent.q_table, {})

    @patch("sys.argv", ["train_q_learning.py", "--episodes", "100"])
    @patch("train_q_learning.train_q_learning_agent")
    def test_main_with_episodes(self, mock_train):
        """--episodesオプションが正しく渡される"""
        main()
        mock_train.assert_called_once_with(100, False)

    @patch(
        "sys.argv", ["train_q_learning.py", "--episodes", "50", "--continue_training"]
    )
    @patch("train_q_learning.train_q_learning_agent")
    def test_main_with_continue(self, mock_train):
        """--continue_trainingオプションが正しく渡される"""
        main()
        mock_train.assert_called_once_with(50, True)

    @patch("train_q_learning.PerfectAgent")
    @patch("train_q_learning.TicTacToe")
    @patch("train_q_learning.QLearningAgent")
    @patch("train_q_learning.tqdm")
    def test_train_q_learning_agent_winner(
        self, mock_tqdm, mock_agent_class, mock_game_class, mock_perfect_agent_class
    ):
        """Q学習エージェントが勝利した場合の報酬計算をテスト"""
        mock_agent = MagicMock()
        mock_agent.player = "X"
        mock_agent.exploration_rate = 0.05
        mock_agent_class.return_value = mock_agent

        mock_game_instance = MagicMock()
        # game_over の side_effect を調整
        type(mock_game_instance).game_over = PropertyMock(side_effect=[False, True])
        # check_winner が q_agent の勝利を返すように設定
        mock_game_instance.check_winner.return_value = mock_agent.player
        mock_game_class.return_value = mock_game_instance

        mock_opponent = MagicMock()
        mock_perfect_agent_class.return_value = mock_opponent
        # 最初のターンは q_agent
        mock_game_instance.get_current_agent.return_value = mock_agent

        mock_agent.get_move.return_value = (0, 0)

        mock_tqdm.return_value = range(1)

        train_q_learning_agent(1, continue_training=False)

        # update_q_table が勝利報酬 (100) で呼ばれたことを確認
        # reward は 100 - 0.1 = 99.9
        args, kwargs = mock_agent.update_q_table.call_args
        self.assertAlmostEqual(args[2], 99.9)

    @patch("train_q_learning.PerfectAgent")
    @patch("train_q_learning.TicTacToe")
    @patch("train_q_learning.QLearningAgent")
    @patch("train_q_learning.tqdm")
    def test_train_q_learning_agent_no_move(
        self, mock_tqdm, mock_agent_class, mock_game_class, mock_perfect_agent_class
    ):
        """get_moveがNoneを返した場合にループが中断されることをテスト"""
        mock_agent = MagicMock()
        mock_agent.exploration_rate = 0.05
        mock_agent_class.return_value = mock_agent

        mock_game_instance = MagicMock()
        type(mock_game_instance).game_over = PropertyMock(return_value=False)
        mock_game_instance.check_winner.return_value = None
        mock_game_class.return_value = mock_game_instance

        mock_opponent = MagicMock()
        mock_perfect_agent_class.return_value = mock_opponent
        mock_game_instance.get_current_agent.return_value = mock_agent

        # get_move が None を返すように設定
        mock_agent.get_move.return_value = None

        mock_tqdm.return_value = range(1)

        train_q_learning_agent(1, continue_training=False)

        # update_q_table が呼ばれていないことを確認
        mock_agent.update_q_table.assert_not_called()

    @patch("train_q_learning.PerfectAgent")
    @patch("train_q_learning.TicTacToe")
    @patch("train_q_learning.QLearningAgent")
    @patch("train_q_learning.tqdm")
    def test_train_q_learning_agent_draw(
        self, mock_tqdm, mock_agent_class, mock_game_class, mock_perfect_agent_class
    ):
        """引き分けの場合の報酬計算をテスト"""
        mock_agent = MagicMock()
        mock_agent.player = "X"
        mock_agent.exploration_rate = 0.05
        mock_agent_class.return_value = mock_agent

        mock_game_instance = MagicMock()
        type(mock_game_instance).game_over = PropertyMock(side_effect=[False, True])
        mock_game_instance.check_winner.return_value = "draw"
        mock_game_class.return_value = mock_game_instance

        mock_game_instance.get_current_agent.return_value = mock_agent
        mock_agent.get_move.return_value = (0, 0)
        mock_tqdm.return_value = range(1)

        train_q_learning_agent(1, continue_training=False)

        # reward は 75 - 0.1 = 74.9
        args, kwargs = mock_agent.update_q_table.call_args
        self.assertAlmostEqual(args[2], 74.9)

    @patch("train_q_learning.PerfectAgent")
    @patch("train_q_learning.TicTacToe")
    @patch("train_q_learning.QLearningAgent")
    @patch("train_q_learning.tqdm")
    def test_train_q_learning_agent_loss(
        self, mock_tqdm, mock_agent_class, mock_game_class, mock_perfect_agent_class
    ):
        """敗北の場合の報酬計算をテスト"""
        mock_agent = MagicMock()
        mock_agent.player = "X"
        mock_agent.exploration_rate = 0.05
        mock_agent_class.return_value = mock_agent

        mock_game_instance = MagicMock()
        type(mock_game_instance).game_over = PropertyMock(side_effect=[False, True])
        mock_game_instance.check_winner.return_value = "O"  # Opponent's win
        mock_game_class.return_value = mock_game_instance

        mock_game_instance.get_current_agent.return_value = mock_agent
        mock_agent.get_move.return_value = (0, 0)
        mock_tqdm.return_value = range(1)

        train_q_learning_agent(1, continue_training=False)

        # reward は -200 - 0.1 = -200.1
        args, kwargs = mock_agent.update_q_table.call_args
        self.assertAlmostEqual(args[2], -200.1)


if __name__ == "__main__":
    unittest.main()
