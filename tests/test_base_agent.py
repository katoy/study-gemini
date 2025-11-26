import unittest
from agents.base_agent import BaseAgent


class TestBaseAgent(unittest.TestCase):
    def test_base_agent_init(self):
        """BaseAgentの初期化が正しく機能するか"""
        agent = BaseAgent("X")
        self.assertEqual(agent.player, "X")

    def test_base_agent_get_move_not_implemented(self):
        """BaseAgentのget_moveがNotImplementedErrorを発生させるか"""
        agent = BaseAgent("O")
        with self.assertRaises(NotImplementedError):
            agent.get_move([[" " for _ in range(3)] for _ in range(3)])


if __name__ == "__main__":
    unittest.main()
