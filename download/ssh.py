import paramiko
from scp import SCPClient
import os
from config.ros import ROS_IP, ROS_HOST_NAME, ROS_IMAGE_PTH, ROS_JSON_PTH, ROS_PCD_PTH


def create_ssh_client(hostname, port, username):
    """创建SSH客户端，不加载系统主机密钥"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username)
    return client


def download_directory(scp_client, remote_dir, local_dir):
    """从远程目录下载到本地目录"""
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    scp_client.get(remote_dir, local_dir, recursive=True)


def delete_remote_subdirectories(ssh_client, remote_dir):
    """删除远程目录中的子文件夹和文件，但保留顶层文件夹"""
    # 获取远程目录下的所有子文件夹和文件
    stdin, stdout, stderr = ssh_client.exec_command(f'ls -A {remote_dir}')
    sub_items = stdout.read().decode().splitlines()

    # 逐个删除子文件夹和文件
    for item in sub_items:
        ssh_client.exec_command(f'rm -rf {os.path.join(remote_dir, item)}')


def download_folders(hostname, port, username, remote_dirs, local_base_dir):
    """从远程服务器下载指定文件夹到本地并删除其子文件夹和文件"""
    ssh_client = create_ssh_client(hostname, port, username)
    scp_client = SCPClient(ssh_client.get_transport())

    for remote_dir in remote_dirs:
        local_dir = os.path.join(local_base_dir, os.path.basename(remote_dir))
        download_directory(scp_client, remote_dir, local_dir)
        delete_remote_subdirectories(ssh_client, remote_dir)  # 删除子文件夹和文件

    scp_client.close()
    ssh_client.close()


if __name__ == '__main__':
    # 配置服务器信息和文件夹路径
    hostname = ROS_IP  # 服务器IP地址
    port = 22  # SSH端口，默认为22
    remote_dirs = [
        ROS_IMAGE_PTH,
        ROS_PCD_PTH,
        ROS_JSON_PTH
    ]
    local_base_dir = 'D:\CEG5003_PointNav\data\obs'  # 本地存储的基础路径

    # 执行下载和删除子文件夹和文件
    download_folders(ROS_IP, 22, ROS_HOST_NAME, remote_dirs, local_base_dir)
