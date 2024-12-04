import os

# Server on the robot
CAMERA_CONFIG_PTH = os.environ.get("CAMERA_CONFIG_PTH", default="D:\CEG5003_PointNav\config\camera.yaml")
LIDAR_CONFIG_PTH = os.environ.get("LIDAR_CONFIG_PTH", default="D:\CEG5003_PointNav\config\lidar.yaml")

SENSOR_CONFIG_PTH = os.environ.get("SENSOR_CONFIG_PTH", default="D:\CEG5003_PointNav\config\sensor.yaml")