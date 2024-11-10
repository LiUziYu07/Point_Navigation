import json
import uuid
import re
from graph.node import Node

import numpy as np
from sentence_transformers import SentenceTransformer

from download.ssh import download_folders
from fusion.get_depth import run as run_depth_service
from core.task import Task, PointNav
from config.ros import ROS_IP, ROS_PORT, ROS_IMAGE_PTH, ROS_JSON_PTH, ROS_PCD_PTH, ROS_HOST_NAME
from config.nav_node_info import coordinates, node_infos, connection_matrix, uuid2timestamp
from utils.robot_requests import send_post_request, url_dict

text_embedding = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def cos_simularity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


class ToolBase:
    def get_description(self):
        pass

    def execute(self, task: Task, args_str: str):
        pass


class ToolSurroundingDetect(ToolBase):
    def __init__(self):
        pass

    def parser(self, args_str):
        try:
            args = json.loads(args_str)
        except ValueError:
            raise Exception("the arguments '{}' is not a json string".format(args_str))

        if "landmark" not in args:
            raise Exception("'landmark' key is missing in the arguments.")

        return args.get("landmark")

    def execute(self, task: Task, args_str: str):
        landmark = self.parser(args_str)
        msgs = ""

        # Rotate and capture surroundings
        cur_x, cur_y, _ = task.cur_node.coordinates
        for degree in [0, 90, 90, 90, 90]:
            msgs = ""
            new_pose = task.cur_node.pose + degree
            nav_data = {
                "goal_x": str(cur_x),
                "goal_y": str(cur_y),
                "goal_z": "0",
                "rotate_degree": new_pose % 360
            }

            nav_response = send_post_request("navigate", nav_data)
            if nav_response.status_code == 200:
                if "success" in nav_response.text.lower():
                    msgs += f"I have success rotate at the current location with pose {new_pose % 360}\n"
                task.cur_node.update_pose(new_pose)
            else:
                msgs += f"Error in navigation: {nav_response.text}\n"

            camera_data = {
                "camera_names": ["front"],
                "analyzers": "manual"
            }

            camera_response = send_post_request("camera", camera_data)
            if camera_response.status_code == 200:
                pass
            else:
                msgs += f"Error in when capturing: {camera_response.text}\n"

            # Depth estimation
            remote_dirs = [
                ROS_IMAGE_PTH,
                ROS_PCD_PTH,
                ROS_JSON_PTH
            ]
            local_base_dir = 'D:\CEG5003_PointNav\data\obs'
    
            download_folders(ROS_IP, 22, ROS_HOST_NAME, remote_dirs, local_base_dir)
            try:
                idx, coords = run_depth_service(landmark)
                depth_data = {
                    "point_x": coords[0],
                    "point_y": coords[1],
                    "point_z": 0,
                }
                transform_response = send_post_request("transform", depth_data)
                print(f"Point on the map: {transform_response.text}")
                msgs += transform_response.text
                break
            except Exception as e:
                msgs += f"In depth estimation: {e}"
        
        if msgs != "":
            return msgs
        else:
            return "I cannot find the landmark"

    def get_description(self):
        return {
            "type": "function",
            "function": {
                "name": "surrounding_detect",
                "description": "This `surrounding_detect` function represents detecting the surroundings of a specific object and estimating its depth.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "landmark": {
                            "type": "string",
                            "description": "`landmark` represents the object for which surroundings are to be detected, like objects.",
                        }
                    },
                    "required": ["landmark"],
                },
            },
        }


