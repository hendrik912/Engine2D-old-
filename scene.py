from input_handler import *
import entities
import pygame
import components
import colors
import numpy as np
import game_state
import quadtree
import collision
import utility
import terrain
import math


class Scene:

    def __init__(self, width, height):
        self.entities = []
        self.width = width
        self.height = height
        self.camera_offset = [0, 0]
        self.quadtree = quadtree.QuadTree(0, (0, 0, width, height), self)
        self.transformed_entity_pts = {}

    def update(self, elapsed_time):
        self.quadtree.clear()

        for entity in self.entities:

            # create the transformed points top down
            if entity.parent is None:

                # dont transform if the entity is static and already has transformed pts
                if entity.move_component is None:
                    try:
                        tep = self.transformed_entity_pts[entity.id]
                    except KeyError:
                        entities.calculate_transformed_pts_topdown(entity, [], self.transformed_entity_pts)
                else:
                    entities.calculate_transformed_pts_topdown(entity, [], self.transformed_entity_pts)
            entity.update(self, elapsed_time)

        for entity in self.entities:
            try:
                comp = entity.components[components.CollisionComponent]
                self.resolve_collision(entity, elapsed_time)
                self.quadtree.insert(entity)
            except KeyError:
                pass

    def resolve_collision(self, entity, elapsed_time):

        neighbors = []
        self.quadtree.retrieve(neighbors, entity)

        for neighbor in neighbors:

            if entity != neighbor:

                mtv = collision.check_collision(entity, neighbor, self)

                if mtv is not False:

                    if entity.move_component is not None:
                        entity.move_component.vel *= 0
                        entity.pos[0] -= mtv[0]
                        entity.pos[1] -= mtv[1]

                    if neighbor.move_component is not None:
                        neighbor.move_component.vel *= 0
                        neighbor.pos[0] += mtv[0]
                        neighbor.pos[1] += mtv[1]

    def render(self, surface):

        if game_state.DEBUG:
            self.quadtree.render(surface, self.camera_offset)

        for ent in self.entities:
            ent.render(game_state.surface, self, self.camera_offset, game_state.DEBUG)

        pygame.display.flip()  # double buffering

    @staticmethod
    def clear(surface):
        surface.fill(colors.WHITE)

    def add_to_entities(self, entity):
        self.entities.append(entity)
        for key, child in entity.children.items():
            self.add_to_entities(child)


def setup(scene):
    InputHandler.set_key_bindings_default()

    """
    max_iteration = 500
    count = 0
    entityNum = 1
    min = 30
    max = 50

    while count < entityNum and max_iteration > 0:

        max_iteration -= 1
        radius = random.randint(min, max)

        x = float(random.randint(radius, game_state.WIDTH/2 - radius))
        y = float(random.randint(radius, game_state.HEIGHT/2 - radius))

        if count % 2 == 0:
            sh = shape.Rectangle(radius, radius)
        else:
            sh = shape.Circle(radius/2)
        m = entities.Entity(x, y, sh)

        add = True

        m.move_component = component.PhysicsComponent(m, radius)

        for entity in scene.entities:
            if collision.check_collision(m, entity) is not False:
                add = False
                break

        if add:
            scene.entities.append(m)
            count += 1
    """

    width = 50
    height = 50

    pts = [
        [+width / 2, -height / 2],  # tr
        [+width / 2, +height / 2],  # br
        [-width / 2, +height / 2],  # bl
        [-width / 2, -height / 2],  # tl
    ]

    entity = entities.Entity(1000, 100)
    entity.input_component = components.PlayerInputComponent(entity)
    #entity.render_component = components.PolygonRenderComponent(entity, pts, 1.2)
    entity.render_component = components.CircleRenderComponent(entity, 10, 10)
    entity.move_component = components.MoveComponent(entity, 10)
    entity.components[components.CameraComponent] = components.CameraComponent(entity)
    entity.components[components.GravityComponent] = components.GravityComponent(entity)
    entity.components[components.FrictionComponent] = components.FrictionComponent(entity, 0.2)
    entity.components[components.CollisionComponent] = components.CollisionComponent(entity)
    scene.add_to_entities(entity)

    entity = entities.Entity(200, 200)
    #entity.render_component = components.PolygonRenderComponent(entity, pts)
    entity.render_component = components.CircleRenderComponent(entity, 10, 2)
    entity.input_component = components.TestInputComponent(entity)
    entity.move_component = components.MoveComponent(entity, 10)
    entity.components[components.GravityComponent] = components.GravityComponent(entity)
    entity.components[components.FrictionComponent] = components.FrictionComponent(entity, 0.2)
    entity.components[components.CollisionComponent] = components.CollisionComponent(entity)
    scene.add_to_entities(entity)

    ########################################################################################################

    width = scene.width
    height = scene.height

    pts = [
        [+width / 2, -height / 2],  # tr
        [+width / 2, +height / 2],  # br
        [-width / 2, +height / 2],  # bl
        [-width / 2, -height / 2],  # tl
    ]

    entity = entities.Entity(width/2, height/2)
    entity.render_component = components.PolygonRenderComponent(entity, pts)
    entity.render_component.fill = False
    scene.add_to_entities(entity)

    # tree = entities.create_tree()
    # tree.components.append(components.CameraComponent(tree))
    # tree.input_component = components.PlayerInputComponent(tree)
    # scene.add_to_entities(tree)
    # count = count_entities(tree)
    # print(count)

    ########################################################################################################

    y_pos = scene.height - 50
    te = terrain.terrain_entity(50, scene.width, 0.1, 200, 200)
    te.pos[1] = y_pos
    te.pos[0] = te.render_component.bounding_radius() - 20

    scene.add_to_entities(te)

