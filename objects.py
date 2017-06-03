# Objects
import Box2D.b2 as Box2D


class Arm:
    
    def __init__(self, world, x, y, color=(0, 0, 0)):
        self.body = world.CreateDynamicBody(position=(x, y))
        self.fixture = self.body.CreateCircleFixture(
            radius=0.05,
            density=32.0,
            friction=100.0
        )
        self.body.linearDamping = 3.0
        self.body.angularDamping = 100.0


class Box:

    def __init__(self, world, x, y, angle, color=(255, 0, 0)):
        self.body = world.CreateDynamicBody(position=(x, y))
        self.fixture = self.body.CreatePolygonFixture(
            box=(0.2, 0.2), density=0.5, friction=100.0
        )
        self.body.angle = angle
        self.body.linearDamping = 4.0
        self.body.angularDamping = 4.0