class ToolViewpointGet(ToolBase):
    def __init__(self):
        pass

    def parser(self, args_str):
        try:
            args = json.loads(args_str)
        except ValueError:
            raise Exception("the arguments '{}' is not a json string".format(args_str))

        required_params = ["viewpoint_id", "landmark", "coord_x", "coord_y"]
        for param in required_params:
            if param not in args:
                raise Exception("parameter '{}' not found in the arguments {}.".format(param, args))

        coord_x = args.get("coord_x")
        coord_y = args.get("coord_y")

        try:
            coord_x = float(coord_x)
            coord_y = float(coord_y)
        except ValueError:
            raise Exception("coord_x and coord_y must be convertible to float.")

        return args.get("viewpoint_id"), args.get("landmark"), coord_x, coord_y

    def execute(self, task: Task, args_str: str):
        viewpoint_id, landmark, coord_x, coord_y = self.parser(args_str)
        landmark_embedding = text_embedding.encode(landmark)
        # Get the current node from the task's graph using the viewpoint_id
        current_node = task.graph.get_node(viewpoint_id)

        if current_node is None:
            raise Exception(f"Viewpoint ID {viewpoint_id} does not exist in the graph.")

        # Get the connected nodes information
        connected_info = task.graph.get_connected_info(viewpoint_id)

        # Find the next accessible viewpoint
        dist = np.inf
        next_viewpoint = None
        simularity_dict = {}
        for info in connected_info:
            next_x, next_y, _ = info["coordinates"]
            desc_embedding = text_embedding.encode(str(info["description"]).replace("{", "").replace("}", ""))

            simularity_dict[info["viewpoint_id"]] = cos_simularity(landmark_embedding, desc_embedding)

            if dist > (coord_y - next_y) ** 2 + (coord_x - next_x) ** 2:
                dist = (coord_y - next_y) ** 2 + (coord_x - next_x) ** 2
                next_viewpoint = info
                
        # Check if the new viewpoint is closer to the current node's coordinates
        cur_x, cur_y, _ = task.cur_node.coordinates
        new_x, new_y, _ = next_viewpoint["coordinates"]

        current_distance = (coord_x - cur_x) ** 2 + (coord_y - cur_y) ** 2

        if dist >= current_distance:
            raise Exception("The new viewpoint is not closer to the target than the current node. The task is completed!")
        
        if next_viewpoint is None:
            raise Exception("No accessible viewpoint found.")

        max_key, max_value = max(simularity_dict.items(), key=lambda x: x[1])
        print("Max Cos Similarity viewpoint:", max_key)

        msg = f"The optimal viewpoint: {next_viewpoint['viewpoint_id']}"
        return msg

    def get_description(self):
        return {
            "type": "function",
            "function": {
                "name": "viewpoint_get",
                "description": "`viewpoint_get` is the method used to query which areas are navigable on the entire node map, generally used after I have known landmark.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "viewpoint_id": {
                            "type": "string",
                            "description": "`viewpoint_id` represents the ID of the current viewpoint",
                        },
                        "landmark": {
                            "type": "string",
                            "description": "`landmark` represents the object for which surroundings are to be detected",
                        },
                        "coord_x": {
                            "type": "string",
                            "description": "`coord_x` represents the x coordinate of the object for which surroundings are to be detected",
                        },
                        "coord_y": {
                            "type": "string",
                            "description": "`coord_y` represents the y coordinate of the object for which surroundings are to be detected",
                        },
                    },
                    "required": ["viewpoint_id", "landmark", "coord_x", "coord_y"],
                },
            },
        }


class ToolNavigate(ToolBase):
    def __init__(self) -> None:
        """
            初始化 ToolNavigate 类，并定义初始变量。
        """
        self.goal_z = 0

    def parser(self, args_str):
        """
            解析输入参数字符串，并返回所需的参数值。

            参数:
            - args_str (str): JSON格式的字符串，包含导航参数。

            返回值:
            - tuple: 包含起点、终点、旋转类型和旋转角度的元组。

            异常处理:
            - 如果参数字符串不是JSON格式，抛出异常。
            - 如果缺少必需的参数，抛出异常。
        """
        try:
            args = json.loads(args_str)
        except ValueError:
            raise Exception("the arguments '{}' is not a json string".format(args_str))

        required_params = ["starting_point", "ending_point", "rotate_degree"]
        for param in required_params:
            if param not in args:
                raise Exception("parameter '{}' not found in the arguments {}.".format(param, args))

        starting_point = args.get("starting_point")
        ending_point = args.get("ending_point")
        rotate_degree = args.get("rotate_degree")

        try:
            rotate_degree = float(rotate_degree)
        except ValueError:
            raise Exception(f"rotate_degree '{rotate_degree}' cannot be converted to a float.")

        return starting_point, ending_point, rotate_degree

    def validate_args(self, starting_point, ending_point, task_info):
        """
            验证起点和终点是否在任务信息中。

            参数:
            - starting_point (str): 起点ID。
            - ending_point (str): 终点ID。
            - task_info (Task): 任务信息对象。

            异常处理:
            - 如果起点或终点未在任务视点中找到，抛出异常。
        """
        if starting_point not in task_info.viewpoints:
            raise ValueError(f"Unrecognized starting point: {starting_point}")
        if ending_point not in task_info.viewpoints:
            raise ValueError(f"Unrecognized ending point: {ending_point}")

    def execute(self, task: PointNav, args_str):
        """
           执行导航任务。

           参数:
           - task (Task): 任务对象，包含视点信息。
           - args_str (str): JSON格式的参数字符串。

           返回值:
           - str: 表示导航成功或失败的消息。

           功能描述:
           1. 解析输入参数，获取起点、终点、旋转类型和旋转角度。
           2. 验证起点和终点的有效性。
           3. 计算位移角度，根据旋转类型设置旋转角度。
           4. 构建请求负载并发送导航请求。
           5. 返回导航成功或失败的消息。

           异常处理:
           - 如果请求失败，则抛出异常。
       """
        starting_point, ending_point, rotate_degree = self.parser(args_str)

        self.validate_args(starting_point, ending_point, task)

        sp_x, sp_y, _ = task.viewpoints[starting_point]
        ep_x, ep_y, _ = task.viewpoints[ending_point]

        delta_x = ep_y - sp_x
        delta_y = ep_x - sp_y
        if abs(delta_x) > abs(delta_y):
            if delta_x < 0:
                new_pose = 180
            else:
                new_pose = 0
        else:
            if delta_y > 0:
                new_pose = 90
            else:
                new_pose = 270

        nav_data = {
            "goal_x": str(ep_x),
            "goal_y": str(ep_y),
            "goal_z": "0",
            "rotate_degree": new_pose % 360
        }
        nav_response = send_post_request("navigate", nav_data)

        msgs = nav_response.text
        if nav_response.status_code == 200:
            print("***************")
            new_node = Node(node_id=ending_point, coordinates=(ep_x, ep_y, 0), description="")
            task.visited_graph.add_node(new_node)
            task.cur_node = new_node
            msgs = "You have successfully navigate to viewpoint {}".format(ending_point)
        else:
            msgs += "You failed navigate to point {}".format(ending_point)

        return msgs

    def get_description(self):
        """
            获取工具的描述信息，包括功能、参数类型和说明。

            返回值:
            - dict: 描述工具的功能和参数信息的字典。
        """
        return {
            "type": "function",
            "function": {
                "name": "navigate",
                "description": "The `navigate` function directs a robot to a specific location and orientation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "starting_point": {
                            "type": "string",
                            "description": "starting_point represents the starting position of the robot's "
                                           "navigation, which is an ID that is used to represent a unique position on "
                                           "the topology map",
                        },
                        "ending_point": {
                            "type": "string",
                            "description": "ending_point represents the destination position of the robot's "
                                           "navigation, which is an ID that is used to represent a unique position on "
                                           "the topology map",
                        },
                        "rotate_degree": {
                            "type": "string",
                            "description": "The `rotate_degree` parameter indicates the desired rotation angle from "
                                           "the robot's current pose, ranging between -360 and 360 degrees.",
                        }
                    },
                    "required": ["goal_x", "goal_y", "rotate_degree"],
                },
            },
        }


