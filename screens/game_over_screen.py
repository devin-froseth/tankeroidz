import pygame
import screen
import title_screen
from pygame.locals import *

class GameOverScreen(screen.Screen):
    def create(self):
        pass
        
    def handle_input(self, event):
        if (event.type == KEYDOWN):
            if (event.key == K_SPACE):
                self.game.set_screen(title_screen.TitleScreen(self.game))
    
    def render(self):
        self.game.frame.fill((128, 128, 0))
