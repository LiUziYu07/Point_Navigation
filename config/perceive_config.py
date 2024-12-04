import os

GROUNDING_DINO_CKPT_PTH = os.environ.get("GROUNDING_DINO_CKPT_PTH", default="D:\CEG5003_PointNav\perception\groundingdino_swint_ogc.pth")
GROUNDING_DINO_CONFIG_PTH = os.environ.get("GROUNDING_DINO_CONFIG_PTH", default="D:\CEG5003_PointNav\perception\GroundingDINO\groundingdino\config\GroundingDINO_SwinT_OGC.py")

SAM_CKPT_PTH = os.environ.get("SAM_CKPT_PTH", default="D:\CEG5003_PointNav\perception\sam_vit_h_4b8939.pth")
SAM_ENCODER_VERSION = os.environ.get("SAM_ENCODER_VERSION", default="vit_h")

SAMPLES_IMAGE_SRC = os.environ.get("IMAGE_SRC", default="D:\\CEG5003_PointNav\\data\\samples")
IMAGE_SRC = os.environ.get("IMAGE_SRC", default="D:\\CEG5003_PointNav\\data\\obs\\tracer_image")
OUTPUT_SRC = os.environ.get("OUTPUT_SRC", default="D:\\CEG5003_PointNav\\data\\results")

TEXT_THRESHOLD = os.environ.get("TEXT_THRESHOLD", default=0.25)
BOX_THRESHOLD = os.environ.get("BOX_THRESHOLD", default=0.5)
NMS_THRESHOLD = os.environ.get("NMS_THRESHOLD", default=0.8)
