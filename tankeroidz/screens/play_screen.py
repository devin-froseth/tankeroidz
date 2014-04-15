import pygame
import random
import screen
import console

from game_over_screen import GameOverScreen
from pygame.locals import *
from entities import *
from ui import *
from io_utils import *
from math_utils import *

class PlayScreen(screen.Screen):
    """Playing screen"""
    
    # States of the PlayScreen
    STATE_RUNNING = 0
    STATE_PAUSED  = 1
    
    def create(self, *args, **kwargs):
        # Containers for entities (game objects)
        self.enemies, self.bullets, self.powerups = [], [], []
        
        self.ticks, self.run_ticks = 0, 0
        self.score = 0
        
        self.difficulty = kwargs.get('difficulty', 'easy')
        self.load_config()

        self.create_tank(kwargs.get('tank', 'classic'))

        self.create_ui()
        self.create_pause_ui()
        
        self.ticks_until_enemy_spawn = self.game.settings['fps'] * 3
        self.set_state(PlayScreen.STATE_RUNNING)
        
    def load_config(self):
        try:
            cfg = ini_to_dict('config/play_config.ini')
            
            # Fixes difficulty configurations by copying default settings to
            # each difficulty's specific dict. This workaround removes the need
            # for if statements that check both difficulty specific settings and
            # default settings.
            for setting in cfg['default']:
                if setting not in cfg[self.difficulty]:
                    cfg[self.difficulty][setting] = cfg['default'][setting]
            
            self.config = cfg[self.difficulty]
                
        except IOError:
            print "Couldn't load play config!" #TODO
    
    def create_tank(self, model):
        """Create the tank object and load some of its attributes from this
        difficulty setting's config."""
        self.tank = Tank(model)
        self.tank.turn_radius = self.config['tank_turnradius']
        self.tank.move_speed = self.config['tank_speed']
        self.tank.wall_walking = self.config['wall_walking']

    def create_ui(self):
        """Create the HUD"""
        ui_path = 'resources/ui/play_ui.ini'
        w, h = self.game.settings['width'], self.game.settings['height']
    
        self.ui = load_ui(ui_path, (w, h))
        
        try:
            self.ui['score_label'].x = w-self.ui['score_label'].width-10
        except ValueError:
            console.log("Score label not found in `" + ui_path + "`.")
        
    def create_pause_ui(self):
        """Create the pause menu UI."""
        pause_ui_path = 'resources/ui/pause_ui.ini'
        w, h = self.game.settings['width'], self.game.settings['height']
        
        self.pause_ui = load_ui(pause_ui_path, (w, h))
        menu_scale = 0.8
        pad_scale = (1 - menu_scale) / 2.0
        menu_x, menu_y = w*pad_scale, h*pad_scale
        menu_width, menu_height = w*menu_scale, h*menu_scale
        pause_bg_bounds = menu_x, menu_y, menu_width, menu_height
        
        try:
            self.pause_ui['bg'].bounds = pause_bg_bounds
        except AttributeError, e:
            console.warn("Couldn't find `bg` in `" + pause_ui_path + "`.")
            
        try: # XXX
            for component in self.pause_ui:
                if component.name != 'bg':
                    self.pause_ui.center_component(component.name, 1, 0)
        except AttributeError as e:
            console.warn("Can't center at line 103.")
            
    def handle_input(self, event):
        hotkeys = self.game.keybindings
        
        if self.state == PlayScreen.STATE_PAUSED:
            if event.type == KEYDOWN:
                if event.key in hotkeys['pause']:
                    self.set_state(PlayScreen.STATE_RUNNING)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = self.pause_ui.get_component_at_pos(pygame.mouse.get_pos())
                    if c is not None:
                        if c.name == 'button_quit':
                            pygame.event.post(pygame.event.Event(QUIT))
                        elif c.name == 'button_resume':
                            self.set_state(PlayScreen.STATE_RUNNING)
                        elif c.name == 'button_restart':
                            self.game.set_screen(GameOverScreen(self.game))
                            
        if self.state == PlayScreen.STATE_RUNNING:
            if event.type == KEYDOWN:
                if event.key in hotkeys['pause']:
                    self.set_state(self.STATE_PAUSED)
                elif event.key in hotkeys['right']:
                    self.tank.dir = 1
                elif event.key in hotkeys['left']:
                    self.tank.dir = -1
                elif event.key in hotkeys['up']:
                    self.tank.speed = 1
                elif event.key in hotkeys['down']:
                    self.tank.speed = -1
                elif event.key in hotkeys['primary']:
                    self.tank.bullet_fire_now = True
                elif event.key in hotkeys['secondary']:
                    self.tank.using_boost = True
            elif event.type == KEYUP:
                if (event.key in hotkeys['right'] or
                    event.key in hotkeys['left']):
                    self.tank.dir = 0
                elif (event.key in hotkeys['up'] or
                      event.key in hotkeys['down']):
                    self.tank.speed = 0
                elif event.key in hotkeys['primary']:
                    self.tank.bullet_fire_now = False
                elif event.key in hotkeys['secondary']:
                    self.tank.using_boost = False

        self.pause_ui.handle_input(event)
        
    def update(self):
        if self.state == self.STATE_RUNNING:
            self.bullet_system()
            self.movement_system()
            self.collision_system()
            self.spawn_system()
            self.status_system()
            self.timed_event_system()
            self.ui.update()
            self.run_ticks += 1
        elif self.state == self.STATE_PAUSED:
            self.pause_ui.update()
        
        self.ticks += 1
    
    def status_system(self):
        """Manages resources (health/power) and buffs."""
        tank = self.tank
        rate = float(self.game.settings['fps'])
        
        # Kill everything with no health - this must come before any regen!
        if tank.health <= 0:
            self.game.set_screen(GameOverScreen(self.game, score=self.score))
            
        for enemy in self.enemies:
            if enemy.health <= 0:
                self.enemies.remove(enemy)
        for bullet in self.bullets:
            if bullet.health <= 0:
                self.bullets.remove(bullet)
        for powerup in self.powerups:
            if powerup.health <= 0:
                self.powerups.remove(powerup)
        
        # Decrement power if using speed boost
        if tank.using_boost and tank.speed != 0:
            tank.power -= tank.max_power * .02 # TODO hardcoded speed cost

        # Health regeneration and wrapping
        tank.health += tank.get('health_regen') / rate
        if tank.health > tank.max_health: tank.health = tank.max_health
          
        # Power regeneration and wrapping
        tank.power += tank.get('power_regen') / rate
        if tank.power > tank.max_power: tank.power = tank.max_power

        # Check all buff timers and remove expired buffs
        # {http://stackoverflow.com/questions/11941817/python-runtimeerror-dictionary-changed-size-during-iteration-how-to-avoid-th}
        for key in tank.mod_timers.keys(): 
            tank.mod_timers[key] -= 1.0 / self.game.settings['fps']
            if tank.mod_timers[key] <= 0: # The cooldown timer has expired
                del tank.mod_timers[key]
                del tank.modifiers[key]
                if key in tank.effects: del tank.effects[key]
    
    def bullet_system(self):
        """Create new bullets if the user requests and is not on cooldown."""
        tank = self.tank
        
        for bullet in self.bullets:
            bullet.age += 1
            
        # If the fire button isn't pressed or fire is on cooldown, exit system
        ticks_since_last = self.run_ticks - self.tank.bullet_last_shot_tick
        max_cd_ticks = self.game.settings['fps'] * self.tank.bullet_cooldown_max
        if not self.tank.bullet_fire_now or ticks_since_last <= max_cd_ticks:
            return
            
        self.spawn_one_bullet()

    def movement_system(self):
        """Handles the movement of all game objects."""
        map_width = self.game.settings['width']
        map_height = self.game.settings['height']
        
        tank = self.tank
        ms_mult = self.config['tank_boost_pct']/100.0 if tank.using_boost else 1
        
        move_step = tank.get('speed') * tank.get('move_speed')*ms_mult
        tank.rot -= tank.get('dir') * tank.get('turn_radius')
        
        # Move the tank
        dx = math.sin(math.radians(tank.rot)) * -move_step
        dy = math.cos(math.radians(tank.rot)) * -move_step
        
        new_x, new_y = tank.x + dx, tank.y + dy

        # Handle the tank trying to escape the confines of the map
        if tank.get('wall_walking'): # Move through walls (wrapping)
            if new_x < 0: new_x = map_width
            elif new_x > map_width: new_x = 0
            
            if new_y < 0: new_y = map_height
            elif new_y > map_height: new_y = 0
        else: # Or be blocked by walls (collision)
            if new_x < 0 or new_x > map_width:  new_x = tank.x
            if new_y < 0 or new_y > map_height: new_y = tank.y
        
        tank.x, tank.y = new_x, new_y
        
        # Update the tank's gun
        tank.gun_x = tank.x - math.sin(math.radians(tank.rot)) * tank.gun_length
        tank.gun_y = tank.y - math.cos(math.radians(tank.rot)) * tank.gun_length        
    
        # Bullet movement
        for bullet in self.bullets:
            bullet.x -= math.sin(math.radians(bullet.rot))*bullet.move_speed
            bullet.y -= math.cos(math.radians(bullet.rot))*bullet.move_speed
        
        # Enemy movement
        for enemy in self.enemies:
            enemy.x -= math.sin(math.radians(enemy.rot))*enemy.move_speed
            enemy.y -= math.cos(math.radians(enemy.rot))*enemy.move_speed
    
    def collision_system(self):
        map_width = self.game.settings['width']
        map_height = self.game.settings['height']
        
        for bullet in self.bullets:
            # Bullet-wall collision
            if (bullet.x < 0 or bullet.x > map_width or
                    bullet.y < 0 or bullet.y > map_height):
                self.bullets.remove(bullet)
                continue
            
            # Bullet-enemy
            for enemy in self.enemies:
                force_break = 0
                if circle_collision(bullet, enemy):
                    if random.randint(0, 100) <= self.config['powerup_chance']:
                        powerup = PowerupFactory.create_random()
                        powerup.x, powerup.y = enemy.x, enemy.y
                        self.powerups.append(powerup)

                    points = enemy.move_speed * 2
                    self.add_score(points)
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    force_break = 1
                    
                # NOTE: Workaround to prevent nonexistent bullets (bullets that
                # were already killed) from being tested against
                if force_break: break
                    
        for enemy in self.enemies:
            # Enemy-wall
            if not 0 < enemy.x < map_width or not 0 < enemy.y < map_height:
                self.enemies.remove(enemy)
                continue
                
            # Enemy-tank
            if circle_collision(enemy, self.tank):
                self.tank.health -= enemy.impact * self.tank.get('damage_modifier')
                self.enemies.remove(enemy)
                continue
                
            # Enemy-enemy
            for enemy2 in self.enemies:
                if circle_collision(enemy, enemy2) and enemy != enemy2:
                    self.enemies.remove(enemy)
                    self.enemies.remove(enemy2)
                    break # Stop iterating because `enemy` has been deleted
            
        for powerup in self.powerups:
            # Powerup-tank
            if circle_collision(powerup, self.tank):
                self.tank.apply_powerup(powerup)
                powerup.health = 0
                console.log("Picked up powerup: " + powerup.name)
            
    def spawn_system(self):
        self.ticks_until_enemy_spawn -= 1
        if self.ticks_until_enemy_spawn >= 0:
            return
            
        enemy = Enemy()
        max_speed = 8
        min_r, max_r = 4, 11
        
        # Spawn either on y- or x-border, somewhat randomly
        if random.choice(['x', 'y']) == 'x':
            enemy.x = random.choice([0, self.game.settings['width']])
            enemy.y = random.randint(0, self.game.settings['height'])
        else:
            enemy.x = random.randint(0, self.game.settings['width'])
            enemy.y = random.choice([0, self.game.settings['height']])
        
        enemy_speed_mod = self.config['enemy_speed_pct'] / 100.0
        
        enemy.radius = random.randint(min_r, max_r)
        enemy.move_speed = (max_speed + min_r - enemy.radius) * enemy_speed_mod
        enemy.impact = enemy.radius #TODO: difficulty modifier
        
        dx = enemy.x - self.tank.x
        dy = enemy.y - self.tank.y
        enemy.rot = math.atan2(dx, dy) * 180/math.pi
        
        self.enemies.append(enemy)
        self.ticks_until_enemy_spawn = .75 * self.game.settings['fps']
        #TODO
    
    def timed_event_system(self):
        fps = float(self.game.settings['fps'])
        secs_per_point_increment = 3
        points_per_increment = 10
        
        if (self.ticks / fps) % secs_per_point_increment == 0:
            self.add_score(points_per_increment)
            
    def render(self):
        self.render_running()
        
        if self.state == self.STATE_PAUSED:
            self.render_paused()
            
    def render_running(self):
        render_vecs = 0
        
        # Render the background
        self.game.frame.fill((0, 128, 128))
        
        # Render images as long as image rendering isn't disabled
        if self.game.settings['render_images']:
            render_vecs = self.render_running_rasters()
        
        # Render vectors if they're enabled or there was an issue rendering imgs
        if self.game.settings['render_vectors'] or render_vecs:
            self.render_running_vectors()
            
        self.render_HUD()
    
    def render_running_rasters(self):
        # Render powerups
        for powerup in self.powerups:
            p_sprite = get_image("powerup_" + powerup.name)
            p_bounds = p_sprite.get_rect()
            p_bounds.center = powerup.x, powerup.y
            self.game.frame.blit(p_sprite, p_bounds)

        # Render Tank
        tank = self.tank
        
        sprite_offset_x = math.sin(math.radians(tank.rot)) * 6
        sprite_offset_y = math.cos(math.radians(tank.rot)) * 6
        # TODO: find out why `6` is the magic number for offset.... DF
        
        tank_sprite = pygame.transform.rotate(tank.sprite, tank.rot)
        tank_bounds = tank_sprite.get_rect()
        tank_bounds.center = (tank.x-sprite_offset_x, tank.y-sprite_offset_y)
        for effect in tank.effects: # Apply visual effects from powerups
            tank_sprite.fill(tank.effects[effect], special_flags=BLEND_RGB_MULT)
        self.game.frame.blit(tank_sprite, tank_bounds)
        
        # Render bullets
        for bullet in self.bullets:
            bullet_bounds = bullet.sprite.get_rect()
            bullet_bounds.center = bullet.x, bullet.y
            
            self.game.frame.blit(bullet.sprite, bullet_bounds)

        # Render enemies
        for enemy in self.enemies:
            enemy_sprite = pygame.transform.scale(enemy.sprite,
                (enemy.width, enemy.height))
            enemy_sprite = pygame.transform.rotate(enemy_sprite, enemy.rot)
            
            enemy_bounds = enemy_sprite.get_rect() 
            enemy_bounds.center = enemy.x, enemy.y
            
            self.game.frame.blit(enemy_sprite, enemy_bounds)
    
    def render_running_vectors(self):
        # Powerups
        for powerup in self.powerups:
            pygame.draw.circle(self.game.frame, (0, 255, 0),
                (int(powerup.x), int(powerup.y)), int(powerup.radius))
        
        # Render Tank
        tank = self.tank
        
        # custom impl of BLEND_RGB_MULT
        # http://stackoverflow.com/questions/601776/what-do-the-blend-modes-in-pygame-mean
        red, green, blue = tank.color
        for effect in tank.effects.values(): # Apply visual effects from powerups
            red = int(red * effect[0] / 256)
            green = int(green * effect[1] / 256)
            blue = int(blue * effect[2] / 256)
        tank_col = red, green, blue
        
        # Render tank hitbox
        pygame.draw.circle(self.game.frame, tank_col,
                (int(tank.x), int(tank.y)), int(tank.radius), 0)
        
        # Render tank gun
        pygame.draw.line(self.game.frame, tank_col, (tank.x, tank.y),
                (tank.gun_x, tank.gun_y), tank.gun_stroke)
        
        # Render bullets
        for bullet in self.bullets:
            pygame.draw.circle(self.game.frame, (255, 0, 0),
                    (int(bullet.x), int(bullet.y)), int(bullet.radius))

        # Render enemies
        for enemy in self.enemies:
            pygame.draw.circle(self.game.frame, enemy.color,
                    (int(enemy.x), int(enemy.y)), int(enemy.radius), 0)
       
    def render_paused(self):
        #self.game.frame.fill((0,0,0))
        self.pause_ui.render(self.game.frame)
        
    def render_HUD(self):
        self.ui.get('health_bar').foreground_fill = self.tank.health / self.tank.max_health
        self.ui.get('power_bar').foreground_fill = self.tank.power / self.tank.max_power
        
        score_label = self.ui.get('score_label')
        
        score_label.text = "Score: " + str(int(self.score))
        score_label.x = self.game.settings['width'] - score_label.width - 10
        
        self.ui.render(self.game.frame)

    def add_score(self, n):
        self.score += n
        
    def set_state(self, state):
        self.clear_tank_events()
        self.state = state
        
    def spawn_one_bullet(self):
        bullet = Bullet()
        bullet.x, bullet.y = self.tank.gun_x, self.tank.gun_y
        bullet.rot = self.tank.rot
        self.bullets.append(bullet)
        self.tank.bullet_last_shot_tick = self.run_ticks
        
    def clear_tank_events(self):
        self.tank.speed = 0
        self.tank.dir = 0
        self.tank.using_boost = False
        self.tank.bullet_fire_now = False