from core.task import init_pointNavTask
from config.nav_node_info import coordinates, node_infos, connection_matrix


def run_task(task_id, content):
    episode = init_pointNavTask(task_id, "Point2PointNav_trial_1", "INIT", content,
                                coordinates, node_infos, connection_matrix)
    print(f"Task started: {episode}")
    episode.run()


if __name__ == "__main__":
    run_task("123", "Hello World")
    