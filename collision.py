import numpy as np
import math
import utility
import components

def check_collision(a, b, scene):

    # circle circle
    if isinstance(a.render_component, components.CircleRenderComponent) and isinstance(b.render_component, components.CircleRenderComponent):
        return circle_circle_collision(a, b, scene)

    if circle_circle_overlap(a, b, scene): # bounding circle

        # polygon circle
        if isinstance(a.render_component, components.CircleRenderComponent) or isinstance(b.render_component, components.CircleRenderComponent):
            if isinstance(a.render_component, components.CircleRenderComponent):
                return circle_polygon_collision(a, b)
            else:
                return circle_polygon_collision(b, a)

        # convex polygon convex polygon
        return sat_collision(a, b, scene)

    return False


def circle_polygon_collision(circle, polygon):
    # search closest vertex from p to circle center

    p_vecs = []

    normals = get_normals(polygon.shape.rotated_points)
    min_axis = [0, 0]
    min_overlap = None

    for i in range(0, 4):
        p_vecs.append(np.array(polygon.shape.rotated_points[i]) + polygon.pos)

    for i in range(0, len(normals)):
        p_proj = get_min_max_proj(p_vecs, normals[i])

        r = circle.shape.get_bounding_radius()
        min_dot = np.dot(circle.pos, normals[i])
        max_dot = np.dot(circle.pos, normals[i])

        c_proj = [
            min_dot - r,
            max_dot + r
        ]

        if do_overlap(c_proj[0], c_proj[1], p_proj[0], p_proj[1]):
            return False

        overlap = get_overlap(c_proj[0], c_proj[1], p_proj[0], p_proj[1])

        if min_overlap is None:
            min_overlap = overlap
            min_axis = normals[i]
        elif min_overlap > overlap:
            min_overlap = overlap
            min_axis = normals[i]

    mtv = [min_overlap * min_axis[0], min_overlap * min_axis[1]]

    return mtv


def circle_circle_collision(a, b, scene):

    a_pos = scene.transformed_entity_pts[a.id][0]
    b_pos = scene.transformed_entity_pts[b.id][0]

    r = a.render_component.get_bounding_radius() + b.render_component.get_bounding_radius()
    dis = math.sqrt((a_pos[0] - b_pos[0]) * (a_pos[0] - b_pos[0]) + (a_pos[1] - b_pos[1]) * (a_pos[1] - b_pos[1]))

    if r < dis:
        return False

    dv = b_pos - a_pos
    dv = utility.normalize(dv) * (r - dis)

    return dv


def circle_circle_overlap(a, b, scene):

    a_pos = scene.transformed_entity_pts[a.id][0]
    b_pos = scene.transformed_entity_pts[b.id][0]

    r = a.render_component.bounding_radius() + b.render_component.bounding_radius()
    r *= r

    dis = (a_pos[0] - b_pos[0]) * (a_pos[0] - b_pos[0]) + \
          (a_pos[1] - b_pos[1]) * (a_pos[1] - b_pos[1])

    return r > dis


def get_min_max_proj(vecs, axis):
    # calculate the min and max projections of a
    min_dot = np.dot(vecs[0], axis)
    max_dot = np.dot(vecs[0], axis)

    for i in range(1, len(vecs)):
        dot = np.dot(vecs[i], axis)

        if min_dot > dot:
            min_dot = dot

        elif max_dot < dot:
            max_dot = dot

    return [min_dot, max_dot]


