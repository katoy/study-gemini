import pytest
from unittest.mock import MagicMock, patch

# tkinterがインストールされていない環境でもテストを実行できるように、
# 実際にインポートする前にモックする
try:
    import tkinter as tk
except ImportError:
    tk = MagicMock()

@pytest.fixture
def mock_master():
    """tkinterのrootウィンドウのモックを提供するフィクスチャ"""
    master = MagicMock(spec=tk.Tk)
    return master

@pytest.fixture
def gui(mock_master):
    """TicTacToeGUIのインスタンスを提供するフィクスチャ（一部モック済み）"""
    sys_modules = {
        'tkinter': MagicMock(),
        'tkinter.font': MagicMock()
    }
    with patch.dict('sys.modules', sys_modules):
        from gui import TicTacToeGUI
        with patch('gui.SettingsUI') as MockSettingsUI, \
             patch('gui.BoardDrawer') as MockBoardDrawer, \
             patch('gui.GameInfoUI') as MockGameInfoUI, \
             patch('gui.TicTacToe') as MockTicTacToe:
            
            # モックの設定
            mock_settings_ui = MockSettingsUI.return_value
            mock_settings_ui.player_var.get.return_value = True  # Human plays X
            mock_settings_ui.agent_var.get.return_value = "Minimax"
            
            # guiインスタンスの生成
            gui_instance = TicTacToeGUI(mock_master)
            
            # モックをインスタンスにアタッチして、テスト内でアクセスできるようにする
            gui_instance.mock_settings_ui = mock_settings_ui
            gui_instance.mock_board_drawer = MockBoardDrawer.return_value
            gui_instance.mock_game_info_ui = MockGameInfoUI.return_value
            gui_instance.mock_tictactoe_class = MockTicTacToe
            gui_instance.mock_game = MockTicTacToe.return_value
            
            yield gui_instance

def test_gui_initialization(gui):
    """GUIの初期化をテストする"""
    gui.master.title.assert_called_with("三目並べ")
    gui.mock_settings_ui.build_settings_ui.assert_called_once()

def test_start_game_human_starts(gui):
    """人間が先手（X）でゲームを開始するケースをテストする"""
    gui.start_game()

    # 正しいエージェントでTicTacToeが初期化されたか
    gui.mock_tictactoe_class.assert_called_once()
    args, kwargs = gui.mock_tictactoe_class.call_args
    assert kwargs['human_player'] == 'X'
    assert kwargs['agent_x'] is None
    # MinimaxAgentのインスタンスであることを確認
    assert kwargs['agent_o'].__class__.__name__ == 'MinimaxAgent'

    # UI関連のメソッドが呼ばれたか
    gui.mock_board_drawer.draw_board.assert_called_once()
    gui.mock_game_info_ui.show_game_info.assert_called_once()

    # AIの先行手番メソッドが呼ばれていないことを確認
    assert not hasattr(gui, 'agent_first_move_mock') or not gui.agent_first_move_mock.called

def test_start_game_ai_starts(gui):
    """AIが先手（X）でゲームを開始するケースをテストする"""
    # 設定を変更
    gui.mock_settings_ui.player_var.get.return_value = False # AI plays X

    # agent_first_move をモック
    gui.agent_first_move = MagicMock()

    gui.start_game()

    # 正しいエージェントでTicTacToeが初期化されたか
    gui.mock_tictactoe_class.assert_called_once()
    args, kwargs = gui.mock_tictactoe_class.call_args
    assert kwargs['human_player'] == 'O'
    assert kwargs['agent_o'] is None
    # MinimaxAgentのインスタンスであることを確認
    assert kwargs['agent_x'].__class__.__name__ == 'MinimaxAgent'

    # AIの先行手番メソッドが呼ばれたことを確認
    gui.agent_first_move.assert_called_once()

def test_on_canvas_click(gui):
    """キャンバスのクリックがcell_clickedに正しく渡されるかテスト"""
    gui.start_game()
    # 人間のターンにする
    gui.mock_game.current_player = "X"
    gui.mock_game.human_player = "X"
    
    gui.cell_clicked = MagicMock()
    
    # (150, 250) をクリック -> (2, 1) のセル
    event = MagicMock()
    event.x = 150
    event.y = 250
    gui.on_canvas_click(event)

    gui.cell_clicked.assert_called_once_with(2, 1)

def test_cell_clicked_human_turn(gui):
    """人間のターンにセルがクリックされた場合の処理をテスト"""
    gui.start_game()
    gui.mock_game.current_player = "X"
    gui.mock_game.human_player = "X"
    gui.mock_game.game_over = False
    gui.mock_game.make_move.return_value = True # 有効な手
    gui.mock_game.check_winner.return_value = None # 勝者なし

    # agent_turnをモック
    gui.agent_turn = MagicMock()
    # draw_board の呼び出し履歴をリセット
    gui.mock_board_drawer.draw_board.reset_mock()

    gui.cell_clicked(1, 1)

    gui.mock_game.make_move.assert_called_once_with(1, 1)
    gui.mock_board_drawer.draw_board.assert_called_once()
    gui.mock_game.switch_player.assert_called_once()
    gui.agent_turn.assert_called_once()

