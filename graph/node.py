import networkx as nx
import math
import uuid


class Node:
    def __init__(self, node_id, coordinates, description, pose=0):
        """
        初始化节点
        :param node_id: 节点的唯一标识
        :param coordinates: 结点的全局坐标，形式为 (x, y, z)
        :param description: 该坐标处的场景描述
        """
        self.node_id = node_id
        self.coordinates = coordinates
        self.description = description
        self.is_visited = False

        # 起始姿态与地图的x轴正方向平行
        self.pose = pose % 360

    def update_pose(self, pose):
        self.pose = pose % 360

    def update_coordinates(self, coordinates):
        self.coordinates = coordinates

    def __repr__(self):
        return f"Node(Node_id: {self.node_id}, Coordinates: {self.coordinates}, Description: {self.description})"


class Map:
    def __init__(self):
        """
        初始化一个空图
        """
        self.graph = nx.Graph()

    def add_node(self, node):
        """
        向图中添加一个节点
        :param node: Node类的实例
        """
        self.graph.add_node(node.node_id, data=node)

    def add_edge(self, node1, node2):
        """
        添加边并计算权重为两节点间距离
        :param node1: 第一个节点
        :param node2: 第二个节点
        """
        distance = calculate_distance(node1.coordinates, node2.coordinates)
        self.graph.add_edge(node1.node_id, node2.node_id, weight=distance)

    def get_connected_info(self, node_id):
        """
        返回与指定节点相连的节点信息
        :param node_id: 要查询的节点ID
        :return: 与该节点相连的所有节点及其相关信息
        """
        if node_id not in self.graph.nodes:
            return f"Node {node_id} does not exist in the graph."

        connected_nodes = self.graph.neighbors(node_id)
        info = []
        for neighbor in connected_nodes:
            edge_data = self.graph.get_edge_data(node_id, neighbor)
            node_data = self.graph.nodes[neighbor]['data']
            info.append({
                'viewpoint_id': neighbor,
                'distance': edge_data['weight'],
                'coordinates': node_data.coordinates,
                'description': node_data.description
            })
        return info

    def generate(self, coordinates, node_infos):
        assert len(coordinates) == len(node_infos), "Coordinates and node_infos must have the same length"

        for i in range(len(coordinates)):
            node = Node(i, coordinates[i], node_infos[i])
            self.add_node(node)
        for i in range(len(coordinates)):
            for j in range(i + 1, len(coordinates)):
                self.add_edge(i, j)

        return self.graph

    def get_node(self, node_id):
        """
        返回指定ID的节点对象
        :param node_id: 节点ID
        :return: Node对象
        """
        if node_id in self.graph.nodes:
            return self.graph.nodes[node_id]['data']
        else:
            return None

    def traverse_graph(self, start_node_id):
        """
        从指定节点开始遍历整个图
        :param start_node_id: 起始节点ID
        :return: 遍历顺序中的节点ID列表
        """
        if start_node_id not in self.graph.nodes:
            return f"Node {start_node_id} does not exist in the graph."

        visited = set()
        traversal_order = []

        def dfs(node_id):
            visited.add(node_id)
            traversal_order.append(node_id)
            for neighbor in self.graph.neighbors(node_id):
                if neighbor not in visited:
                    dfs(neighbor)

        dfs(start_node_id)
        return traversal_order

    def __str__(self):
        """
        返回图的字符串表示
        :return: 图的字符串表示
        """
        result = []
        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]['data']
            connected_info = self.get_connected_info(node_id)
            result.append(
                f"Node ID: {node_id}, Coordinates: {node_data.coordinates}, Description: {node_data.description}")
            for info in connected_info:
                result.append(
                    f"  Connected to Node ID: {info['Connected Node ID']}, Distance: {info['Distance (Weight)']}, Coordinates: {info['Node Coordinates']}, Description: {info['Node Description']}")
        return "\n".join(result)


def calculate_distance(coord1, coord2):
    """
    计算两点之间的欧氏距离
    :param coord1: 第一个点的坐标
    :param coord2: 第二个点的坐标
    :return: 两点之间的距离
    """
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(coord1, coord2)]))


# 示例使用
if __name__ == "__main__":
    # 初始化图
    graph = Map()

    # 添加一些节点，坐标假设为 (x, y, z) 格式，描述为 "场景描述"
    node1 = Node(node_id=str(uuid.uuid4()), coordinates=(0, 0, 0), description="Node 1 Scene")
    node2 = Node(node_id=str(uuid.uuid4()), coordinates=(1, 1, 1), description="Node 2 Scene")
    node3 = Node(node_id=str(uuid.uuid4()), coordinates=(2, 2, 2), description="Node 3 Scene")
    node4 = Node(node_id=str(uuid.uuid4()), coordinates=(3, 3, 3), description="Node 4 Scene")
    node5 = Node(node_id=str(uuid.uuid4()), coordinates=(4, 4, 4), description="Node 5 Scene")

    # 向图中添加节点
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_node(node5)

    # 添加节点间的连接关系
    graph.add_edge(node1, node2)
    graph.add_edge(node2, node3)
    graph.add_edge(node3, node4)
    graph.add_edge(node4, node5)
    graph.add_edge(node1, node5)
    graph.add_edge(node1, node4)

    # 查询某个节点的相连信息
    node_id_to_query = node1.node_id
    connected_info = graph.get_connected_info(node_id_to_query)
    print(f"Connected nodes for Node {node_id_to_query}:")
    for info in connected_info:
        print(info)
