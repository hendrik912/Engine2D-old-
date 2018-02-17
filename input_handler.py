from enum import Enum
import pygame


class Controls(Enum):
    unset = -1
    move_forward = 0
    move_backward = 1
    move_left = 2
    move_right = 3
    turn_left = 4
    turn_right = 5
    run = 6
    jump = 7


# keys -> control -> bool

class InputHandler:

    mouse_x_offset = 0
    mouse_y_offset = 0
    mouse_scroll = 0

    # map from key to action
    keys = {
        pygame.K_w: Controls.unset,
        pygame.K_a: Controls.unset,
        pygame.K_s: Controls.unset,
        pygame.K_d: Controls.unset,
        pygame.K_q: Controls.unset,
        pygame.K_e: Controls.unset,
        pygame.K_SPACE: Controls.unset,
        pygame.K_LSHIFT: Controls.unset,
    }

    # map from action to bool
    controls = {
        Controls.move_forward: False,
        Controls.move_backward: False,
        Controls.move_left: False,
        Controls.move_right: False,
        Controls.turn_left: False,
        Controls.turn_right: False,
        Controls.jump: False,
        Controls.unset: False,
        Controls.run: False,
    }

    @staticmethod
    def set_key_bindings_default():

        InputHandler.keys[pygame.K_w] = Controls.move_forward
        InputHandler.keys[pygame.K_s] = Controls.move_backward
        InputHandler.keys[pygame.K_a] = Controls.move_left
        InputHandler.keys[pygame.K_d] = Controls.move_right
        InputHandler.keys[pygame.K_e] = Controls.turn_right
        InputHandler.keys[pygame.K_q] = Controls.turn_left
        InputHandler.keys[pygame.K_SPACE] = Controls.jump
        InputHandler.keys[pygame.K_LSHIFT] = Controls.run
