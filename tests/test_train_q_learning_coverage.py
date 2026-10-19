"""train_q_learning.py の未カバー分岐を補うテスト。"""

from unittest.mock import MagicMock, PropertyMock, patch

from train_q_learning import train_q_learning_agent


@patch("train_q_learning.PerfectAgent")
@patch("train_q_learning.TicTacToe")
@patch("train_q_learning.QLearningAgent")
@patch("train_q_learning.tqdm")
def test_train_q_learning_agent(
    mock_tqdm, mock_agent_class, mock_game_class, mock_perfect_agent_class
):
    """対戦相手が手を返さない場合はエピソードのループを抜ける。"""
    mock_agent = MagicMock()
    mock_agent.exploration_rate = 0.05
    mock_agent.q_table = {}
    mock_agent_class.return_value = mock_agent

    mock_opponent = MagicMock()
    mock_opponent.get_move.return_value = None
    mock_perfect_agent_class.return_value = mock_opponent

    mock_game = MagicMock()
    type(mock_game).game_over = PropertyMock(return_value=False)
    mock_game.get_current_agent.return_value = mock_opponent
    mock_game_class.return_value = mock_game

    mock_tqdm.return_value = range(1)

    with patch("builtins.print"):
        train_q_learning_agent(1, continue_training=True)

    mock_opponent.get_move.assert_called_once()
    mock_game.make_move.assert_not_called()
    mock_game.switch_player.assert_not_called()
    mock_agent.decay_exploration_rate.assert_called_once_with(0, 1)
    mock_agent.save_q_table.assert_called_once()
