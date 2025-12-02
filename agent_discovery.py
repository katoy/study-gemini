# agent_discovery.py
import os
import importlib
import inspect
from agents.base_agent import BaseAgent

AGENT_ALIASES = {"Random": "ランダム"}


def get_agent_details():
    """
    agentsディレクトリからエージェントを動的に検出し、
    表示用の名前リストと、表示名からクラスオブジェクトへのマッピングを返します。

    Returns:
        tuple[list[str], dict[str, type]]:
            - display_names (list): UIで表示するためのエージェント名のリスト
            - agent_map (dict): 表示名からエージェントクラスオブジェクトへのマッピング
    """
    agent_classes = {}

    agents_dir = "agents"
    if os.path.exists(agents_dir):
        for filename in os.listdir(agents_dir):
            if (
                filename.endswith(".py")
                and not filename.startswith("__")
                and filename != "base_agent.py"
            ):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"agents.{module_name}")
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                            # クラス名から "Agent" を除去して基本名を生成
                            base_name = name.replace("Agent", "")
                            agent_classes[base_name] = obj
                except Exception as e:
                    print(f"Warning: Could not import agent from {module_name}: {e}")

    # 表示名リストとマッピングを作成
    display_names = []
    agent_map = {}

    for base_name, class_obj in sorted(agent_classes.items()):
        display_name = AGENT_ALIASES.get(base_name, base_name)
        display_names.append(display_name)
        agent_map[display_name] = class_obj

    # "ランダム"を先頭に持ってくる
    if "ランダム" in display_names:
        display_names.remove("ランダム")
        display_names.insert(0, "ランダム")

    return display_names, agent_map
