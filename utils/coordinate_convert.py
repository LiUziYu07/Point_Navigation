import numpy as np
import math


def get_transformation_pt(camera_matrix, dist_coeffs, distort_type, transform_matrix, image_width, image_height, pt):
    point_homogeneous = np.append(pt, 1)  # 转换为齐次坐标
    transformed_point = transform_matrix @ point_homogeneous  # 应用变换

    if distort_type == "fisheye":
        a, b = transformed_point[0] / transformed_point[2], transformed_point[1] / transformed_point[2]
        r = math.sqrt(a ** 2 + b ** 2)

        theta = math.atan(r)
        theta_d = theta * (1 + dist_coeffs[0] * theta ** 2 + dist_coeffs[1] * theta ** 4 + dist_coeffs[
            2] * theta ** 6 + dist_coeffs[3] * theta ** 8)

        x_prime = (theta_d / r) * a
        y_prime = (theta_d / r) * b

    elif distort_type == "undistort":
        a, b = transformed_point[0] / transformed_point[2], transformed_point[1] / transformed_point[2]
        x_prime = a
        y_prime = b

    elif distort_type == "non_fisheye":
        a, b = transformed_point[0] / transformed_point[2], transformed_point[1] / transformed_point[2]
        r = math.sqrt(a ** 2 + b ** 2)

        taylor_term = 1 + dist_coeffs[0] * r ** 2 + dist_coeffs[1] * r ** 4 + dist_coeffs[2] * r ** 6 + dist_coeffs[3] * r ** 8

        x_prime = a * taylor_term
        y_prime = b * taylor_term

    u = camera_matrix[0][0] * x_prime + camera_matrix[0][2]
    v = camera_matrix[1][1] * y_prime + camera_matrix[1][2]

    if u < 0 or v < 0 or u >= image_width or v >= image_height or transformed_point[2] < 0:
        return None

    dist = np.linalg.norm(transformed_point[:3])
    return u, v, dist
