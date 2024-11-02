import open3d as o3d
import os
import numpy as np


def visualize_pcd_with_camera(file_path: str, camera_position=(0, 0, 5), zoom=0.7, z_threshold=0.01):
    """
    加载 PCD 文件并在可视化时设置自定义的相机初始位置，同时过滤Z轴接近0的点。

    :param file_path: PCD 文件的路径
    :param camera_position: 相机初始位置 (x, y, z)，默认在 (0, 0, 5)
    :param zoom: 相机初始缩放比例，默认值为 0.7
    :param z_threshold: Z轴过滤阈值，小于该值的点将被去除，默认值为 0.01
    """
    try:
        # 检查文件路径是否存在
        if not os.path.exists(file_path):
            print(f"文件路径无效: {file_path}")
            return

        # 读取 PCD 文件
        pcd = o3d.io.read_point_cloud(file_path)

        # 检查是否成功加载
        if pcd.is_empty():
            print(f"无法加载 PCD 文件，请检查文件路径: {file_path}")
            return

        # 转换为numpy数组进行过滤
        points = np.asarray(pcd.points)
        # filtered_points = points[points[:, 2] > z_threshold]
        filtered_points = points
        # 检查是否有剩余的点
        if filtered_points.shape[0] == 0:
            print("过滤后无有效点可视化，请调整过滤阈值或检查点云数据。")
            return

        # 将过滤后的点转换为点云
        filtered_pcd = o3d.geometry.PointCloud()
        filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)

        # 创建可视化窗口
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name="PCD 点云可视化 (相机调整)", width=800, height=600)

        # 添加点云
        vis.add_geometry(filtered_pcd)

        # 获取 ViewControl 对象
        view_control = vis.get_view_control()

        # 设置相机参数
        view_control.set_lookat([0, 0, 0])  # 相机观察目标点
        view_control.set_up([0, -1, 0])  # 设置相机上向量
        view_control.set_front(camera_position)  # 设置相机位置
        view_control.set_zoom(zoom)  # 设置初始缩放比例

        # 运行可视化
        vis.run()

        # 关闭窗口
        vis.destroy_window()

    except Exception as e:
        print(f"可视化 PCD 文件时出错: {e}")


if __name__ == "__main__":
    # 替换为你的 PCD 文件路径
    file_path = "D:\\CEG5003_PointNav\\data\\obs\\tracer_pcd\\1730128062\\1730128062.pcd"
    visualize_pcd_with_camera(file_path, camera_position=(0, -1, 1), z_threshold=0.01)
