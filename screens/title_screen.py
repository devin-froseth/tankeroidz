import pygame
import screen
import play_screen
import io_utils
from pygame.locals import *
import ui

class TitleScreen(screen.Screen):
    STATE_SPLASH = 0
    STATE_SETTINGS = 1
    STATE_TANK_SELECT = 2

    def create(self):
        self.difficulty = 'easy'
        
        self.bg = io_utils.get_image("splash")
        self.create_ui()
    
    def create_ui(self):
        self.settings_ui = ui.load_ui('resources/ui/settings_menu.ui',
            (self.game.settings['width'], self.game.settings['height']))
            
        for component in self.settings_ui.components:
            self.settings_ui.center_component(component.name, 1, 0)
            
        self.create_tank_ui()
        
    def create_tank_ui(self):
        self.tanks_by_key = {}
    
        tank_ui = ui.load_ui('resources/ui/tank_select.ini',
            (self.game.settings['width'], self.game.settings['height']))
        
        tank_x, tank_y = 54, 100
        pad_x, pad_y = 60, 40
        
        items_per_row = 4
        x_offset, y_offset = 0, 0
        x, y = 0, 0
        item_count = 0

        # TODO: Hard coded values need to be replaced (see commented code)
        # The math works, but there's a better way to do this and the values
        # can be hard-coded for now
        '''max_x = items_per_row * (tank_x + pad_x)
        max_y = (len(io_utils.image_cache) / 2 + 1) * (tank_y + pad_y)
        
        x_offset = (self.game.settings['width'] - max_x) / 2
        y_offset = (self.game.settings['height'] - max_y) / 2'''
        x_offset, y_offset = 40, 60
        
        for k, v in io_utils.image_cache.iteritems():
            if k.startswith("tank_") and "classic" not in k:
                id = k
                tank_name = k.split("_")[-1]
                
                item_count += 1 # also serves as the key bind if < 10 tanks
                self.tanks_by_key[item_count] = k
                
                bounds_ = x+x_offset, y+y_offset, tank_x, tank_y
                label_bounds = x+x_offset, y+tank_y+y_offset, tank_x, tank_y
                
                tank_label = ui.Label(text=(str(item_count) + ". " + tank_name),
                    x=x+x_offset, y=y+tank_y+y_offset, color=(150,225,225))
                
                tank_ui["SEL_"+id] = ui.UIObject(texture=v, bounds=bounds_)
                tank_ui["LABEL_"+id] = tank_label
                tank_label.x -= (tank_label.width - tank_x) / 2
                
                if item_count % items_per_row == 0:
                    x = 0
                    y += tank_y + pad_y
                else:
                    x += tank_x + pad_x
        
        w, h = self.game.settings['width'], self.game.settings['height']
        tank_ui.center_component('title', 1, 0)
        self.tank_ui = tank_ui
        
    def handle_input(self, event):
    
        if self.state == TitleScreen.STATE_SPLASH:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.set_state(TitleScreen.STATE_SETTINGS)
                    
        elif self.state == TitleScreen.STATE_SETTINGS:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.set_state(TitleScreen.STATE_TANK_SELECT)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = self.settings_ui.get_component_at_pos(pygame.mouse.get_pos())
                    if c is not None:
                        if c.name.startswith('button_'):
                            self.difficulty = c.name.split('_')[-1]
                            self.set_state(TitleScreen.STATE_TANK_SELECT)
                            return
                
        elif self.state == TitleScreen.STATE_TANK_SELECT:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.start_playing()
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = self.tank_ui.get_component_at_pos(pygame.mouse.get_pos())
                    if c is not None:
                        if "tank_" in c.name:
                            tank_name = c.name.split("_")[-1]
                            self.start_playing(tank_name)
    
    def start_playing(self, tank_name='classic'):
        self.game.set_screen(play_screen.PlayScreen(self.game, tank=tank_name,
            difficulty=self.difficulty))
    
    def update(self):
        pass
    
    def render(self):
        if self.state == TitleScreen.STATE_SPLASH:
            self.game.frame.blit(self.bg, (0, 0))
        elif self.state == TitleScreen.STATE_SETTINGS:
            self.game.frame.fill((0, 128, 128))
            self.settings_ui.render(self.game.frame)
        elif self.state == TitleScreen.STATE_TANK_SELECT:
            self.game.frame.fill((0, 128, 128))
            self.tank_ui.render(self.game.frame)