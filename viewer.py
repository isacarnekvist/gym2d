import pygame
import numpy as np
import pygame.gfxdraw
import Box2D.b2 as Box2D


def string_to_color(arg):
    if arg in ['w', 'white']:
        return (255, 255, 255)
    if arg in ['b', 'blue']:
        return (0, 0, 255)
    if arg in ['r', 'red']:
        return (255, 0, 0)
    if arg in ['k', 'black']:
        return (0, 0, 0)
    if arg in ['g', 'green']:
        return (0, 255, 0)
    if arg in ['y', 'yellow']:
        return (255, 255, 0)
    if arg in ['gray']:
        return (128, 128, 128)
    if arg in ['pink']:
        return (255, 180, 180)


class Viewer:
    """
    origin_x : int
        x-coordinate of origin in pixel space
    origin_y : int
        y-coordinate of origin in pixel space
    scale : float
        display pixel width / corresponding real world width
    """
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
        if not isinstance(color, tuple):
            color = string_to_color(color)
        self.surface.fill(color)
        
    def render(self):
        pygame.display.flip()
        self.surface.fill((255, 255, 255))

    def draw_circle(self, x, y, radius, color='b', filled=True):
        if not isinstance(color, tuple):
            color = string_to_color(color)
        xp, yp = self.world2pixel(x, y)
        pygame.gfxdraw.aacircle(
            self.surface, xp, yp, int(radius * self.scale), color
        )
        if filled:
            pygame.gfxdraw.filled_circle(
                self.surface, xp, yp, int(radius * self.scale), color
            )

    def draw_line(self, xs, ys, color='b'):
        if not isinstance(color, tuple):
            color = string_to_color(color)
        coords = list(map(lambda arg: self.world2pixel(*arg), zip(xs, ys)))
        for i in range(len(coords) - 1):
            if np.max(np.abs(coords[i])) > 30000:
                continue
            if np.max(np.abs(coords[i + 1])) > 30000:
                continue
            pygame.gfxdraw.line(
                self.surface,
                coords[i][0],
                coords[i][1],
                coords[i + 1][0],
                coords[i + 1][1],
                color
            )

    def draw_polygon(self, vertices, color='b', filled=True):
        if not isinstance(color, tuple):
            color = string_to_color(color)
        vertices.append(vertices[0])
        pygame.gfxdraw.aapolygon(self.surface, vertices, color)
        if filled:
            pygame.gfxdraw.filled_polygon(self.surface, vertices, color)
            
    def draw_box2d(self, shape, transform, color='b', filled=True):
        if isinstance(shape, Box2D.circleShape):
            x, y = transform * shape.pos
            self.draw_circle(x, y, shape.radius, color=color, filled=filled)
        elif isinstance(shape, Box2D.polygonShape):
            vertices = [
                self.world2pixel(*(transform * vertex))
                for vertex in shape.vertices
            ]
            self.draw_polygon(vertices, color=color, filled=filled)
        else:
            raise ValueError('Got type {}'.format(type(drawable.shape)))

    def render(self):
        pygame.display.flip()

    def _draw_polygon(self, drawable):
        transformed = [self.world2pixel(*(drawable.transform * s)) for s in drawable.shape.vertices]
        if drawable.filled:
            pygame.gfxdraw.filled_polygon(self.surface, transformed, drawable.color)
        pygame.gfxdraw.aapolygon(self.surface, transformed, drawable.color)

        pass
        
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
