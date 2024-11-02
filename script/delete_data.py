import os
import shutil
from config.data import OBS_CONFIG_PTH, OUTDATED_FOLDER


def clear_folder_contents(folder_paths):
    """
    清空指定文件夹中的内容，但保留文件夹本身。

    :param folder_paths: 列表，包含要清空的文件夹路径
    """
    for folder_path in folder_paths:
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # 删除文件或符号链接
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # 删除文件夹及其内容
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            print(f"The folder {folder_path} does not exist.")


if __name__ == "__main__":
    folder_paths = [OBS_CONFIG_PTH, OUTDATED_FOLDER]
    clear_folder_contents(folder_paths)
