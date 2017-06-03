# Environments
import abc
import numpy as np
import Box2D.b2 as Box2D

from .viewer import Viewer
from .objects import Arm, Box


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
        self.time_step = 1.0 / 24.0
        self.vel_iters = 6
        self.pos_iters = 2
        self.height = 300
        self.width_real = 0.4
        self.scale = self.width / self.width_real
        self.height_real = self.width_real * self.height / self.width
        self.origin = np.array([self.width / 2, self.height / 2])
        self.world = Box2D.world(gravity=(0.0, 0.0))
        self.goal_position = (1.0, 0.0)
        self.goal_radius = 0.2 * np.sqrt(2)
        
        # For plotting model predictions
        self._traces = dict()
        
        # Insert objects, set position in _reset()
        self.box = Box(self.world, 0.0, 0.0, 0.0)
        self.arm = Arm(self.world, 0.0, 0.0)
        self.viewer = None
        self._state_scalar = 10.0
        self._reset()
    
    def _reset(self):
        self.box.body.position = (0.0, 0.0)
        self.box.body.angle = 0.0
        self.box.body.linearVelocity = (0.0, 0.0)
        self.box.body.angularVelocity = 0.0
        angle = 2 * np.pi * np.random.rand()
        self.arm.body.position = (0.25 * np.sqrt(2) * np.cos(angle), 0.25 * np.sqrt(2) * np.sin(angle))
        self.arm.body.linearVelocity = (0.0, 0.0)
        return self.get_state()
    
    def add_trace(self, key, state):
        if key not in self._traces:
            self._traces[key] = []
        self._traces[key].append(
            state / self._state_scalar
        )
        
    def get_state(self):
        return np.array([
            *self.arm.body.position,       # 0, 1
            *self.arm.body.linearVelocity, # 2, 3
            *self.box.body.position,       # 4, 5
            np.cos(self.box.body.angle), np.sin(self.box.body.angle),
            *self.box.body.linearVelocity, # 8, 9
            self.box.body.angularVelocity, # 10
            *self.goal_position            # 11, 12
        ]).astype(np.float32) * self._state_scalar
    
    def _step(self, x):
        u = np.zeros(2)
        if np.linalg.norm(x[:2]) > 0:
            u = x[-1] * np.array(x[:2]) / np.linalg.norm(x[:2])
        self.arm.body.ApplyForceToCenter(list(map(np.float64, u)), False)
        self.world.Step(self.time_step, self.vel_iters, self.pos_iters)
        return (
            self.get_state(),
            0.0, # reward externally defined for now
            False,
            {}
        )
    
    def _render(self):
        if not self.viewer:
            self.viewer = Viewer(400, 300, 200, 150, 400 / 4)
        self.viewer.fill('w')
        
        self.viewer.draw_circle(*self.goal_position, self.goal_radius, filled=False)
        for obj, color in [(self.box, 'r'), (self.arm, 'k')]:
            self.viewer.draw_box2d(
                obj.fixture.shape,
                obj.body.transform,
                color
            )
            
        for value in self._traces.values():
            X = np.array(value)
            self.viewer.draw_line(X[:, 0], X[:, 1], 'k')
            self.viewer.draw_line(X[:, 4], X[:, 5], (100, 0, 0))

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
