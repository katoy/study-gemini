import unittest
from agents.minimax_agent import MinimaxAgent


class TestMinimaxAgent(unittest.TestCase):
    def setUp(self):
        # ここではエージェントを "O" として初期化（テストケースに合わせる）
        self.agent = MinimaxAgent("O")

    def test_get_move_winning_move(self):
        """勝ち手が複数ある場合、即勝利できる手が選択されるか"""
        board = [["O", "O", " "], ["X", "X", " "], [" ", " ", " "]]
        # エージェント "O" は (0,2) に置けば即勝利
        move = self.agent.get_move(board)
        self.assertEqual(move, (0, 2))

    def test_get_move_blocking_move(self):
        """相手の勝利を防ぐために、ブロックする手が選ばれるか"""
        board = [["X", "X", " "], ["O", " ", " "], [" ", " ", " "]]
        # 相手 "X" の勝利を防ぐため、エージェント "O" は (0,2) を選択すべき
        move = self.agent.get_move(board)
        self.assertEqual(move, (0, 2))

    def test_get_move_draw_move(self):
        """引き分けになる局面で、有効な手が選ばれるか"""
        board = [["X", "O", "X"], ["X", "O", " "], ["O", "X", " "]]
        move = self.agent.get_move(board)
        # 複数の有効手が考えられるため、全セルの中にあるかチェック
        self.assertIn(move, [(1, 2), (2, 2)])

    def test_get_move_immediate_win(self):
        """即座に勝てる手がある場合、その手が選ばれるか"""
        board = [["O", "O", " "], ["X", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (0, 2))

    def test_get_move_avoid_immediate_loss(self):
        """相手の即勝利を防ぐ手が選ばれるか"""
        board = [["X", "X", " "], ["O", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (0, 2))

    def test_get_move_empty_board(self):
        """空の盤面で、どの手も有効な手として選ばれるか"""
        board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertIn(move, [(i, j) for i in range(3) for j in range(3)])

    def test_get_move_full_board(self):
        """盤面が埋まっている場合、None が返るか"""
        board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]
        move = self.agent.get_move(board)
        self.assertIsNone(move)

    def test_minimax_win(self):
        """エージェント側の勝利が確定している場合、評価値が正となるか"""
        board = [["O", "O", "O"], ["X", "X", " "], [" ", " ", " "]]
        score = self.agent.minimax(board, 0, True)
        self.assertEqual(score, 100)

    def test_minimax_lose(self):
        """相手側の勝利が確定している場合、評価値が負となるか"""
        board = [["X", "X", "X"], ["O", "O", " "], [" ", " ", " "]]
        score = self.agent.minimax(board, 0, True)
        self.assertEqual(score, -100)

    def test_minimax_draw(self):
        """引き分けの場合、評価値が0となるか"""
        board = [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]]
        score = self.agent.minimax(board, 0, True)
        self.assertEqual(score, 0)

    def test_minimax_ongoing(self):
        """ゲームが進行中の場合、評価値が整数で返るか"""
        board = [["X", "O", " "], ["X", " ", " "], [" ", " ", " "]]
        score = self.agent.minimax(board, 0, True)
        self.assertIsInstance(score, int)

    def test_get_move_specific_pattern(self):
        """
        特定の盤面パターンで、エージェントが期待する手を選ぶかテストする。
        例: [X, O, X], [ , O, ], [O, X, X] の場合、(1, 2) が最適手と予想する
        """
        board = [["X", "O", "X"], [" ", "O", " "], ["O", "X", "X"]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (1, 2))

    def test_get_move_specific_pattern2(self):
        """
        盤面に先手の "X" がある場合、エージェント "O" の最適な手が中央 (1,1) となる例
        例: [X,  , ], [ ,  , ], [ ,  , ]
        """
        board = [["X", " ", " "], [" ", " ", " "], [" ", " ", " "]]
        move = self.agent.get_move(board)
        self.assertEqual(move, (1, 1))


if __name__ == "__main__":
    unittest.main()
