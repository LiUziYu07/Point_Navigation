from graph.node import Node, Map
from core.actions import generate_action_space
from config.nav_node_info import coordinates, node_infos, connection_matrix, uuid2timestamp
from config.api import MODEL
from enum import Enum


class Status(Enum):
    INIT = "INIT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Task:
    def __init__(self, task_id, description, status):
        self.task_id = task_id
        self.description = description
        self.status = Status(status)

    def update_status(self, status):
        self.status = status

    def update_task_description(self, description):
        self.description = description

    def __str__(self):
        return f"Task ID: {self.task_id}, Description: {self.description}, Status: {self.status}"


class PointNav(Task):
    def __init__(self, task_id, description, instructions, status, coordinates, node_infos, connection_matrix, uuid2timestamp):
        super().__init__(task_id, description, status)
        self.coordinates = coordinates
        self.node_infos = node_infos
        self.instructions = instructions
        self.uuid2timestamp = uuid2timestamp
        self.timestamp2uuid = {v: k for k, v in uuid2timestamp.items()}

        self.connection_matrix = connection_matrix
        self.viewpoints = generate_action_space(coordinates, self.timestamp2uuid)
        self.graph = self.generate_map()
        self.visited_graph = self.generate_visited_map()
        self.cur_node = None

    def generate_map(self):
        """
        生成系统图
        :return: 生成的图
        """
        graph = Map()
        node_ids = list(self.viewpoints.keys())
        for node_id, coord in self.viewpoints.items():
            node = Node(node_id, coord, self.node_infos[self.uuid2timestamp[node_id]])
            graph.add_node(node)

        for i, node_id in enumerate(node_ids):
            for j, neighbor_id in enumerate(node_ids):
                if self.connection_matrix[i][j]:
                    graph.add_edge(graph.get_node(node_id), graph.get_node(neighbor_id))
        return graph

    def generate_visited_map(self):
        """
        生成agent已经走过的图
        :return: 生成的图
        """
        return Map()

    def execute(self):
        """
              执行聊天模型的对话并处理工具调用。

              功能描述:
              1. 调用聊天模型API，生成对话响应。
              2. 将响应消息添加到消息列表中。
              3. 处理响应中的工具调用，如果存在工具调用则逐一执行：
                  - 提取函数名称和参数。
                  - 执行工具函数并获取结果。
                  - 打印工具调用的ID、函数名称、参数和响应结果。
                  - 将工具调用的结果添加到消息列表中。
              4. 如果存在内容响应，则打印机器人响应的内容和使用的token数量。

              异常处理:
              - 捕获并打印异常信息，包括当前的消息列表。

              注意:
              - 函数假设存在 'client', 'MODEL', 'messages', 'tools', 和 'add_tool_message' 等对象和方法。
        """
        try:
            response = self.client.chat.completions.create(
                MODEL,
                messages=self.messages,
                tools=self.tools.get_tools_usages()
            )

            print("robot raw response: {}".format(response), end="\n\n")

            self.messages.append(response.choices[0].message)
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = tool_call.function.arguments
                    function_response = self.tools.execute(function_name, function_args)
                    print(
                        "robot call tools id {}\nfunc: {}\nargs: {}\nresp: {}".format(
                            tool_call.id,
                            function_name,
                            function_args,
                            function_response,
                        )
                    )
                    self.add_tool_message(
                        tool_call.id, function_name, function_response
                    )
            if response.choices[0].message.content:
                print(
                    "robot: {}\n token: [{}] ".format(
                        response.choices[0].message.content, response.usage.total_tokens
                    ),
                    end="\n\n",
                )
        except Exception as e:
            print("Error: {}\nmessages: {}".format(e, self.messages))

    def run(self):
        start_viewpoint = next(vp_id for vp_id, coords in self.viewpoints.items() if coords == (0, 0, 0))
        self.cur_node = self.graph.get_node(start_viewpoint)
        pass

    def test(self):
        start_viewpoint = next(vp_id for vp_id, coords in self.viewpoints.items() if coords == (0, 0, 0))
        self.cur_node = self.graph.get_node(start_viewpoint)
        self.visited_graph.add_node(self.cur_node)

    def __str__(self):
        return f"PointNav Task ID: {self.task_id}, Description: {self.description}, Status: {self.status}, Instructions: {self.instructions}, Viewpoints: {len(self.viewpoints.keys())}"


if __name__ == "__main__":
    task = PointNav(1, "Point2PointNav", "Go out and see a walkway, then turn right toward the door", "IN_PROGRESS",
                    coordinates, node_infos, connection_matrix)
    task.test()