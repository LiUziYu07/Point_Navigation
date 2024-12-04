import os

# Server on the robot
IMAGE_FOLDER = os.environ.get("IMAGE_FOLDER", default="D:\\CEG5003_PointNav\\data\\obs\\tracer_image")
ACML_FOLDER = os.environ.get("ACML_FOLDER", default="D:\\CEG5003_PointNav\\data\\obs\\tracer_json")
PCD_FOLDER = os.environ.get("PCD_FOLDER", default="D:\\CEG5003_PointNav\\data\\obs\\tracer_pcd")

DETECT_FOLDER = os.environ.get("DETECT_FOLDER", default="D:\\CEG5003_PointNav\\data\\obs\\tracer_pcd")
SEGMENT_FOLDER = os.environ.get("SEGMENT_FOLDER", default="D:\\CEG5003_PointNav\\data\\results")

OBS_CONFIG_PTH = os.environ.get("OBS_CONFIG_PTH", default="D:\CEG5003_PointNav\data\obs")
OUTDATED_FOLDER = os.environ.get("OUTDATED_FOLDER", default="D:\\CEG5003_PointNav\\data\\outdated")