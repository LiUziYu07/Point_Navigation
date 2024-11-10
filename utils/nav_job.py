from core.task import PointNav
from config.nav_node_info import coordinates, node_infos, connection_matrix, uuid2timestamp
from config.api import GPT_MODEL
from prompt.prompts import SYSTEM_PRINCIPLE
from llm.gpt_client import GPTClient


def run_task(task_id, content):
    task_type = "PointNav"
    episode = PointNav(task_id, "PointNav_trial_1",  "", "INIT",
                                coordinates, node_infos, connection_matrix, uuid2timestamp)
    print(f"Task started: {episode}")
    print(content)
    episode.test()
    client = GPTClient(task=episode, task_type=task_type, model=GPT_MODEL, sys_msgs=SYSTEM_PRINCIPLE)
    client.run(instructions=content)


if __name__ == "__main__":
    run_task("123", "Hello World")
    