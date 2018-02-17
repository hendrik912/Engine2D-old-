import math
import time
import copy
import numpy as np
import random


def max_length_vec(pts):
    max_length = magnitude_square(pts[0])
    for i in range(1, len(pts)):
        length = magnitude_square(pts[i])
        if length > max_length:
            max_length = length
    return math.sqrt(max_length)


def rotate_points(points, v_up, v_side):
    for point in points:
        rotate_point(point, v_up, v_side)


def rotate_point(point, v_up, v_side):

    x = point[0]
    y = point[1]

    xneu = x * v_side[0] + y * v_up[0]
    yneu = x * v_side[1] + y * v_up[1]

    point[0] = xneu
    point[1] = yneu


def rotate_point_angle(point, radians):

    p = [0, 0]

    p[0] = point[0]*math.cos(radians) - point[1]*math.sin(radians)
    p[1] = point[0]*math.sin(radians) + point[1]*math.cos(radians)

    point[0] = p[0]
    point[1] = p[1]


def scale_points(points, scale):
    for point in points:
        point[0] *= scale
        point[1] *= scale


def translate_points(points, x, y):
    for point in points:
        point[0] += x
        point[1] += y


def get_time_in_ms():
    return int(round(time.time() * 1000))


def truncate(vec2, max_value):
    mag = magnitude(vec2)
    if mag > max_value:
        vec2 = (vec2 / mag) * max_value
    return vec2


def magnitude(vec2):
    return math.sqrt(vec2[0]**2 + vec2[1]**2)


def magnitude_square(vec2):
    return vec2[0] ** 2 + vec2[1] ** 2


def normalize(v):
    return v / np.linalg.norm(v)


def perpendicular(vec2):
    v = copy.copy(vec2)
    v[0] = vec2[1]
    v[1] = -vec2[0]
    return v


def angle_between(v1, v2):

    v1_u = normalize(v1)
    v2_u = normalize(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def dist_vec_on_torus(a, b, width, height):

    dx1 = a[0] - b[0]
    if dx1 < 0:
        dx1 *= -1

    # b is to the right of a
    if a[0] <= b[0]:
        dx2 = a[0] + width - b[0]
        # preserve sign
        left = False
    # b is to the left of a
    else:
        dx2 = b[0] + width - a[0]
        # preserve sign
        left = True

    if dx1 < dx2:
        dx = a[0] - b[0]  # to get the correct sign
    else:
        if left:
            dx = -dx2
        else:
            dx = dx2

    dy1 = a[1] - b[1]
    if dy1 < 0:
        dy1 *= -1

    # b is above a
    if a[1] <= b[1]:
        dy2 = a[1] + height - b[1]
        # if the wrap-around-distance is smaller then go right
        top = False
    # b is under a
    else:
        dy2 = b[1] + height - a[1]
        # if the wrap-around-distance is smaller, then go left
        top = True

    if dy1 < dy2:
        dy = a[1] - b[1]  # to get the correct sign
    else:
        if top:
            dy = -dy2
        else:
            dy = dy2

    return np.array([dx, dy])



