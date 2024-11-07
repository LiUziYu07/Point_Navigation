import os
import shutil
from config.perceive_config import OUTPUT_SRC
from config.data import OUTDATED_FOLDER, OBS_CONFIG_PTH


def move_subfolders(source_folder, target_folder):
    if not os.path.exists(source_folder):
        print(f"源文件夹 {source_folder} 不存在。")
        return
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"目标文件夹 {target_folder} 创建成功。")

    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        if os.path.isdir(item_path):  # 检查是否为文件夹
            target_path = os.path.join(target_folder, item)
            # 如果目标文件夹中已存在同名文件夹，将内容挪到该文件夹
            if os.path.exists(target_path):
                for sub_item in os.listdir(item_path):
                    sub_item_path = os.path.join(item_path, sub_item)
                    shutil.move(sub_item_path, target_path)
                # print(f"文件夹 {item} 的内容已合并到 {target_path}。")
                os.rmdir(item_path)  # 删除空的源文件夹
            else:
                shutil.move(item_path, target_path)
                # print(f"文件夹 {item} 已转移到 {target_folder}。")


if __name__ == '__main__':
    move_subfolders(OUTPUT_SRC, OUTDATED_FOLDER)
    move_subfolders(OBS_CONFIG_PTH, OUTDATED_FOLDER)
