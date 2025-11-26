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
        


    @patch('train_q_learning.TicTacToe')
    @patch('train_q_learning.QLearningAgent')
    @patch('train_q_learning.tqdm')
    @patch('builtins.print')
    def test_train_q_learning_agent(self, mock_print, mock_tqdm, mock_agent_class, mock_game_class):
        """学習関数が正しく動作するか"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # PropertyMock を使って exploration_rate の値を変更可能にする
        type(mock_agent).exploration_rate = PropertyMock(return_value=0.05)
        type(mock_agent).min_exploration_rate = 0.01 # min_exploration_rate も設定
        # exploration_rate の実際の値は decay_exploration_rate で更新されるので、
        # ここでは初期値を設定し、テストの最後で最終的な値をアサートします。
        
        # q_agent.player の初期値を設定（train_q_learning_agent 内で上書きされる）
        mock_agent.player = 'X' 
        
        mock_game_instance = MagicMock(game_over=True, check_winner=MagicMock(return_value=None))
        mock_game_class.return_value = mock_game_instance # TicTacToe のモックインスタンスを設定
        
        mock_tqdm.return_value = range(2)
        
        train_q_learning_agent(2, continue_training=False)
        
        mock_agent.save_q_table.assert_called_once()
        mock_print.assert_called()
        
        # q_agent.player が 'O' になったことを確認 (2エピソードなので最終的には 'O' になる)
        self.assertEqual(mock_agent.player, 'O')
        



    @patch('train_q_learning.TicTacToe')
    @patch('train_q_learning.QLearningAgent')
    @patch('train_q_learning.tqdm')
    def test_train_q_learning_agent_continue(self, mock_tqdm, mock_agent_class, mock_game_class):
        """continue_training=Trueの場合、Qテーブルを初期化しない"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        original_q_table = {"test": 1}
        mock_agent.q_table = original_q_table
        mock_agent.exploration_rate = 0.05 # 実数値を設定
        mock_agent.get_move.return_value = (0, 0)
        mock_agent.board_to_string.return_value = "         "
        mock_agent.get_available_moves.return_value = []
        
        mock_game = MagicMock()
        mock_game.game_over = True  # すぐに終了
        mock_game.check_winner.return_value = None
        mock_game.agent = mock_agent
        mock_game_class.return_value = mock_game
        
        mock_tqdm.return_value = range(2) # 2エピソードだけテスト
        
        train_q_learning_agent(2, continue_training=True) # num_episodes を 2 に変更
        
        # Qテーブルが初期化されていないことを確認
        self.assertNotEqual(mock_agent.q_table, {})





    @patch('sys.argv', ['train_q_learning.py', '--episodes', '100'])
    @patch('train_q_learning.train_q_learning_agent')
    def test_main_with_episodes(self, mock_train):
        """--episodesオプションが正しく渡される"""
        main()
        mock_train.assert_called_once_with(100, False)

    @patch('sys.argv', ['train_q_learning.py', '--episodes', '50', '--continue_training'])
    @patch('train_q_learning.train_q_learning_agent')
    def test_main_with_continue(self, mock_train):
        """--continue_trainingオプションが正しく渡される"""
        main()
        mock_train.assert_called_once_with(50, True)


if __name__ == "__main__":
    unittest.main()
