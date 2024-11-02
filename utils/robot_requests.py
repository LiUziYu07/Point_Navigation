import json
import requests
from config.ros import ROS_IP, ROS_PORT

url_dict = {
    "camera": f"http://{ROS_IP}:{ROS_PORT}/camera?id=123",
    "navigate": f"http://{ROS_IP}:{ROS_PORT}/navigate?id=123",
    "transform": f"http://{ROS_IP}:{ROS_PORT}/transform?id=123",
}


def send_post_request(func_name, data):
    if func_name not in url_dict:
        raise Exception(f"Error: Invalid function name: {func_name}")
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url_dict[func_name], headers=headers, json=json.dumps(data))
    if response.status_code != 200:
        raise Exception(f"Error: When sending POST request. Request url: {url_dict[func_name]}, header: {headers}, "
                        f"request body: {data}")
    return response