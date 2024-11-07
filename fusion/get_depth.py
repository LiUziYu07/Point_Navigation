import open3d
import cv2
import numpy as np
import demjson
import os
import open3d as o3d
from tqdm import tqdm

from utils.folder_transfer import move_subfolders
from utils.read_config import read_parameters_from_yaml
from utils.coordinate_convert import get_transformation_pt
from config.sensor_config import SENSOR_CONFIG_PTH
from config.perceive_config import OUTPUT_SRC
from perception.perception import perceive
from config.data import PCD_FOLDER, IMAGE_FOLDER, ACML_FOLDER, SEGMENT_FOLDER, OUTDATED_FOLDER, OBS_CONFIG_PTH


def get_project_pt(point, mask, camera_matrix, distort_coeffs, distort_type, transform_matrix, image):
    """
        将点云中的点投影到图像上，并根据图像掩码判断该点是否有效。

        参数:
        - point (numpy.ndarray): 点云中的单个点，表示为3D坐标。
        - mask (numpy.ndarray): 图像的二值掩码，用于标记目标区域。
        - camera_matrix (numpy.ndarray): 相机内参矩阵，用于将3D点投影到2D图像平面。
        - distort_coeffs (numpy.ndarray): 相机的畸变系数，用于校正图像畸变。
        - distort_type (str): 畸变类型，用于选择畸变校正的方法。
        - transform_matrix (numpy.ndarray): 雷达坐标系到相机坐标系的变换矩阵，用于将点云从雷达坐标系转换到相机坐标系。
        - image (numpy.ndarray): 读取的图像，用于获取像素颜色和尺寸信息。

        返回值:
        - numpy.ndarray or None: 返回有效的投影点坐标。如果投影成功并且在掩码范围内，则返回该点；否则返回None。

        功能描述:
        1. 调用 'get_transformation_pt' 函数，根据相机内参、畸变系数、畸变类型和变换矩阵，将3D点转换为2D像素坐标。
        2. 若投影成功，提取相应像素的颜色。
        3. 判断投影点是否在图像掩码范围内，并返回原始点云点的3D坐标。
        4. 如果点不在掩码范围或投影失败，返回None。

        注意:
        - 该函数假设输入的图像为RGB格式。
        - 'get_transformation_pt' 是一个外部函数，用于执行3D点到2D图像平面的投影和畸变校正。
        """

    dist_info = get_transformation_pt(camera_matrix, distort_coeffs, distort_type, transform_matrix, image.shape[1],
                                      image.shape[0], point)
    x, y = None, None
    if dist_info:
        x, y, _ = dist_info
        if mask[int(y)][int(x)]:
            return point

    return None


def get_depth(**kwargs):
    # noinspection LanguageDetectionInspection
    """
            计算目标标志物的深度值。

            参数:
            kwargs (dict): 参数字典，其中应包含以下关键参数：
                - 'landmark' (str): 目标标志物名称，指示在图像中要寻找的目标。
                - 'folder_id' (str): 文件夹ID，用于指定处理的文件夹路径。

            返回值:
            float: 目标标志物的平均深度值。

            异常:
            Exception: 如果 'landmark' 或 'folder_id' 参数缺失时抛出此异常。
            FileNotFoundError: 如果所需的文件夹或文件不存在时抛出此异常。

            功能描述:
            1. 从输入的kwargs中提取'folder_id'和'landmark'参数，并检查它们是否存在。
            2. 检查图像文件夹、特定图像文件、ACML文件和PCD文件的存在性，若不存在则抛出相应错误。
            3. 读取传感器配置中的变换矩阵、相机内参、畸变系数和畸变类型。
            4. 打印调试信息，提示正在尝试在图像中寻找目标标志物。
            5. 通过感知模块在指定图像中检测目标标志物。
            6. 加载分割掩码文件，若文件不存在则抛出相应错误。
            7. 将点云数据与图像进行对齐，并利用相机内参和畸变系数投影点云中的点。
            8. 根据投影后的点云计算目标标志物的平均深度值，并返回该值。

            注意:
            - 函数假设输入路径（IMAGE_FOLDER, ACML_FOLDER, PCD_FOLDER, SEGMENT_FOLDER）已定义为全局变量。
            - 函数依赖于外部的参数读取函数 'read_parameters_from_yaml' 以及图像和点云处理函数 'perceive' 和 'get_project_pt'。
            """

    if kwargs["folder_id"] is None:
        raise Exception("Error: Missing `folder_id` parameter")

    folder_id = kwargs["folder_id"]

    image_file_pth = os.path.join(IMAGE_FOLDER, folder_id, f"{folder_id}_0.jpg")
    if not os.path.exists(image_file_pth):
        raise FileNotFoundError(f"Error: image file {image_file_pth} does not exist")

    acml_file_pth = os.path.join(ACML_FOLDER, folder_id, "amcl.json")
    if not os.path.exists(acml_file_pth):
        raise FileNotFoundError(f"Error: folder {acml_file_pth} does not exist")

    pcd_file_pth = os.path.join(PCD_FOLDER, folder_id, f"{folder_id}.pcd")
    if not os.path.exists(pcd_file_pth):
        raise FileNotFoundError(f"Error: folder {pcd_file_pth} does not exist")

    # 读取从雷达坐标系道相机坐标系的变换矩阵、相机的内参、相机的畸变系数、畸变类型
    transformerMarix_l2c, camera_matrix, distot_coeffs, distort_type = read_parameters_from_yaml(SENSOR_CONFIG_PTH)

    mask_file = os.path.join(SEGMENT_FOLDER, "json", folder_id, "segment", f"{folder_id}_0_segment.json")
    if not os.path.exists(mask_file):
        raise FileNotFoundError(f"Error: mask file {mask_file} does not exist")

    print("************************ Try to read the mask ************************")
    mask_data = demjson.decode_file(mask_file, encoding='utf-8')
    target_pts = []
    depth = None
    if mask_data:
        mask = mask_data[0]["mask"]
        pcd = o3d.io.read_point_cloud(pcd_file_pth)
        image = cv2.imread(image_file_pth)
        points = pcd.points

        for point in points:
            point = get_project_pt(point, mask, camera_matrix, distot_coeffs, distort_type, transformerMarix_l2c, image)
            if point is not None:
                target_pts.append(point)

        target_pts = np.array(target_pts)
        if len(target_pts) > 0:
            mean = np.mean(target_pts, axis=0)
            std_dev = np.std(target_pts, axis=0)
            print(f"Variance before removing outliers: {np.var(target_pts, axis=0)}")
            filtered_pts = [pt for pt in target_pts if np.all(np.abs(pt - mean) <= 2 * std_dev)]
            filtered_pts = np.array(filtered_pts)
            print(f"Variance after removing outliers: {np.var(filtered_pts, axis=0)}")
            target_pts = np.array(filtered_pts)
        depth = np.mean(target_pts, axis=0)

    return depth


