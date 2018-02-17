from steering_behavior import *
import copy
import colors
import components
import pygame

#########################################################################################


class Entity:

    nextValidID = 0

    def __init__(self, x, y):
        self.id = self.set_id()
        self.set_id()
        self.parent = None
        self.children = {}

        self.pos = np.array([x, y], dtype=np.float32)
        self.up = np.array(game_state.UP, dtype=np.float32)
        self.side = np.array(game_state.LEFT, dtype=np.float32)

        self.components = {}
        self.move_component = None
        self.render_component = None
        self.input_component = None

    @staticmethod
    def set_id():
        Entity.nextValidID += 1
        return Entity.nextValidID - 1

    def render(self, surface, scene, camera_offset, debug=False):

        entry = scene.transformed_entity_pts[self.id]

        ##########################################################################################################
        pos = copy.deepcopy(entry[0])
        pts = entry[1]

        if self.render_component is not None:
            self.render_component.update(surface, pos, pts, self.up, self.side, camera_offset, debug)

        """
        if debug:
            start_pos = (int(pos[0] + camera_offset[0]), int(pos[1] + camera_offset[1]))
            for key, child in self.children.items():
                child_pos = scene.transformed_entity_pts[child.id][0]

                end_pos = (int(child_pos[0] + camera_offset[0]),
                           int(child_pos[1] + camera_offset[1]))

                pygame.draw.line(surface, colors.GRAY, start_pos, end_pos)
        """

    def set_parent(self, entity):
        self.remove_parent()
        self.parent = entity
        self.parent.children[self.id] = self

    def remove_parent(self):
        if self.parent is not None:
            del self.parent.children[self.id]

    def update_components(self, scene, time_elapsed):

        for key, component in self.components.items():
            component.update(scene)

        if self.input_component is not None:
            self.input_component.update(time_elapsed)

        if self.move_component is not None:
            self.move_component.update(time_elapsed)

    def update(self, scene, time_elapsed):
        self.update_components(scene, time_elapsed)


#########################################################################################

def calculate_transformed_pts_topdown(entity, transformations, transformation_map):

    pos = [entity.pos[0], entity.pos[1]]
    pts = copy.deepcopy(entity.render_component.points)

    utility.scale_points(pts, entity.render_component.scale)

    up = [entity.up[0], entity.up[1]]
    side = [entity.side[0], entity.side[1]]

    # go through all transformations of the parents
    for i in range(len(transformations) - 1, -1, -1):
        t = transformations[i]
        # rotation der pos:
        # ausrichtung des parents angewandt auf eigene pos
        utility.rotate_point(pos, t[1], t[2])
        pos[0] += t[0][0]
        pos[1] += t[0][1]

        # akkumulierte ausrichtung
        utility.rotate_point(up, t[1], t[2])
        utility.rotate_point(side, t[1], t[2])

    # add own transform
    transformations.append([[entity.pos[0], entity.pos[1]], entity.up, entity.side])

    # pass the transformations don to the children
    count = 1
    for key, child in entity.children.items():
        if count > 0:
            trans_cpy = copy.deepcopy(transformations)
            calculate_transformed_pts_topdown(child, trans_cpy, transformation_map)
        else:
            calculate_transformed_pts_topdown(child, transformations, transformation_map)
        count += 1

    utility.rotate_points(pts, up, side)
    transformation_map[entity.id] = [pos, pts]

#########################################################################################


def count_entities(entity):

    count = 1

    for key, child in entity.children.items():
        count += count_entities(child)

    return count

#########################################################################################


def create_tree():

    width = 10
    height = 10

    pts2 = [
        [+width / 2, -height / 2],  # tr
        [+width / 2, +height / 2],  # br
        [-width / 2, +height / 2],  # bl
        [-width / 2, -height / 2],  # tl
    ]

    root = Entity(200, 200)
    root.render_component = components.PolygonRenderComponent(root, pts2)

    x_offset = 200
    add_tree_nodes(root, 3, 2, pts2, width, height, x_offset)

    return root


def add_tree_nodes(parent, depth, num_nodes, pts, width, height, x_offset):
    if depth < 1:
        return
    for i in range(0, num_nodes):
        node = Entity(0, 0)
 #       node.input_component = components.TestInputComponent(node)
        node.render_component = components.PolygonRenderComponent(node, pts)
        node.set_parent(parent)
        node.pos[1] -= height * 5
        node.pos[0] = -x_offset/2 + i*x_offset

        add_tree_nodes(node, depth-1, num_nodes, pts, width, height, x_offset/2)










"""
    def set_transformed_pts_bu(self):

        pos = [self.pos[0], self.pos[1]]
        pts = copy.deepcopy(self.shape.points)

        # eigenrotation
        utility.rotate_points(pts, self.up, self.side)

        # accumulate parent transformations
        if self.parent is not None:
            self.parent.get_parent_transform(pos, pts)

        # apply parent transformation
        self.absolute_pos = pos

        utility.translate_points(pts, pos[0], pos[1])
        self.shape.transformed_pts = pts

    def get_parent_transform_bu(self, pos, pts):

        utility.rotate_point(pos, self.up, self.side)
        utility.rotate_points(pts, self.up, self.side)

        pos[0] += self.pos[0]
        pos[1] += self.pos[1]

        if self.parent is not None:
            self.parent.get_parent_transform(pos, pts)
"""