def sat_collision(a, b, scene):

    a_vecs = []
    b_vecs = []

    a_entry = scene.transformed_entity_pts[a.id]
    a_pos = a_entry[0]
    a_pts = a_entry[1]

    b_entry = scene.transformed_entity_pts[b.id]
    b_pos = b_entry[0]
    b_pts = b_entry[1]

    # muss hier wirklich noch die position hinzuaddiert werden?

    normals = get_normals(a_pts) + get_normals(b_pts)
    min_axis = [0, 0]
    min_overlap = None

    for i in range(0, len(a_pts)):
        ap = np.array(a_pts[i]) + a_pos
        a_vecs.append(ap)

    for i in range(0, len(b_pts)):
        bp = np.array(b_pts[i]) + b_pos
        b_vecs.append(bp)

    for i in range(0, len(normals)):
        a_proj = get_min_max_proj(a_vecs, normals[i])
        b_proj = get_min_max_proj(b_vecs, normals[i])

        if do_overlap(a_proj[0], a_proj[1], b_proj[0], b_proj[1]) > 0: # warum > 0 ?
            return False

        overlap = get_overlap(a_proj[0], a_proj[1], b_proj[0], b_proj[1])

        if min_overlap is None:
            min_overlap = overlap
            min_axis = normals[i]
        elif min_overlap > overlap:
            min_overlap = overlap
            min_axis = normals[i]

    mtv = [min_overlap * min_axis[0], min_overlap * min_axis[1]]

    return mtv


def do_overlap(min1, max1, min2, max2):
    return max2 < min1 or max1 < min2


def get_overlap(min1, max1, min2, max2):

    # was wenn min1 < min2 && max1 > max2 ?

    if max1 > min2:
        return max1 - min2
    else:
        return max2 - min1


def get_normals(points):
    normals = []

    length = len(points)

    for i in range(0, length - 1):
        segment = [
            points[i + 1][0] - points[i][0],
            points[i + 1][1] - points[i][1]
        ]

        normal = [-segment[1], segment[0]]  # left normal
        normal = utility.normalize(normal)
        normals.append(normal)

    segment = [
        points[0][0] - points[length - 1][0],
        points[0][1] - points[length - 1][1]
    ]

    normal = [-segment[1], segment[0]]  # left normal
    normal = utility.normalize(normal)
    normals.append(normal)

    return normals


def check_terrain(entity, terrain):

    if entity.physics_component is None or entity.graphics_component is None:
        return

    r = entity.shape.bounding_radius
    height = terrain.shape.get_height(entity.pos[0], terrain.pos)

    bounce = 0.8

    if entity.pos[1] + r > height:
        entity.pos[1] = height - r
        entity.physics_component.vel[1] *= -bounce

    return


def check_edges(entity, width, height):

    if entity.move_component is not None:
        r = entity.render_component.bounding_radius()
    else:
        return

    bounce = 0.8

    right = entity.pos[0] + r
    left = entity.pos[0] - r
    top = entity.pos[1] - r
    bot = entity.pos[1] + r

    if right > width:
        entity.pos[0] -= right - width
        entity.move_component.vel[0] *= -bounce

    elif left < 0:
        entity.pos[0] -= left
        entity.move_component.vel[0] *= -bounce

    if bot > height:
        entity.pos[1] -= bot - height
        entity.move_component.vel[1] *= -bounce

    elif top < 0:
        entity.pos[1] -= top
        entity.move_component.vel[1] *= -bounce


def wrap_around_edges(mover, width, height):

    x = mover.pos[0]
    y = mover.pos[1]

    if x > width:
        x = 0
    elif x < 0:
        x = width

    if y > height:
        y = 0
    elif y < 0:
        y = height

    mover.pos[0] = x
    mover.pos[1] = y


def collision_response(m1, m2):

    """
    Friction = -1 * ffac * |N| * vel
    """

    start_pos = m1.pos
    end_pos = m2.pos
    bounce = 0.5

    m = (start_pos[1] - end_pos[1]) / (start_pos[0] - end_pos[0])

    normal = np.array([1, m])
    mag = np.sqrt(normal.dot(normal))
    normal /= mag

    v = m1.vel
    vnew = bounce * (-2 * (v.dot(normal)) * normal + v)
    m1.vel = vnew

    v1 = m1.vel
    vnew1 = bounce * (-2 * (v1.dot(normal)) * normal + v1)
    m2.velocity = vnew1