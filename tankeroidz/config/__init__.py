from pygame.locals import *

defaults = {
    "settings": {
        'width': 480,
        'height': 320,
        'title': "Tankeroidz",
        'fps': 30,
        'powerup_chance': 20,
        'difficulty': 'HARD',
        'dev_mode': True,
        'show_console': False
    },
    "keybindings": {
        'pause': [K_p],
        'select': [K_RETURN],
        'up': [K_w, K_UP],
        'right': [K_d, K_RIGHT],
        'left': [K_a, K_LEFT],
        'down': [K_s, K_DOWN],
        'primary': [K_SPACE],
        'secondary': [K_LSHIFT]  
    }
}