import abc
import numpy as np
import Box2D.b2 as Box2D

from .viewer import Viewer
from .objects import Arm, Box, Goal


def rand_in_range(a, b):
    return a + (b - a) * np.random.rand()


class Environment(metaclass=abc.ABCMeta):
    
    def reset(self):
        return self._reset()

    @abc.abstractmethod
    def _reset(self):
        pass
    
    def render(self):
        self._render()
    
    @abc.abstractmethod
    def _render(self):
        pass
    
    def step(self, x):
        return self._step(x)
    
    @abc.abstractmethod
    def _step(self, x):
        pass
    
    
class OneArmCubePushing(Environment):
    
    def __init__(self):
        self.width = 400
        self.time_step = 1.0 / 60.0
        self.vel_iters = 6
        self.pos_iters = 2
        self.height = 300
        self.width_real = 0.4
        self.scale = self.width / self.width_real
        self.height_real = self.width_real * self.height / self.width
        self.origin = np.array([self.width / 2, self.height / 2])
        self.world = Box2D.world(gravity=(0.0, 0.0))
        
        # Insert objects, set position in _reset()
        self.box = Box(self.world, 0.0, 0.0, 0.0)
        self.goal = Goal(0.0, 0.0, 0.2 * np.sqrt(2))
        self.arm = Arm(self.world, 0.0, 0.0)
        self.viewer = None
        self._reset()
    
    def _reset(self):
        box_x = rand_in_range(-1.0, 1.0)
        box_y = rand_in_range(-0.5, 0.5)
        box_angle = rand_in_range(0, np.pi)
        self.box.box.position = (box_x, box_y)
        self.box.box.angle = box_angle
        goal_x = rand_in_range(-1.0, 1.0)
        goal_y = rand_in_range(-0.5, 0.5)
        self.goal.position = (goal_x, goal_y)
        while True:
            arm_x = rand_in_range(-1.0, 1.0)
            arm_y = rand_in_range(-0.5, 0.5)
            if np.linalg.norm([arm_x - box_x, arm_y - box_y]) > 0.4:
                self.arm.arm.position = (arm_x, arm_y)
                break
        self.drawables = [
            self.goal, self.arm, self.box
        ]
        return self._get_state()
        
    def _get_state(self):
        return np.array([
            *self.arm.arm.position,
            *self.arm.arm.linearVelocity,
            *self.box.box.position,
            self.box.box.angle,
            *self.box.box.linearVelocity,
            self.box.box.angularVelocity,
            *self.goal.position
        ])
    
    def _step(self, x):
        direction = x[:2]
        if np.linalg.norm(direction) > 0.0:
            direction /= np.linalg.norm(direction)
        norm = x[-1]
        self.arm.apply_force(*(norm * direction))
        self.world.Step(self.time_step, self.vel_iters, self.pos_iters)
        return (
            self._get_state(),
            0.0, # reward externally defined for now
            False,
            {}
        )
    
    def _render(self):
        if not self.viewer:
            self.viewer = Viewer(400, 300, 200, 150, 400 / 4)
        self.viewer.fill((240, 240, 240))
        for drawable in self.drawables:
            self.viewer.draw(drawable)
        self.viewer.render()
        
    def world2pixel(self, x, y):
        """
        Returns (xp, yp, scale), where:
        xp : int
            pixel coordinates corresponding to x
        yp : int
            pixel coordinates corresponding to y
        scale : float
            multiply by this to get corresponding distance in pixel space
        """
        pixel_x = x * self.width / self.width_real + self.origin[0]
        pixel_y = self.height - (y * self.height / self.height_real + self.origin[1])
        return int(pixel_x), int(pixel_y), self.width / self.width_real
