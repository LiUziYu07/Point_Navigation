import cv2
import argparse
import os
import json

import numpy as np
import supervision as sv

import torch
import torchvision

from groundingdino.util.inference import Model
from segment_anything import sam_model_registry, SamPredictor

from config.perceive_config import GROUNDING_DINO_CONFIG_PTH, GROUNDING_DINO_CKPT_PTH, SAM_CKPT_PTH, SAM_ENCODER_VERSION
from config.perceive_config import OUTPUT_SRC, IMAGE_SRC, SAMPLES_IMAGE_SRC
from config.perceive_config import TEXT_THRESHOLD, BOX_THRESHOLD, NMS_THRESHOLD


def perceive(
        image_src,
        classes,
):
    """
        执行物体检测和分割的感知函数。

        参数:
        - image_src (str): 图像的源文件夹路径，包含需要处理的图像文件。
        - classes (list of str): 待检测的目标类别列表。

        功能描述:
        1. 根据设备情况初始化推理设备（CUDA或CPU）。
        2. 构建GroundingDINO模型和SAM模型，用于物体检测和分割。
        3. 遍历指定文件夹中的图像文件，并执行以下操作:
           - 加载图像并调用GroundingDINO模型检测目标。
           - 使用检测到的结果在图像上进行标注并保存检测结果图像。
           - 将检测结果保存到JSON文件中。
           - 使用非极大值抑制（NMS）减少冗余的边界框。
           - 使用SAM模型对检测的边界框进行分割，得到目标掩码。
           - 将分割结果保存为图像和JSON文件。

        输出:
        - 标注后的检测图像和分割图像，保存到指定输出路径。
        - 检测和分割结果保存为JSON格式，包含类别、置信度、边界框和掩码信息。

        注意:
        - 该函数依赖于GroundingDINO和SAM模型进行检测和分割操作。
        - 输出结果保存在OUTPUT_SRC路径下的相应文件夹中。

        例外处理:
        - 如果输入的文件夹中不包含有效的图像文件，函数将跳过处理。
        - 非极大值抑制（NMS）用于减少重复检测结果。
    """

    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Building GroundingDINO inference model
    grounding_dino_model = Model(model_config_path=GROUNDING_DINO_CONFIG_PTH,
                                 model_checkpoint_path=GROUNDING_DINO_CKPT_PTH)

    # Building SAM Model and SAM Predictor
    sam = sam_model_registry[SAM_ENCODER_VERSION](checkpoint=SAM_CKPT_PTH)
    sam.to(device=DEVICE)
    sam_predictor = SamPredictor(sam)

    for root, dirs, files in os.walk(image_src):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)

                # load image
                image = cv2.imread(image_path)

                # detect objects
                detections = grounding_dino_model.predict_with_classes(
                    image=image,
                    classes=classes,
                    box_threshold=BOX_THRESHOLD,
                    text_threshold=TEXT_THRESHOLD
                )

                # annotate image with detections
                box_annotator = sv.BoxAnnotator()
                labels = [
                    f"{classes[class_id]} {confidence:0.2f}"
                    for _, _, confidence, class_id, _, _
                    in detections]
                annotated_frame = box_annotator.annotate(scene=image.copy(), detections=detections, labels=labels)

                # save the annotated grounding dino image
                relative_path = os.path.relpath(root, image_src)
                subfolder_id = os.path.basename(relative_path)
                detect_subfolder = os.path.join(OUTPUT_SRC, "image", subfolder_id, "detect")
                os.makedirs(detect_subfolder, exist_ok=True)
                output_groundingdino_image_path = os.path.join(detect_subfolder,
                                                               f"{os.path.splitext(file)[0]}_detection.jpg")
                cv2.imwrite(output_groundingdino_image_path, annotated_frame)

                # Save detection results to JSON
                detect_json_subfolder = os.path.join(OUTPUT_SRC, "json", subfolder_id, "detect")
                os.makedirs(detect_json_subfolder, exist_ok=True)
                output_detect_json_path = os.path.join(detect_json_subfolder,
                                                       f"{os.path.splitext(file)[0]}_detect.json")
                detection_results = [
                    {
                        "class": classes[class_id],
                        "confidence": float(confidence),
                        "bounding_box": box.tolist()
                    }
                    for box, _, confidence, class_id, _, _ in detections
                ]
                with open(output_detect_json_path, 'w') as json_file:
                    json.dump(detection_results, json_file, indent=4)

                # NMS post process
                print(f"Before NMS: {len(detections.xyxy)} boxes")
                nms_idx = torchvision.ops.nms(
                    torch.from_numpy(detections.xyxy),
                    torch.from_numpy(detections.confidence),
                    NMS_THRESHOLD
                ).numpy().tolist()

                detections.xyxy = detections.xyxy[nms_idx]
                detections.confidence = detections.confidence[nms_idx]
                detections.class_id = detections.class_id[nms_idx]

                print(f"After NMS: {len(detections.xyxy)} boxes")

                # Prompting SAM with detected boxes
                def segment(sam_predictor: SamPredictor, image: np.ndarray, xyxy: np.ndarray) -> np.ndarray:
                    sam_predictor.set_image(image)
                    result_masks = []
                    for box in xyxy:
                        masks, scores, logits = sam_predictor.predict(
                            box=box,
                            multimask_output=True
                        )
                        index = np.argmax(scores)
                        result_masks.append(masks[index])
                    return np.array(result_masks)

                # convert detections to masks
                detections.mask = segment(
                    sam_predictor=sam_predictor,
                    image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                    xyxy=detections.xyxy
                )

                # annotate image with detections
                box_annotator = sv.BoxAnnotator()
                mask_annotator = sv.MaskAnnotator()
                labels = [
                    f"{classes[class_id]} {confidence:0.2f}"
                    for _, _, confidence, class_id, _, _
                    in detections]
                annotated_image = mask_annotator.annotate(scene=image.copy(), detections=detections)
                annotated_image = box_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)

                # save the annotated grounded-sam image
                segment_subfolder = os.path.join(OUTPUT_SRC, "image", subfolder_id, "segment")
                os.makedirs(segment_subfolder, exist_ok=True)
                output_groundedsam_image_path = os.path.join(segment_subfolder,
                                                             f"{os.path.splitext(file)[0]}_segmentation.jpg")
                cv2.imwrite(output_groundedsam_image_path, annotated_image)

                # Save segmentation results to JSON
                segment_json_subfolder = os.path.join(OUTPUT_SRC, "json", subfolder_id, "segment")
                os.makedirs(segment_json_subfolder, exist_ok=True)
                output_segment_json_path = os.path.join(segment_json_subfolder,
                                                        f"{os.path.splitext(file)[0]}_segment.json")
                segmentation_results = [
                    {
                        "class": classes[class_id],
                        "confidence": float(confidence),
                        "bounding_box": box.tolist(),
                        "mask": mask.tolist()
                    }
                    for box, mask, confidence, class_id, _, _ in detections
                ]
                with open(output_segment_json_path, 'w') as json_file:
                    json.dump(segmentation_results, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grounded-Segment-Anything parameters")
    parser.add_argument("--classes", type=str, nargs='+', default=["chair"])

    args = parser.parse_args()
    print(args.classes)
    perceive(
        SAMPLES_IMAGE_SRC,
        classes=args.classes
    )
