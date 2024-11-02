import yaml
import numpy as np


def read_parameters_from_yaml(filename):
    with open(filename, 'r') as file:
        params = yaml.safe_load(file)

    # Extract rotation and translation parameters
    roll = params['rotation']['roll']
    pitch = params['rotation']['pitch']
    yaw = params['rotation']['yaw']
    tran_x = params['translation']['x']
    tran_y = params['translation']['y']
    tran_z = params['translation']['z']

    # Create rotation matrices
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])
    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])

    # Combine rotation matrices
    Rotation = R_z @ R_y @ R_x

    # Create 4x4 transformation matrix
    transformMatrix = np.eye(4)
    transformMatrix[:3, :3] = Rotation
    transformMatrix[:3, 3] = [tran_x, tran_y, tran_z]

    # Extract intrinsic camera matrix parameters
    f_x = params['intrinsic_matrix']['focal_length_x']
    f_y = params['intrinsic_matrix']['focal_length_y']
    c_x = params['intrinsic_matrix']['center_x']
    c_y = params['intrinsic_matrix']['center_y']

    # Create camera intrinsic matrix
    Camera_inMat = np.array([
        [f_x, 0, c_x],
        [0, f_y, c_y],
        [0, 0, 1]
    ], dtype=np.float64)

    transformMatrix_l2c = np.linalg.inv(transformMatrix)

    dist_coeffs = np.array([params["distort_param"]["k1"], params["distort_param"]["k2"], params["distort_param"]["p1"],
                            params["distort_param"]["p2"]], dtype=np.float64)

    return transformMatrix_l2c, Camera_inMat, dist_coeffs, params["intrinsic_matrix"]["distort_type"]
