import pygame
import pygame.gfxdraw
import Box2D.b2 as Box2D


class Viewer:
    
    def __init__(self, width, height, origin_x, origin_y, scale):
        self.height = height
        self.width = width
        self.scale = scale
        self.origin_x = origin_x
        self.origin_y = origin_y
        pygame.init()
        pygame.display.set_caption('Environment')
        self.surface = pygame.display.set_mode((width, height))
        
    def fill(self, color):
        self.surface.fill(color)
        
    def draw(self, drawable):
        if isinstance(drawable.shape, Box2D.circleShape):
            self._draw_circle(drawable)
        elif isinstance(drawable.shape, Box2D.polygonShape):
            self._draw_polygon(drawable)
        else:
            raise ValueError('Got type {}'.format(type(drawable.shape)))
            
    def render(self):
        pygame.display.flip()
            
    def _draw_circle(self, drawable):
        x, y = self.world2pixel(*(drawable.transform * drawable.shape.pos))
        if drawable.filled:
            pygame.gfxdraw.filled_circle(
                self.surface,
                x, y, int(self.scale * drawable.shape.radius),
                drawable.color
            )
        pygame.gfxdraw.aacircle(
            self.surface,
            x, y, int(self.scale * drawable.shape.radius),
            drawable.color
        )
        
    def _draw_polygon(self, drawable):
        transformed = [self.world2pixel(*(drawable.transform * s)) for s in drawable.shape.vertices]
        if drawable.filled:
            pygame.gfxdraw.filled_polygon(self.surface, transformed, drawable.color)
        pygame.gfxdraw.aapolygon(self.surface, transformed, drawable.color)
        
    def world2pixel(self, x, y):
        """
        Returns (xp, yp), where:
        xp : int
            pixel coordinates corresponding to x
        yp : int
            pixel coordinates corresponding to y
        """
        pixel_x = x * self.scale + self.origin_x
        pixel_y = self.height - (y * self.scale + self.origin_y)
        return int(pixel_x), int(pixel_y)
