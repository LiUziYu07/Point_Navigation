import os

# Server on the robot
# ROS_IP = os.environ.get("ROS_IP", default="172.26.63.127")
ROS_IP = os.environ.get("ROS_IP", default="172.20.10.9")
# ROS_IP = os.environ.get("ROS_IP", default="10.249.125.237")
ROS_PORT = os.environ.get("ROS_PORT", default=8080)

ROS_HOST_NAME = os.environ.get("ROS_HOST_NAME", default="wr")
ROS_IMAGE_PTH = os.environ.get("ROS_IMAGE_PTH", default="/home/wr/Downloads/tracer_image/")
ROS_PCD_PTH = os.environ.get("ROS_PCD_PTH", default="/home/wr/Downloads/tracer_pcd/")
ROS_JSON_PTH = os.environ.get("ROS_JSON_PTH", default="/home/wr/Downloads/tracer_json/")