def test_cell_clicked_game_over(gui):
    """ゲーム終了時にセルがクリックされても何も起こらないことをテスト"""
    gui.start_game()
    gui.mock_game.game_over = True
    
    gui.cell_clicked(0, 0)

    gui.mock_game.make_move.assert_not_called()

def test_agent_turn(gui):
    """エージェントのターンの処理をテスト"""
    gui.start_game()
    # エージェントのターンにする
    agent_mock = gui.mock_game.agent_o
    gui.mock_game.current_player = "O"
    gui.mock_game.agent_player = "O"
    gui.mock_game.get_current_agent.return_value = agent_mock
    agent_mock.get_move.return_value = (2, 2)
    gui.mock_game.make_move.return_value = True
    gui.mock_game.check_winner.return_value = None # 勝者なし

    # draw_board の呼び出し履歴をリセット
    gui.mock_board_drawer.draw_board.reset_mock()

    gui.agent_turn()

    agent_mock.get_move.assert_called_once_with(gui.mock_game.board)
    gui.mock_game.make_move.assert_called_once_with(2, 2)
    gui.mock_board_drawer.draw_board.assert_called_once()
    gui.mock_game.switch_player.assert_called_once()

def test_game_over_winner(gui):
    """勝者が決まってゲームが終了するケースをテスト"""
    gui.start_game()
    # ラベルのモックを取得
    mock_label = gui.result_label
    mock_label.pack.reset_mock()
    
    gui.game_over("X")

    gui.canvas.unbind.assert_called_with("<Button-1>")
    mock_label.config.assert_called_with(text="Xの勝ちです！")
    mock_label.pack.assert_called_once()

def test_game_over_draw(gui):
    """引き分けでゲームが終了するケースをテスト"""
    gui.start_game()
    mock_label = gui.result_label
    mock_label.pack.reset_mock()
    # winner_lineがない場合をシミュレート
    gui.mock_game.winner_line = None
    
    gui.game_over("draw")

    gui.canvas.unbind.assert_called_with("<Button-1>")
    # highlight_winner_cellsが呼ばれないことを確認
    gui.mock_board_drawer.highlight_winner_cells.assert_not_called()
    mock_label.config.assert_called_with(text="引き分けです！")
    mock_label.pack.assert_called_once()

@pytest.mark.parametrize("agent_name, expected_class_name", [
    ("ランダム", "RandomAgent"),
    ("Minimax", "MinimaxAgent"),
    ("Database", "DatabaseAgent"),
    ("Perfect", "PerfectAgent"),
    ("QLearning", "QLearningAgent"),
    ("Unknown", "NoneType"),
])
def test_create_agent_instance(gui, agent_name, expected_class_name):
    """_create_agent_instanceが正しいエージェントクラスを返すかテスト"""
    agent = gui._create_agent_instance(agent_name, "X")
    assert agent.__class__.__name__ == expected_class_name

def test_play_first_game_and_restart(gui):
    """
    1ゲーム目をプレイし、停止した後に2ゲーム目を正常にプレイできるかテストする。
    """
    # 1. 1ゲーム目をセットアップしてプレイ
    gui.start_game()
    gui.mock_game.current_player = "X"
    gui.mock_game.human_player = "X"
    gui.mock_game.game_over = False
    gui.mock_game.make_move.return_value = True
    gui.mock_game.check_winner.return_value = "X" # Xの勝利
    gui.game_over = MagicMock()

    gui.cell_clicked(0, 0)
    gui.game_over.assert_called_once_with("X")

    # 2. ゲームを停止
    gui.stop_game()

    # 3. モックをリセットして2ゲーム目を準備
    gui.mock_tictactoe_class.reset_mock()
    gui.mock_game.reset_mock()
    gui.mock_board_drawer.reset_mock()
    gui.mock_game_info_ui.reset_mock()
    
    # 4. 2ゲーム目をスタート
    gui.start_game()

    # 2ゲーム目が正しく初期化されたことを確認
    gui.mock_tictactoe_class.assert_called_once()
    gui.mock_board_drawer.draw_board.assert_called_once()
    gui.mock_game_info_ui.show_game_info.assert_called_once()

    # 5. 2ゲーム目をプレイできることを確認
    gui.mock_game.current_player = "X"
    gui.mock_game.human_player = "X"
    gui.mock_game.game_over = False
    gui.mock_game.make_move.return_value = True
    gui.mock_game.check_winner.return_value = None
    gui.agent_turn = MagicMock()

    gui.cell_clicked(1, 1)
    gui.mock_game.make_move.assert_called_once_with(1, 1)
    gui.agent_turn.assert_called_once()