def pre_process(**kwargs):
    """
    图像预处理函数，用于在指定文件夹中寻找目标标志物。

    参数:
    - kwargs (dict): 参数字典，应包含以下关键参数：
        - 'landmark' (str): 标志物的名称，用于指示要检测的目标。

    功能描述:
    1. 从输入的kwargs中提取 'landmark' 参数，并检查其是否存在。
    2. 检查IMAGE_FOLDER路径是否存在，若不存在则抛出相应错误。
    3. 调用 'perceive' 函数，执行目标标志物的检测。

    异常:
    - Exception: 如果缺少 'landmark' 参数，则抛出此异常。
    - FileNotFoundError: 如果IMAGE_FOLDER路径不存在，则抛出此异常。

    注意:
    - 该函数假设 IMAGE_FOLDER 是一个全局定义的变量。
    - 'perceive' 函数会在给定图像文件夹中寻找指定的标志物，并执行检测操作。
    """
    if kwargs["landmark"] is None:
        raise Exception("Error: Missing `landmark` parameter")

    landmark_name = kwargs["landmark"]

    image_folder = os.path.join(IMAGE_FOLDER)
    if not os.path.exists(image_folder):
        raise FileNotFoundError(f"Error: folder {image_folder} does not exist")

    print(f"************************ Try to find the {landmark_name} in the images ************************")
    perceive(image_folder, [landmark_name])


def run(landmark):
    """
    运行标志物深度计算的主函数。

    参数:
    - landmark (str): 指定的标志物名称，用于图像检测和深度计算。

    功能描述:
    1. 调用 'pre_process' 函数，执行目标标志物的预处理检测。
    2. 遍历 IMAGE_FOLDER 中的所有文件夹，对每个文件夹调用 'get_depth' 函数，计算标志物的3D深度坐标。
    3. 将检测结果存储在 'landmark_depth' 列表中。
    4. 将输出文件夹（OUTPUT_SRC和OBS_CONFIG_PTH）移动到OUTDATED_FOLDER中，以便归档处理过的文件。
    5. 通过计算3D坐标的平方和，找到深度最小的标志物位置。
    6. 返回最小深度对应的文件夹索引和对应的3D坐标。

    返回值:
    - min_index (int): 最小深度值对应的文件夹索引。
    - (x, y, z) (tuple of float): 最小深度值对应的3D坐标。

    注意:
    - 使用 'tqdm' 模块显示遍历文件夹的进度。
    - 'move_subfolders' 函数用于将指定文件夹中的子文件夹移动到归档文件夹。
    """
    pre_process(landmark=landmark)

    landmark_depth = []
    for root, dirs, files in tqdm(os.walk(IMAGE_FOLDER)):
        for folder_id in dirs:
            depth_info = get_depth(landmark=landmark, folder_id=folder_id)
            if depth_info is not None:
                landmark_depth.append(depth_info)

    print(f"Depths from multiple views: {landmark_depth}")
    # 将图像源文件以及计算的结果挪走
    move_subfolders(OUTPUT_SRC, OUTDATED_FOLDER)
    move_subfolders(OBS_CONFIG_PTH, OUTDATED_FOLDER)
    if not landmark_depth:
        raise ValueError(f"Error: landmark_depth list is empty. No {landmark} depth information found.")
    min_index, (x, y, z) = min(enumerate(landmark_depth), key=lambda t: t[1][0] ** 2 + t[1][1] ** 2 + t[1][2] ** 2)
    return min_index, (round(x, 3), round(y, 3), round(z, 3))


if __name__ == "__main__":
    landmark = "cabinet"
    depths = run(landmark)
    print(depths)