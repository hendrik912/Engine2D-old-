import noise
import entities
import components
import utility


def generate_points(step, mag, step_offset, num, x_scale, x_offset):
        points = []
        for x in range(0, num):
            yy = mag * (noise.pnoise1(x * step + step_offset, octaves=2))
            xx = x * x_scale - x_offset
            points.append([xx, yy])
        return points


def split_into_parts(pts):
    points_list = []
    max_pts = 50
    part_pts = []
    p = pts[0]
    part_pts.append([p[0], p[1]])
    p = pts[1]
    part_pts.append([p[0], p[1]])

    i = 2
    while i < len(pts):

        p1 = pts[i-2]
        p2 = pts[i-1]
        p = pts[i]

        if len(part_pts) < max_pts and not to_the_left(p1, p2, p):
            part_pts.append([p[0], p[1]])
        else:
            points_list.append(part_pts)
            part_pts = []
            p = pts[i-1]
            part_pts.append([p[0], p[1]])
            p = pts[i]
            part_pts.append([p[0], p[1]])

        i += 1

    return points_list


def terrain_entity(x_step, width, pn_step, pn_step_offset, pn_mag):

    num_pts = int(width / x_step) + 6
    pts = generate_points(pn_step, pn_mag, pn_step_offset, num_pts, x_step, 0)
    points_list = split_into_parts(pts)

    terrain_ent = entities.Entity(0, 0, points_list[0])

    terrain_ent.render_component = components.PolygonRenderComponent(terrain_ent)
    terrain_ent.components[components.CollisionComponent] = components.CollisionComponent(terrain_ent)

    shift_center(terrain_ent)
    close_shape(terrain_ent.points, 50)

    # die erstellten shapes in entitäten übertragen
    for i in range(1, len(points_list)):
        pts = points_list[i]
        ent = entities.Entity(0, 0, pts)
        ent.render_component = components.PolygonRenderComponent(ent)
        ent.components[components.CollisionComponent] = components.CollisionComponent(ent)
        ent.set_parent(terrain_ent)

        shift_center(ent)
        ent.pos[0] -= x_step

        close_shape(ent.points, 50)
    return terrain_ent


def to_the_left(p1, p2, p):

    ori = (p2[0] - p1[0]) * (p[1] - p1[1]) - (p[0] - p1[0]) * (p2[1] - p1[1])
    if ori > 0:
        return False # right hand side
    else:
        return True


def close_shape(pts, specific_height=None):

    if specific_height is not None:
        max_y = specific_height
    else:
        max_y = pts[0][1]
        for p in pts:
            if p[1] > max_y:
                max_y = p[1]
        max_y += 5

    p = pts[len(pts)-1]
    pn = [p[0], max_y]
    pts.append(pn)
    p = pts[0]
    pn = [p[0], max_y]
    pts.append(pn)


def shift_center(entity):
    # only works if applied before close_shape(...)
    x_scale = entity.points[1][0] - entity.points[0][0]
    width = (len(entity.points)-1) * x_scale
    x_offset = entity.points[0][0]
    entity.pos[0] += width/2 + x_offset   # position mit rotationspunkt in der mitte

    for pt in entity.points:
        pt[0] -= (width/2 + x_offset)

























"""

 // Left test implementation given by Petr
    private static int Orientation(Point p1, Point p2, Point p)
    {
        // Determinant
        int Orin = (p2.X - p1.X) * (p.Y - p1.Y) - (p.X - p1.X) * (p2.Y - p1.Y);

        if (Orin > 0)
            return -1; //          (* Orientation is to the left-hand side  *)
        if (Orin < 0)
            return 1; // (* Orientation is to the right-hand side *)

        return 0; //  (* Orientation is neutral aka collinear  *)
    }

    
def crossproduct2D(p0, p1, p2):

    d1 = [0, 0]
    d2 = [0, 0]

    d1[0] = p1[0] - p0[0]
    d1[1] = p1[1] - p0[1]

    d2[0] = p2[0] - p1[0]
    d2[1] = p2[1] - p1[1]

      


    d1.x = p1.x - p0.x
    d1.y = p1.y - p0.y

    d2.x = p2.x - p1.x
    d2.y = p2.y - p1.y


 given p[k], p[k+1], p[k+2] each with coordinates x, y:
 dx1 = x[k+1]-x[k]
 dy1 = y[k+1]-y[k]
 dx2 = x[k+2]-x[k+1]
 dy2 = y[k+2]-y[k+1]
 zcrossproduct = dx1*dy2 - dy1*dx2

"""