if __name__ == "__main__":
    task_id = uuid.uuid4()

    episode = PointNav(task_id, "Point2PointNav_trial_1", "INIT", "",
                                coordinates, node_infos, connection_matrix, uuid2timestamp)
    episode.test()
    print(episode.cur_node)
    msgs = []

    # landmark = "blue garbagecan"
    # landmark = "green bag"
    landmark = "cabinet"
    point_x, point_y, point_z = None, None, None
    surrounding_detect = ToolSurroundingDetect()
    surrounding_msgs = surrounding_detect.execute(episode, f'{{"landmark": "{landmark}"}}')
    print(f"Surrounding_detect msgs: {surrounding_msgs}")
    try:
        matches = re.findall(r'x=(-?[0-9.]+), y=(-?[0-9.]+), z=(-?[0-9.]+)', surrounding_msgs)
        print(f"Depth msgs: {surrounding_msgs}")
        if matches:
            point_x, point_y, point_z = matches[0]
        else:
            print("Unmatch Informatinon msgs")
    except Exception as e:
        print(e)

    viewpoint_get = ToolViewpointGet()
    next_viewpoint_msg = viewpoint_get.execute(episode,
                                           f'{{"viewpoint_id": "{episode.cur_node.node_id}", "landmark": "{landmark}", "coord_x": {point_x}, "coord_y": {point_y}}}')

    navi = ToolNavigate()
    navi.execute(episode, f'{{"starting_point": "{episode.cur_node.node_id}", "ending_point": "{next_viewpoint_msg.replace("The optimal viewpoint:", "").strip()}", "rotate_degree": 0}}')

    landmark = "green bag"
    point_x, point_y, point_z = None, None, None
    surrounding_detect = ToolSurroundingDetect()
    surrounding_msgs = surrounding_detect.execute(episode, f'{{"landmark": "{landmark}"}}')
    try:
        matches = re.findall(r'x=(-?[0-9.]+), y=(-?[0-9.]+), z=(-?[0-9.]+)', surrounding_msgs)
        print(f"Depth msgs: {surrounding_msgs}")
        if matches:
            point_x, point_y, point_z = matches[0]
        else:
            print("Unmatch Informatinon msgs")
    except Exception as e:
        print(e)

    viewpoint_get = ToolViewpointGet()
    next_viewpoint_msg = viewpoint_get.execute(episode,
                                               f'{{"viewpoint_id": "{episode.cur_node.node_id}", "landmark": "{landmark}", "coord_x": {point_x}, "coord_y": {point_y}}}')

    navi = ToolNavigate()
    navi.execute(episode,
                 f'{{"starting_point": "{episode.cur_node.node_id}", "ending_point": "{next_viewpoint_msg.replace("The optimal viewpoint:", "").strip()}", "rotate_degree": 0}}')
