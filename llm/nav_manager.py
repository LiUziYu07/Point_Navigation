from navPoint_function import ToolNavigate as PointNavigate, ToolViewpointGet, ToolSurroundingDetect
from core.task import PointNav
from config.nav_node_info import coordinates, node_infos, connection_matrix, uuid2timestamp


class ToolManager:
    def __init__(self, task_type: str):
        self.tool_dict = {}
        self.task_type = task_type
        self.generate_tools_dict()

    def generate_tools_dict(self):
        # 根据 task_type 生成工具字典
        tools = {
            'surrounding_detect': ToolSurroundingDetect(),
            'navigate': PointNavigate(),
            'viewpoint_get': ToolViewpointGet(),
        }
        self.tool_dict = tools

    def execute(self, tool_name: str, tool_args: dict, task: str = None):
        # 优化的工具执行方法
        try:
            tool = self.tool_dict.get(tool_name)

            if tool and task:
                msgs = tool.execute(task, tool_args)
            else:
                return f"Unrecognized command: {tool_name}"
        except Exception as e:
            msgs = f"Error during execution: {e}"

        return msgs

    def get_tools_usages(self):
        usages = []
        for _, tool in self.tool_dict.items():
            usages.append(tool.get_description())
        return usages


if __name__ == '__main__':
    tool_manager = ToolManager('pointNav')

    task = PointNav(1, "Point2PointNav", "Go out and see a walkway, then turn right toward the door", "IN_PROGRESS",
                    coordinates, node_infos, connection_matrix, uuid2timestamp)
    start_viewpoint = next(vp_id for vp_id, coords in task.viewpoints.items())
    end_viewpoint = next(vp_id for vp_id, coords in task.viewpoints.items() if vp_id == list(task.viewpoints.keys())[1])

    tool_name = "navigate"
    tool_args = f'{{"starting_point": "{start_viewpoint}", "ending_point": "{end_viewpoint}", "rotate_degree": 90}}'
    msgs = tool_manager.execute(tool_name, tool_args, task=task)
    print(msgs)
