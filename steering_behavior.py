import utility
import numpy as np
import game_state
import random
import math


class Action:

    seek = 0
    flee = 1

    pursuit = 2
    evade = 3

    wander = 4
    nothing = 5


class SteeringBehavior:

    def __init__(self, agent):
        self.agent = agent
        self.target_agent1 = None
        self.target_agent2 = None
        self.target = None
        self.action = Action.wander

        self.wander_radius = 10
        self.wander_distance = 40.0
        self.wander_jitter = 5

        # test test test

        # stuff for the wander behavior
        theta = random.uniform(0, 2*math.pi)
        # create a vector to a target position on the wander circle
        self.wander_target = np.array([
            self.wander_radius * math.cos(theta),
            self.wander_radius * math.sin(theta),
        ])


    """
     //stuff for the wander behavior
  double theta = RandFloat() * TwoPi;

  //create a vector to a target position on the wander circle
  m_vWanderTarget = Vector2D(m_dWanderRadius * cos(theta),
                              m_dWanderRadius * sin(theta));

    
    """

    def pursuit_on(self, prey):
        self.target_agent1 = prey
        self.action = Action.pursuit

    def wander_on(self):
        self.action = Action.wander

    def flee_on(self, pursuer):
        self.action = Action.flee
        self.target_agent1 = pursuer

    def evade_on(self, pursuer):
        self.action = Action.evade
        self.target_agent1 = pursuer

    def seek(self, target_pos, on_torus=True):

        if on_torus:
            dv = utility.dist_vec_on_torus(target_pos, self.agent.pos, game_state.WIDTH, game_state.HEIGHT)
            desired_vel = self.agent.max_speed * utility.normalize(dv)
        else:
            desired_vel = self.agent.max_speedmax_speed * utility.normalize(target_pos - self.agent.pos)

        return desired_vel - self.agent.vel

    def flee(self, target_pos, on_torus=True):

        panic_dis = 100.0 * 100.0

        if on_torus:
            dv = utility.dist_vec_on_torus(self.agent.pos, target_pos, game_state.WIDTH, game_state.HEIGHT)
            distance = utility.magnitude_square(dv)
        else:
            dv = self.agent.pos - target_pos
            distance = utility.magnitude_square(self.agent.pos - target_pos)

        if distance > panic_dis:
            return np.array([0.0, 0.0])

        desired_vel = self.agent.max_speed * utility.normalize(dv)
        return desired_vel - self.agent.vel

    def arrive(self, target_pos, deceleration=3, on_torus=True):

        to_target = utility.dist_vec_on_torus(target_pos, self.agent.pos, game_state.WIDTH, game_state.HEIGHT)
        dist = utility.magnitude(to_target)

        if dist <= 0:
            return np.array([0,0])

        if deceleration > 5:
            deceleration = 5
        elif deceleration < 1:
            deceleration = 1

        deceleration_tweaker = 0.5

        speed = dist / float(deceleration) * deceleration_tweaker
        if speed > self.agent.max_speed:
            speed = self.agent.max_speed

        if on_torus:
            desired_vel = speed * utility.normalize(to_target)
        else:
            desired_vel = (speed/dist) * (target_pos - self.agent.pos)
        return desired_vel - self.agent.vel

    def pursuit(self, evader, on_torus=True):
        # if the evader is ahead and facing the agent we can just seek
        to_evader = evader.pos - self.agent.pos
        relative_heading = np.dot(self.agent.heading, evader.heading)

        if np.dot(to_evader, self.agent.heading) and relative_heading < -0.95: # acos(0.95)=18degs
            return self.seek(evader.pos)

        evader_speed = utility.magnitude(evader.vel)

        # predict where the evader will be
        look_ahead_time = utility.magnitude(to_evader) / (self.agent.max_speed + evader_speed)
        look_ahead_time += self.turn_around_time(evader.pos)
        future_pos = evader.pos + evader.vel * look_ahead_time
        return self.seek(future_pos)

    def evade(self, pursuer):
        to_pursuer = pursuer.pos - self.agent.pos
        pursuer_speed = utility.magnitude(pursuer.vel)
        look_ahead_time = utility.magnitude(to_pursuer) / (self.agent.max_speed + pursuer_speed)
        future_pos = pursuer.pos + pursuer.vel * look_ahead_time
        return self.flee(future_pos)

    def wander(self):

        self.wander_target += np.array([random.uniform(-1, 1) * self.wander_jitter, random.uniform(-1,1) * self.wander_jitter])
        self.wander_target = self.wander_radius * utility.normalize(self.wander_target)

        target_local = self.wander_target + np.array([self.wander_distance, 0])
        utility.rotate_point(target_local, self.agent.side, self.agent.heading)
        target_world = self.agent.pos + target_local

        """
        circle_pos = np.array([self.wander_distance, 0])
        utility.rotate_point(circle_pos, self.agent.side, self.agent.heading)
        circle_pos += self.agent.pos

        pygame.draw.circle(engine.surface, color.RED, [int(circle_pos[0]), int(circle_pos[1])], self.wander_radius, 1)
        pygame.draw.circle(engine.surface, color.RED, [int(target_world[0]), int(target_world[1])], 3)
        """

        return target_world - self.agent.pos

    def do_nothing(self):
        return np.array([0, 0])

    def turn_around_time(self, to_target):

        to_target = utility.normalize(to_target)
        dot = np.dot(self.agent.heading, to_target)
        coefficient = 0.5

        return (dot - 1.0) * -coefficient

    def calculate(self):

        if self.action == Action.wander:
            return self.wander()
        elif self.action == Action.seek:
            return self.seek(self.target_agent1.pos)
        elif self.action == Action.flee:
            return self.flee(self.target_agent1.pos)
        elif self.action == Action.pursuit:
            return self.pursuit(self.target_agent1)
        elif self.action == Action.evade:
            return self.evade(self.target_agent1)
        else:
            return self.do_nothing()



        #      return self.seek(pygame.mouse.get_pos())
        #return self.flee(pygame.mouse.get_pos())
        #return self.arrive(pygame.mouse.get_pos(), 5)



