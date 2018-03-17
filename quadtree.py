import pygame
import random
import colors
import game_state

class QuadTree:
    def __init__(self, level, bounds, scene):
        self.MAX_ENTITIES = 2
        self.MAX_LEVELS = 5
        self.level = level
        self.entities = []
        self.bounds = bounds
        self.nodes = []
        self.scene = scene

    def get_depth(self):

        if len(self.nodes) > 0:
            return self.nodes[0].getDepth()

        return self.level

    def render(self, surface, offset):

        b1 = self.bounds[0] * game_state.ZOOM + offset[0]
        b2 = self.bounds[1] * game_state.ZOOM + offset[1]
        b3 = self.bounds[2] * game_state.ZOOM
        b4 = self.bounds[3] * game_state.ZOOM
        nb = (b1, b2, b3, b4)

        pygame.draw.rect(surface, colors.GRAY, nb, 1)

        for node in self.nodes:
            if node is not None:
                node.render(surface, offset)

    def clear(self):
        self.entities = []

        for i in range(len(self.nodes), 0):
            self.nodes[i].clear()

        self.nodes = []

    def insert(self, entity):

        if len(self.nodes) > 0:
            index = self.get_quadrant(entity)

            if index is not None:

                self.nodes[index].insert(entity)
                return

        self.entities.append(entity)

        if len(self.entities) > self.MAX_ENTITIES and self.level < self.MAX_LEVELS:

            if len(self.nodes) == 0:
                self.split()

            i = 0

            while i < len(self.entities):

                index = self.get_quadrant(self.entities[i])

                if index is not None:

                    self.entities[i].quadrant = index + 1

                    self.nodes[index].insert(self.entities[i])
                    self.entities.pop(i)
                else:
                    i += 1

    def get_quadrant(self, entity):

        index = None

        pos = entity.transformed_pts[0]

        center = (self.bounds[0] + self.bounds[2] / 2,
                  self.bounds[1] + self.bounds[3] / 2)

        radius = entity.bounding_radius()


        entity_bounds = [
            pos[0] - radius,  # x min
            pos[1] - radius,  # y min

            pos[0] + radius,  # x max
            pos[1] + radius,  # y max
        ]

        # is the entity completely in the top or the bottom row?
        top = entity_bounds[1] + entity_bounds[3] < center[1]
        bottom = entity_bounds[1] > center[1]

        # is the entity completely in the left or right column?
        left = entity_bounds[0] + entity_bounds[2] < center[0]
        right = entity_bounds[0] > center[0]

        # selecting the quadrant
        if top:
            if right:  # quadrant 1
                index = 0
            elif left:  # quadrant 2
                index = 1
        elif bottom:
            if left:  # quadrant 3
                index = 2
            elif right:  # quadrant 4
                index = 3

        return index

    def split(self):

        sub_width = self.bounds[2] / 2
        sub_height = self.bounds[3] / 2
        x = self.bounds[0]
        y = self.bounds[1]

        self.nodes.append(QuadTree(self.level + 1, (x + sub_width, y, sub_width, sub_height), self.scene))  # quadrant 1
        self.nodes.append(QuadTree(self.level + 1, (x, y, sub_width, sub_height), self.scene))  # quadrant 2
        self.nodes.append(QuadTree(self.level + 1, (x, y + sub_height, sub_width, sub_height), self.scene))  # 3
        self.nodes.append(QuadTree(self.level + 1, (x + sub_width, y + sub_height, sub_width, sub_height), self.scene))  # 4

    def retrieve(self, neighbors, entity):

        if len(self.nodes) > 0:

            index = self.get_quadrant(entity)

            if index is not None:
                self.nodes[index].retrieve(neighbors, entity)
            else:
                for node in self.nodes:
                    node.retrieve(neighbors, entity)

        for entity in self.entities:
            neighbors.append(entity)

