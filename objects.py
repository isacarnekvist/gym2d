import Box2D.b2 as Box2D


class Drawable:

    @property
    def filled(self):
        return True

    @property
    def color(self):
        raise NotImplementedError

    @property
    def shape(self):
        raise NotImplementedError

    @property
    def transform(self):
        raise NotImplementedError


class Arm(Drawable):
    
    def __init__(self, world, x, y, color=(0, 0, 0)):
        self.arm = world.CreateDynamicBody(position=(x, y))
        self.arm.CreateCircleFixture(radius=0.05, density=32.0, friction=100.0)
        self.arm.linearDamping = 3.0
        self.arm.angularDamping = 100.0
        self._color = color
        
    @property
    def color(self):
        return self._color
    
    @property
    def shape(self):
        return self.arm.fixtures[0].shape
    
    @property
    def transform(self):
        return self.arm.transform
        
    def apply_force(self, x, y):
        self.arm.ApplyForceToCenter((x, y), True)


class Box(Drawable):

    def __init__(self, world, x, y, angle, color=(255, 0, 0)):
        self.box = world.CreateDynamicBody(position=(x, y))
        self.box.CreatePolygonFixture(box=(0.2, 0.2), density=0.5, friction=100.0)
        self.box.angle = angle
        self.box.linearDamping = 10.0
        self.box.angularDamping = 10.0
        self._color = color
        
    @property
    def color(self):
        return self._color
    
    @property
    def shape(self):
        return self.box.fixtures[0].shape
    
    @property
    def transform(self):
        return self.box.transform


class Goal(Drawable):

    def __init__(self, x, y, radius):
        super(Drawable).__init__()
        self._shape = Box2D.circleShape(radius=radius)
        self._transform = Box2D.transform((x, y), Box2D.rot(0.0))
        self.position = (x, y)
    
    @property
    def shape(self):
        return self._shape
    
    @property
    def transform(self):
        return self._transform
    
    @property
    def color(self):
        return (0, 0, 0)
    
    @property
    def filled(self):
        return False
