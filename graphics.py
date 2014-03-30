import pygame

class Graphics(object):
    def __init__(self, surface):
        self.drawables = []
        self.surface = surface
        
    def add_drawable(self, drawable):
        self.drawables.append(drawable)
    
    def remove_drawable(self, drawable):
        if (drawable in self.drawables):
            self.drawables.remove(drawable)
            
    def clear(self):
        self.drawables = []

    def paint(self):
        for drawable in self.drawables:
            self.surface.blit(drawable.surface, drawable.point)
            
class Drawable(object):
    def __init__(self, surface=None, pos=(0,0)):
        self.surface = surface
        self.x = pos[0]
        self.y = pos[1]
    
    @staticmethod
    def load_image(path, pos=(0,0)):
        s = pygame.image.load(path)
        s.convert()
        s.set_colorkey((0, 0, 0))
        
        return Drawable(s, pos)
    
    @staticmethod
    def create_rect(rect, color):
        s = pygame.Surface((rect[2], rect[3]))
        
        if (len(color) > 3):
            s.set_alpha(color[3])
            
        s.fill(color)
        
        return Drawable(s, (rect[0], rect[1]))
    
    @staticmethod
    def create_circle(circle, color):
        r = circle[2] # radius
        d = r*2
        
        s = pygame.Surface((d, d))
        
        if (len(color) > 3):
            s.set_alpha(color[3])
        
        if (color[:3] == (0, 0, 0)):
            color = (1, 1, 1) # quick fix for colorkey
            
        pygame.draw.circle(s, color, (r, r), r)
        
        s.set_colorkey((0, 0, 0))
        
        return Drawable(s, (circle[0], circle[1]))
    
    @property
    def bounds(self):
        return self.surface.get_bounding_rect()
        
    @property
    def point(self):
        return self.x, self.y