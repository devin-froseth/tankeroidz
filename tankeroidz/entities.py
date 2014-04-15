import math
import random
import pygame
import operator
import io_utils

class Entity(object):
    def __init__(self):
        self.create()

    def create(self):
        pass

class GameObject(Entity): # TODO convert ticks -> sec
    """A unit in the game world.

    Attributes:
        x: Unit's x-coordinate in pixels
        y: Unit's y-coordinate in pixels
        radius: Unit's radius in pixels. If the unit's width or height is set,
            its radius is resolved to half of the average of the two dimensions.
        width: Unit's width in pixels.
        height: Unit's height in pixels.
        rot: Unit's angle of rotation in degrees. Positive values rotate the
            unit counterclockwise. 0 degrees is north or "up".
        turn_radius: The rate at which the unit can turn in one game tick in
            degrees.
        speed: 1-dimension direction of movement. This should be set to 0 (for
            no movement), 1 (for forward movement), or -1 (for reverse
            movement). Use GameObject.move_speed to set the unit's actual
            movement speed.
        move_speed: Movement speed in pixels per game tick.
        color: If a sprite is not provided for the unit, the unit will be
            rendered using the given color.
        sprite: The unit's sprite (image) as a PyGame Surface object.
        max_health: The unit's total health points. For entities such as bullets
            and enemies, use `1` for max_health for consistency.
        health: Current remaining health points. The game's logic system should
            handle unit's with health <= 0 and prevent health > max_health.
        health_regen: Health points per game tick to regenerate.
        max_power: The unit's total power points. Power is used for actions such
            as speed boosts and bullet firing.
        power: Current remaining power points.
        power_regen: Power points per game tick to regenerate.
        damage_modifier: REMOVE  THIS!
        impact: Damage done in health points when this unit collides with
            another unit.
        age: The number of game ticks that this unit has been active.

        position: a tuple with the unit's x- and y-coordinates
        draw_pos: a read-only tuple with the unit's coords for drawing
    """
    def __init__(self):
        self.x, self.y = 0, 0
        self._radius = 1
        self._width, self._height = 1, 1

        self.rot = 0
        self.turn_radius = 180 * math.pi/180

        self.speed = 0
        self.move_speed = 1 # px / sec

        self.color = (0, 0, 0)
        self.sprite = None

        self.auras = []

        self.max_health = 1
        self.health = 1
        self.health_regen = 0

        self.max_power = 0
        self.power = 0
        self.power_regen = 0

        self.damage_modifier = 1.0

        # Damage done on collision
        self.impact = 0

        self.age = 0 # ticks

        self.modifiers = {}
        self.mod_timers = {}

        self.create()

    def apply_damage(self, health):
        self.health -= health * self.damage_modifier

    def on_impact(self, unit):
        return

    def get(self, name, default=''):
        value = getattr(self, name)

        if (value is None): #TODO
            print "No!!!! property"
            return

        if (name in self.modifiers):
            mod = self.modifiers[name]

            value = mod.oper(value, mod.value)

        return value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._width, self._height = value*2, value*2
        self._radius = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._radius = value/2 if (value < self._height) else self._radius
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._radius = value/2 if (value < self._width) else self._radius
        self._height = value

    @property
    def bounds(self, value):
        return (self.x, self.y, self.width, self.height)
    
    @property
    def position(self):
        return self.x, self.y
    @position.setter
    def position(self, *args):
        self.x = args[0]
        self.y = args[1]
        
    @property
    def draw_pos(self):
        return int(self.x), int(self.y)
        
