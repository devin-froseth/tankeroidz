""" 
    tankeroidz.game
    ~~~~~~~~~~~~~~~
    
    Tankeroidz game application/engine. Contains the Game class, which
    initializes the game and manages the game loop.
    
    :copyright: (C) 2014 Froseth, Devin and Palowitch, Brendon.
    :license: GPL, see LICENSE for more details.
"""
import pygame
import sys
import os
from pygame.locals import *

from screens import *
from console import *
import console
import config
import io_utils

class Game:
    """The game application; loads the game and manages the main loop."""

    def __init__(self):
        pygame.init()

        self.load()
        
        self.timer = pygame.time.Clock()
        
        # Must set logo before setting display mode
        logo = pygame.image.load('resources/logo32.png')
        pygame.display.set_icon(logo)
        
        pygame.display.set_caption(self.settings['title'])
        self.frame = pygame.display.set_mode((self.settings['width'],
            self.settings['height']))

        self.preload_images()
  
    def load(self):
        """Load settings and keybindings."""
        self.load_settings()
        self.load_keybindings()
            
    def load_settings(self):
        try:
            self.settings = io_utils.ini_to_dict("config/settings.ini")
        except IOError:
            self.settings = config.defaults['settings']
            console.warn("Failed to load game settings. Defaults loaded from " 
                "config.py.")
            
    def load_keybindings(self):
        try:
            kb = io_utils.ini_to_dict("config/keybinds.ini")
        except IOError:
            kb = config.defaults['keybindings']
            console.warn("Failed to load keybindings. Defaults loaded from "
                "config.py.")
        else: 
            # No error, but we still must convert dict values from str -> list
            for action in kb:
                key_list = []
                key_list_as_str = kb[action].split(",")
                
                for key in key_list_as_str:
                    # Fix issues with caps (a user manually edits keybinds.ini?)
                    key = key.upper() if len(key) > 1 else key.lower()
                    key = "K_" + key
                    
                    if key in globals():
                        key_list.append(globals()[key])
                
                kb[action] = key_list
                    
        self.keybindings = kb
    
    def preload_images(self):
        """Loads all png images in the './resources' directory and caches them
        by their file name. Assumes no two files have the same name."""
        images = io_utils.get_filenames_r('resources', 'png')
        
        for img_name in images:
            img = pygame.image.load(img_name).convert_alpha()
            img.set_colorkey((255, 0, 255)) # ugly purple is transparent
            
            io_utils.cache_image(io_utils.file_name(img_name), img)
        
    def start(self):
        """Prepare the game to start and begin the game loop."""
        #self.screen = None
        self.set_screen(TitleScreen(self))
        self.ticks = 0
        self.run()
    
    def run(self):
        """The game's main loop. The game processes input, runs its update
        logic, then renders to the window. The game runs indefinitely until
        the process is ended (preferably using a PyGame QUIT Event)."""
        while (True):
            self.process_input()
            self.update()
            self.render()
            self.timer.tick(self.settings['fps'])
    
    def process_input(self):
        """Process events and input such as keypresses, mouse button presses,
        and PyGame Events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                console.log("Thanks for playing " + self.settings['title'] + "!")
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE: # If ESC is pressed, QUIT the game
                    pygame.event.post(pygame.event.Event(QUIT))
                    
            self.screen.handle_input(event)
    
    def update(self):
        """Run the current screen's update logic."""
        self.screen.update()
        self.ticks += 1
    
    def render(self):
        """Render the current screen to the PyGame surface and update the
        display."""
        self.screen.render()
        pygame.display.flip()
    
    def set_screen(self, screen):
        """Sets the game's current screen, which represents its state."""
        if hasattr(self, "screen") and self.screen is not None:
            self.screen.exit()
        
        self.screen = screen
        self.screen.enter()