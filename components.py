from input_handler import Controls
from input_handler import InputHandler
import colors
import collision
import pyrr
import steering_behavior
import numpy as np
import utility
import game_state
import pygame
import copy


class BaseComponent:
    def __init__(self, owner):
        self.owner = owner

    def update(self, scene):
        return


class GravityComponent(BaseComponent):

    def __init__(self, owner, force_vec=np.array([0, 10])):
        super(GravityComponent, self).__init__(owner)
        self.force = force_vec

    def update(self, scene):
        if self.owner.move_component is not None:
            self.owner.move_component.apply_force(self.force)


class FrictionComponent(BaseComponent):

    def __init__(self, owner, coefficient):
        super(FrictionComponent, self).__init__(owner)
        self.coefficient = coefficient

    def update(self, scene):
        if self.owner.move_component is None:
            return

        vel = self.owner.move_component.vel
        friction = np.array([vel[0], vel[1]])
        if friction[0] != 0 or friction[1] != 0:
            utility.normalize(friction)
            friction_coefficient = 0.2
            friction[0] *= -friction_coefficient * self.owner.move_component.mass
            friction[1] *= -friction_coefficient * self.owner.move_component.mass
            self.owner.move_component.apply_force(friction)


class MoveComponent:

    def __init__(self, owner, mass):
        self.owner = owner
        self.mass = mass

        self.vel = np.array([0.0, 0.0])
        self.acc = np.array([0.0, 0.0])
        self.max_speed = 50

    def apply_force(self, force):
        self.acc += force / self.mass

    def update(self, time_elapsed):
        self.vel += self.acc * time_elapsed
        self.owner.pos += self.vel * time_elapsed
        self.acc *= 0


class CollisionComponent(BaseComponent):

    def __init__(self, owner):
        super(CollisionComponent, self).__init__(owner)

    def update(self, scene):
        collision.check_edges(self.owner, scene.width, scene.height)


class RenderComponent:

    def __init__(self, owner, line_color=colors.BLACK, fill_color=colors.GRAY, outline=True, fill=True):
        self.owner = owner

        self.line_color = line_color
        self.fill_color = fill_color
        self.fill = fill
        self.outline = outline

    def update(self, surface, pos, pts, v_up, v_side, offset, debug=False):
        if not debug:
            return

        final_pos = [pos[0], pos[1]]
        final_pos[0] *= game_state.ZOOM
        final_pos[1] *= game_state.ZOOM
        final_pos[0] += offset[0]
        final_pos[1] += offset[1]
        radius = self.owner.bounding_radius() * game_state.ZOOM

        pygame.draw.circle(surface, colors.GRAY, (int(final_pos[0]), int(final_pos[1])), int(radius), 1)

        start_pos = (int(final_pos[0]), int(final_pos[1]))
        end_pos = (int(final_pos[0] + v_up[0] * radius),
                   int(final_pos[1] + v_up[1] * radius))

        pygame.draw.line(surface, colors.GREEN, start_pos, end_pos)

        end_pos = (int(final_pos[0] + v_side[0] * radius),
                   int(final_pos[1] + v_side[1] * radius))

        pygame.draw.line(surface, colors.TEAL, start_pos, end_pos)


class CircleRenderComponent(RenderComponent):

    def __init__(self, owner, radius, scale=1.0, line_color=colors.BLACK, fill_color=colors.GRAY, fill=True):
        super(CircleRenderComponent, self).__init__(owner, [[0.0, 0.0], [0.0, radius]], scale, line_color, fill_color, fill)
        self.fill = fill

    def update(self, surface, pos, pts, v_up, v_side, offset, debug=False):

        final_pos = [pos[0], pos[1]]
        final_pos[0] *= game_state.ZOOM
        final_pos[1] *= game_state.ZOOM
        final_pos[0] += offset[0]
        final_pos[1] += offset[1]
        radius = self.bounding_radius() * game_state.ZOOM

        if self.fill:
            pygame.draw.circle(surface, self.fill_color, (int(final_pos[0]), int(final_pos[1])), int(radius), 0)

        super(CircleRenderComponent, self).update(surface, pos, pts, v_up, v_side, offset, debug)

        if self.outline:
            pygame.draw.circle(surface, self.line_color, (int(final_pos[0]), int(final_pos[1])), int(radius), 1)


class PolygonRenderComponent(RenderComponent):

    def __init__(self, owner, line_color=colors.BLACK, fill_color=colors.GRAY, fill=True):
        super(PolygonRenderComponent, self).__init__(owner, line_color, fill_color, fill)

    def update(self, surface, pos, pts, v_up, v_side, offset, debug=False):
        final_pos = [pos[0], pos[1]]
        final_pos[0] *= game_state.ZOOM
        final_pos[1] *= game_state.ZOOM
        final_pos[0] += offset[0]
        final_pos[1] += offset[1]

        # extrem suboptimal
        cpy_pts = copy.deepcopy(pts)

        utility.scale_points(cpy_pts, game_state.ZOOM)
        utility.translate_points(cpy_pts, final_pos[0], final_pos[1])

        if self.fill:
            pygame.draw.polygon(surface, self.fill_color, cpy_pts, 0)

        if self.outline:
            pygame.draw.polygon(surface, self.line_color, cpy_pts, 1)

        super(PolygonRenderComponent, self).update(surface, pos, pts, v_up, v_side, offset, debug)


