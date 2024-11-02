import cv2
import numpy as np


def get_undistort_image(image, camera_matrix, distort_coeffs, distort_type):
    if distort_type == "fisheye":
        R = np.eye(3)
        mapx, mapy = cv2.fisheye.initUndistortRectifyMap(camera_matrix, distort_coeffs, R, camera_matrix, image.shape[:2], cv2.CV_32FC1)

        undistort_image = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
    else:
        undistort_image = cv2.undistort(image, camera_matrix, distort_coeffs)

    return undistort_image
