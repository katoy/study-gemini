import os
import openai
import random
import logging
import json
from agents.base_agent import BaseAgent

# Configure logging to a file
logging.basicConfig(
    filename="chatgpt_agent_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

print("DEBUG: chatgpt_agent.py is being loaded.")  # Debug print


class ChatGPTAgent(BaseAgent):
    def __init__(
        self, player: str, model: str = "gpt-5.1", num_few_shot_examples: int = 5
    ):
        super().__init__(player)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.board_history = []  # For conversational context
        self.num_few_shot_examples = num_few_shot_examples
        self.few_shot_examples = self._load_few_shot_examples()

    def _load_few_shot_examples(self) -> list[dict]:
        """
        perfect_moves.json からランダムに例を取りつつ、
        「絶対にブロックしないと負ける」ような重要な盤面を手作りで追加する。
        """
        examples: list[dict] = []
        try:
            with open("perfect_moves.json", "r") as f:
                perfect_moves_data = json.load(f)

            valid_moves = {k: v for k, v in perfect_moves_data.items() if v != -1}

            if len(valid_moves) > self.num_few_shot_examples:
                selected_states = random.sample(
                    list(valid_moves.keys()), self.num_few_shot_examples
                )
            else:
                selected_states = list(valid_moves.keys())

            for board_state_str in selected_states:
                move_index = valid_moves[board_state_str]
                row, col = divmod(move_index, 3)

                # board_state_str は 9 文字（X/O/空）と想定
                board_grid_str = ""
                for i in range(0, 9, 3):
                    # 3 文字をそのまま使う: X, O, ' ' 等
                    line = list(board_state_str[i:i + 3])
                    # 空白は '.' に変換して 3 文字にする
                    line = [ch if ch in ["X", "O"] else "." for ch in line]
                    board_grid_str += "".join(line) + "\n"

                x_count = board_state_str.count("X")
                o_count = board_state_str.count("O")
                player_to_move_in_example = "X" if x_count == o_count else "O"

                examples.append(
                    {
                        "board_state": board_grid_str.strip(),  # 例: "O..\nXX.\n..."
                        "player_to_move": player_to_move_in_example,
                        "optimal_move": f"{row},{col}",
                    }
                )
        except FileNotFoundError:
            logging.warning("perfect_moves.json not found for few-shot examples.")
        except json.JSONDecodeError:
            logging.error("Error decoding perfect_moves.json.")
        except Exception as e:
            logging.error(f"Error loading few-shot examples: {e}")

        # ★ 手作りの重要局面を追加（ブロック優先を身につけさせる）★
        handcrafted = [
            # 今回あなたが遭遇したような形:
            # O..
            # XX.
            # ...
            # → O の番なら (1,2) にブロックしないと即負け
            {
                "board_state": "O..\nXX.\n...",
                "player_to_move": "O",
                "optimal_move": "1,2",
            },
            # 縦ブロックの例:
            # O.X
            # .X.
            # O..
            # → X の番なら (2,1) でブロック
            {
                "board_state": "O.X\n.X.\nO..",
                "player_to_move": "X",
                "optimal_move": "2,1",
            },
            # 自分が即勝てる例:
            # OO.
            # .X.
            # X..
            # → O の番なら (0,2) で勝ち
            {
                "board_state": "OO.\n.X.\nX..",
                "player_to_move": "O",
                "optimal_move": "0,2",
            },
        ]

        examples.extend(handcrafted)
        return examples

    def get_move(self, board: list) -> tuple[int, int] | None:
        # ボードを文字列に変換（'.' が空きマス）
        board_str = ""
        for r_idx, row in enumerate(board):
            line = []
            for cell in row:
                if cell == " " or cell == "":
                    line.append(".")
                else:
                    line.append(cell)
            board_str += "".join(line)
            if r_idx < len(board) - 1:
                board_str += "\n"

        # 利用可能な手の一覧
        empty_cells = []
        for r in range(3):
            for c in range(3):
                if board[r][c] == " " or board[r][c] == "":
                    empty_cells.append(f"({r},{c})")

        available_moves_str = ", ".join(empty_cells) if empty_cells else "None"

        logging.debug(f"Current board state for player {self.player}:\n{board_str}")
        logging.debug(f"Available moves: {available_moves_str}")

        # ★ よりアルゴリズム的で厳格な system メッセージ ★
        system_message_content = (
            f"あなたは三目並べの最強AIです。プレイヤー '{self.player}' として、"
            "決して負けないことを唯一の目的とします。\n"
            "\n"
            "あなたは Minimax（c-minimax）戦略に従い、以下のアルゴリズムを厳密に実行してください。"
            "思考は内部だけで行い、出力には一切含めてはいけません。\n"
            "\n"
            "アルゴリズム:\n"
            "1. まず、自分が今すぐ勝てる手があるか全ての合法手について確認する。"
            "   あれば、その中から1手を必ず選ぶ。\n"
            "2. 1 で勝てる手がない場合、相手が次の手で勝てるかどうかを全ての合法手についてシミュレーションする。"
            "   相手の即勝利を防ぐブロック手が存在する場合、必ずその中から1手を選ぶ。\n"
            "3. それ以外の場合、Minimax 戦略に従い、将来の勝ち筋が最大になる手を選ぶ。"
            "   一般的には「中心 > 角 > 辺」の順に価値が高いことを考慮する。\n"
            "\n"
            "ボードは3x3のグリッドで、行と列は0から2。空のマスは '.' で表されます。"
            "既に 'X' または 'O' が置かれているマスには絶対に手を打ってはいけません。\n"
            "合法手は、ユーザーから与えられるリストの中の座標のみです。"
            "そのリストに含まれない座標は、たとえ空いていても選んではいけません。\n"
            "\n"
            "あなたは頭の中でどれだけ詳細に手順を考えても構いませんが、"
            "出力は最終的な1手のみとします。\n"
            "出力形式は厳密に `<move>行,列</move>` の1行だけです（例: `<move>0,0</move>`）。\n"
            "説明文・コメント・余分な文字・空行などは一切出力してはいけません。\n"
            "無効な手、または形式に従わない応答は、AIとしての致命的な失敗と見なされます。"
            "\n"
            "以下に、いくつかのボード状態と最適な手の例を示します。"
        )

        prompt_messages = [{"role": "system", "content": system_message_content}]

        # few-shot 例
        for example in self.few_shot_examples:
            prompt_messages.append(
                {
                    "role": "user",
                    "content": (
                        f"現在のボードの状態:\n{example['board_state']}\n"
                        f"プレイヤー '{example['player_to_move']}' の番です。"
                        f"合法手の中から最善手を1つだけ選んでください。"
                        f"応答は `<move>行,列</move>` の形式のみです。"
                    ),
                }
            )
            prompt_messages.append(
                {
                    "role": "assistant",
                    "content": f"<move>{example['optimal_move']}</move>",
                }
            )

        # 実際の問い合わせ
        prompt_messages.append(
            {
                "role": "user",
                "content": (
                    f"現在のボードの状態:\n{board_str}\n\n"
                    f"利用可能な手は次のとおりです（必ずこの中から選んでください）: {available_moves_str}\n\n"
                    f"上記のボードで、プレイヤー '{self.player}' は次にどこに移動すべきですか？\n"
                    "内部では自由に思考して構いませんが、最終的な出力は厳密に `<move>行,列</move>` の形式で"
                    "1行だけにしてください（例: `<move>0,0</move>`）。\n"
                    "それ以外の文字・説明・空行は絶対に含めないでください。"
                ),
            }
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prompt_messages,
                max_completion_tokens=20,
                temperature=0.0,  # ★ ランダム性を殺す
            )

            logging.debug(f"Raw ChatGPT response: {response}")

            import re

            move_str_raw = response.choices[0].message.content.strip()
            logging.debug(f"Raw ChatGPT response content: '{move_str_raw}'")

            # <move>行,列</move> の中身を取り出す
            match = re.search(r"<move>(.*?)</move>", move_str_raw)
            if match:
                move_str = match.group(1).strip()
            else:
                logging.error(
                    f"Could not find <move> tags in response: '{move_str_raw}'. "
                    f"Board state:\n{board_str}"
                )
                return self._find_random_valid_move(board)

            logging.debug(f"Parsed move string from ChatGPT: '{move_str}'")

            try:
                row, col = map(int, move_str.split(","))
                logging.debug(f"Parsed move: ({row}, {col})")
            except ValueError:
                logging.error(
                    f"ChatGPT returned an unparseable move string: '{move_str}'. "
                    f"Board state:\n{board_str}"
                )
                return self._find_random_valid_move(board)

            # 有効手かチェック
            if (
                0 <= row < 3
                and 0 <= col < 3
                and (board[row][col] == " " or board[row][col] == "")
            ):
                logging.info(f"ChatGPT suggested valid move: ({row}, {col})")
                return row, col
            else:
                logging.warning(
                    f"ChatGPT returned an invalid move: {move_str}. Board state:\n{board_str}. "
                    "Falling back to random move."
                )
                return self._find_random_valid_move(board)

        except Exception as e:
            logging.error(f"Error calling ChatGPT API or parsing response: {e}")
            return self._find_random_valid_move(board)

    def _find_random_valid_move(self, board: list) -> tuple[int, int] | None:
        empty_cells = []
        for r in range(3):
            for c in range(3):
                if board[r][c] == " " or board[r][c] == "":
                    empty_cells.append((r, c))
        if empty_cells:
            move = random.choice(empty_cells)
            logging.info(f"Falling back to random valid move: {move}")
            return move
        logging.error(
            "No empty cells found for fallback. This should not happen in a valid game."
        )
        return None