class Tank(GameObject):
    def __init__(self, model):
        GameObject.__init__(self)
        self.load_sprite(model)
        
    def load_sprite(self, model):
        self.sprite = io_utils.get_image('tank_' + model).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (27, 50))
        self.sprite = pygame.transform.flip(self.sprite, 0, 1)
        
    def create(self):
        self.x, self.y = 150, 150
        self.radius = 16

        self.move_speed = 4
        
        self.dir = 0
        self.turn_radius = 5
        
        self.sprite = None
        
        self.color = 150, 150, 150
        
        self.gun_length = self.height/2 + 6
        self.gun_stroke = 3
        self.gun_x, self.gun_y = 0, 0
        
        self.bullet_fire_now = False
        self.bullet_cooldown_max = .333
        self.bullet_cooldown_left = 0
        self.bullet_last_shot_tick = -self.bullet_cooldown_max
        
        self.max_health = 100
        self.health = self.max_health
        self.health_regen = .2 
        
        self.damage_modifier = 1.0
        self.wall_walking = 0
        
        self.max_power = 100
        self.power = self.max_power
        self.power_regen = 10

        self.using_boost = False
        self.powerups = []
        
        self.effects = {} # Visual effects, assume BLEND_RGB_MULT
    
    def apply_powerup(self, powerup):
        key = powerup.modifies
        value = powerup.value
        
        # Add the modifier and its timer        
        self.modifiers[key] = Modifier(value)
        if powerup.duration > 0:
            self.mod_timers[key] = powerup.duration
        if powerup.effect is not None:
            self.effects[key] = powerup.effect
    
class Enemy(GameObject):
    def create(self):
        self.speed = 1
        self.color = (0, 0, 0)
        self.impact = 10
        
        self.sprite = io_utils.get_image('enemy').copy().convert_alpha()
        
    def on_impact(self, unit=None):
        self.health = 0
        if unit is not None:
            unit.apply_damage(self.impact)

class Bullet(GameObject):
    def create(self):
        self.radius = 6
        self.impact = 10
        self.speed = 1
        self.move_speed = 10
        
        self.sprite = io_utils.get_image('bullet_default').copy().convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        
        self.color = (255, 0, 0)
        
    def on_impact(self, unit=None):
        self.health = 0
        if unit is not None:
            unit.apply_damage(self.impact)
        
class Modifier(object):
    operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.div,
        "_": lambda a, b: b # replacement, i.e. faux assignment
    }
    _oper = None
    value = 0
    
    def __init__(self, *args): #TODO
        if len(args) == 1:
            val = args[0]
            
            try:
                if val[0] in self.operators: # first char is an operator
                    self.oper = val[0]
                    self.value = float(val[1:])
                else: # assume replacement operator
                    self.oper = "_"
                    self.value = float(val)
            except:
                print "SOMETHING WENT WRONG. " + str(val)

    @property
    def oper(self):
        return self._oper
    
    @oper.setter
    def oper(self, val):
        if type(val) is str:
            self._oper = self.operators[val]
        elif ifbuiltin(val):
            self._oper = val
        else:
            raise ValueError
            
    def __str__(self):
        return "Modifier(Operator: " + str(self._oper) + ", Value: " + str(self.value) + ")"
    
class Powerup(GameObject):
    def create(self):
        self.radius = 4
        self.speed = 0
        self.max_age = 0
        self.modifies = None
        self.value = None
        self._effect = None
    
    @property
    def effect(self):
        return self._effect
    @effect.setter
    def effect(self, effect):
        if type(effect) is str:
            effect = [int(n) for n in effect.split(',')]
        self._effect = effect

powerups = [
    {
        "name": "speedboost",
        "duration": 300,
        "buff": ['move_speed', '*1.5'],
        "effect": (200, 200, 128)
    },
    {
        "name": "healthpack",
        "duration": 90,
        "buff": ['health_regen', '+10'],
        "effect": (255, 128, 128)
    },
    {
        "name": "energypack",
        "duration": 90,
        "buff": ['power_regen', '+30'],
        "effect": (128, 128, 255)
    },
    {
        "name": "absorb",
        "duration": 90,
        "buff": ['damage_modifier', '*-1'],
        "effect": (50, 200, 50)
    },
    {
        "name": "wallwalking",
        "duration": 300,
        "buff": ['wall_walking', '1'],
        "effect": (255, 255, 255)
    }
]

powerups = {
    "speedboost": {
        "duration": 300,
        "modifies": "move_speed",
        "value": "*1.5",
        "effect": '200,200,128'
    },
    "healthpack": {
        "duration": 90,
        "modifies": "health_regen",
        "value": "+10",
        "effect": (255, 128, 128)
    }
}

powerups = io_utils.ini_to_dict('resources/powerups.ini')
    
class PowerupFactory(object):
    
    @staticmethod
    def create_random():
        powerup = Powerup()
        powerup.name = random.choice(powerups.keys())
        aura = powerups[powerup.name]
        
        for key in aura:
            setattr(powerup, key, aura[key])

        return powerup