class InputComponent(BaseComponent):

    def __init__(self, owner):
        super(InputComponent, self).__init__(owner)

        self.max_turn_rate = 0.3
        self.max_speed_forward = 1.0
        self.max_speed_side = 0.3
        self.max_speed_backward = 0.5

        # from -1 to 1
        self.move_backward_forward = 0.0
        self.move_left_right = 0.0
        self.turn = 0.0

    def update(self, time_elapsed):

        if self.owner.move_component is None:
            return

        speed = self.owner.move_component.max_speed
        heading = self.owner.up
        right = -self.owner.side

        move_force = np.array([0.0, 0.0])

        side = np.array([
            self.owner.side[0] * self.max_turn_rate * self.turn,
            self.owner.side[1] * self.max_turn_rate * self.turn
        ])

        if self.move_left_right != 0.0:
            move_force[0] -= right[0] * self.move_left_right * speed
            move_force[1] -= right[1] * self.move_left_right * speed
            self.move_left_right = 0.0

        if self.move_backward_forward != 0.0:
            move_force[0] += heading[0] * self.move_backward_forward * speed
            move_force[1] += heading[1] * self.move_backward_forward * speed
            self.move_backward_forward = 0.0

        if self.turn != 0.0:
            self.owner.up[0] += side[0]
            self.owner.up[1] += side[1]
            self.owner.up = utility.normalize(self.owner.up)
            self.owner.side = utility.perpendicular(self.owner.up)
            self.turn = 0.0

        length = pyrr.vector3.length(move_force)

        if length > 0.1:
            self.owner.move_component.apply_force(move_force)


class PlayerInputComponent(InputComponent):

    def __init__(self, owner):
        super(PlayerInputComponent, self).__init__(owner)

    def update(self, time_elapsed):
        super(PlayerInputComponent, self).update(time_elapsed)

        running = InputHandler.controls[Controls.run]

        if InputHandler.controls[Controls.move_forward]:
            if running:
                self.move_backward_forward = self.max_speed_forward
            else:
                self.move_backward_forward = self.max_speed_forward/2

        if InputHandler.controls[Controls.move_backward]:
            if running:
                self.move_backward_forward = -self.max_speed_forward
            else:
                self.move_backward_forward = -self.max_speed_forward / 2

        if InputHandler.controls[Controls.move_left]:
            if running:
                self.move_left_right = -self.max_speed_side
            else:
                self.move_left_right = -self.max_speed_side / 2

        if InputHandler.controls[Controls.move_right]:
            if running:
                self.move_left_right = self.max_speed_side
            else:
                self.move_left_right = self.max_speed_side / 2

        if InputHandler.controls[Controls.turn_right]:
            if running:
                self.turn = -self.max_turn_rate
            else:
                self.turn = -self.max_turn_rate / 2

        if InputHandler.controls[Controls.turn_left]:
            if running:
                self.turn = self.max_turn_rate
            else:
                self.turn = self.max_turn_rate / 2


class SteeringBehaviorInputComponent(BaseComponent):

    def __init__(self, owner):
        super(SteeringBehaviorInputComponent, self).__init__(owner)
        self.steering = steering_behavior.SteeringBehavior(self.owner)
        self.steering.wander_on()

    def update(self, time_elapsed):
        super(SteeringBehaviorInputComponent, self).update(time_elapsed)

        print(self.steering.calculate())


   #     self.owner.apply_force(self.steering.calculate())


class CameraComponent(BaseComponent):
    def __init__(self, owner):
        super(CameraComponent, self).__init__(owner)

    def update(self, scene):
        pos = self.owner.transformed_pts[0]

        scene_width = scene.width * game_state.ZOOM
        scene_height = scene.height * game_state.ZOOM

        x = pos[0] * game_state.ZOOM
        if x <= game_state.WIDTH / 2:
            scene.camera_offset[0] = 0
        elif x >= (scene_width - game_state.WIDTH / 2):
            scene.camera_offset[0] = - (scene_width - game_state.WIDTH)
        else:
            dis = game_state.WIDTH / 2 - x
            scene.camera_offset[0] = dis

        y = pos[1] * game_state.ZOOM
        if y <= game_state.HEIGHT / 2:
            scene.camera_offset[1] = 0
        elif y >= (scene_height - game_state.HEIGHT / 2):
            scene.camera_offset[1] = - (scene_height - game_state.HEIGHT)
        else:
            dis = game_state.HEIGHT / 2 - y
            scene.camera_offset[1] = dis
