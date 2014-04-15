import pygame
import io_utils
import math_utils

from pygame.locals import *

fonts = {
    'console': ["resources/fonts/UbuntuMono-Bold.ttf", 20],
    'hud': ["resources/fonts/FredokaOne.ttf", 18],
    'default': ["resources/fonts/FredokaOne.ttf", 16]
}

#TODO CHECK IF SETTER IS ..

class UI(object):
    """The UI manager. You can add and get UI objects by using the UI class
    as an interface.
    
    Attributes:
        components: List of all UI components belonging to this UI.
    """
    def __init__(self, *args, **kwargs):
        self.components = []
        self.listening = False
        
        self.width, self.height = -1, -1
        
        for key, value in kwargs.iteritems():
            if key == "size":
                self.width, self.height = value
            else:
                raise ValueError("UI(): Unrecognized kwarg: `" + key + "`.")
                
        if 'size' not in kwargs:
            raise ValueError("UI(): Missing `size` tuple kwarg.")
            
            
        
    def handle_input(self, event):
        """Handles input from the mouse and keyboard."""
        if self["CURSOR"] is None:
            return
            
        cursor = self["CURSOR"]
            
        if event.type == KEYDOWN:
            if event.key in [K_DOWN, K_s]:
                cursor.dy = 1
            elif event.key in [K_UP, K_w]:
                cursor.dy = -1
            elif event.key in [K_LEFT, K_a]:
                cursor.dx = -1
            elif event.key in [K_RIGHT, K_d]:
                cursor.dx = 1
                
        if event.type == KEYUP:
            if event.key in [K_DOWN, K_s, K_UP, K_w]:
                cursor.dy = 0
            elif event.key in [K_LEFT, K_a, K_RIGHT, K_d]:
                cursor.dx = 0
            elif event.key in [K_SPACE]:
                cursor.pressed = True
            
    def update(self):
        if self["CURSOR"] is None:
            return
            
        # Move the cursor
        self["CURSOR"].x += self["CURSOR"].dx * self["CURSOR"].sensitivity
        self["CURSOR"].y += self["CURSOR"].dy * self["CURSOR"].sensitivity
        
        # Click the cursor
        self.touch_cursor()
        
        #self.move_cursor()

    def touch_cursor(self):
        if self["CURSOR"] is None or not self["CURSOR"].pressed:
            return
            
        cursor = self["CURSOR"]
        
        # Use a reverse loop here so that UI components with higher indices
        # are favored - those are the components that are rendered last and
        # therefore the "top layers"
        for i in range(len(self.components)-1, -1, -1):
            component = self.components[i]
            if io_utils.point_in_rect(cursor, component) and component != cursor:
                print "CLICKED", component.name, component.on_click
                if component.on_click is not None:
                    component.on_click()
                break
        
        cursor.pressed = False
        
    def get_component_at_pos(self, *args, **kwargs):
        """Returns the UI component at the specified position.
        
        Args:
            point (tuple): A 2-length tuple containing the x-coordinate at the 0
                index and the y-value at the 1 index.
        Kwargs:
            x (int): The x-coordinate of the cursor.
            y (int): The y-coordinate of the cursor.
        Raises:
            ValueError
        """
        if 'x' in kwargs and 'y' in kwargs:
            x, y = kwargs.x, kwargs.y
        elif len(args) > 0 and len(args[0]) > 1:
            x, y = args[0]
        else:
            msg = ("ui.get_component_at_pos: Invalid arguments - your arguments"
                " must be either a tuple or kwargs containing x- and y-values.")
            raise ValueError(msg)

        # Use a reverse loop here so that UI components with higher indices
        # are favored - those are the components that are rendered last and
        # therefore the "top layers"
        for i in range(len(self.components)-1, -1, -1):
            component = self.components[i]
            if math_utils.point_in_rect((x, y), component): #TODO
                return component
                
        return None
        
    def center_component(self, component, adjust_x=True, adjust_y=True):
        """Centers the component in the UI."""
        if type(component) is str:
            component = self[component]
            
        if adjust_x: component.x = (self.width - component.width) / 2
        if adjust_y: component.y = (self.height - component.height) / 2
                
    def render(self, surface):
        for components in self.components:
            components.render(surface)
    
    def add(self, name, component):
        self[name] = component
        return component
        
    def get(self, name):
        return self[name]
        
    def remove(self, key):
        self.components.remove(key)
    
    def index(self, key):
        for i in range(self.components):
            if self.components[i].name == key:
                return i
        raise ValueError(key + " not found in " + self + ".")
    
    def contains(self, key):
        return key in self
    
    def __setitem__(self, key, value):
        if not isinstance(value, UIObject):
            raise TypeError("Can't add non UIObject to UI.")
            
        if self.contains(key):
            self.remove(key)
            
        value.name = key
        self.components.append(value)
        
        return value
    
    def __getitem__(self, key):
        for component in self.components:
            if component.name == key:
                return component
    
    def __contains__(self, key):
        for i in range(len(self.components)):
            if self.components[i].name == key:
                return True
        return False
        
    def __iter__(self):
        for c in self.components:
            yield c

    def __delitem__(self, key):
        if type(key) is not int:
           key = self.index(key)
       
        del self.components[key]

class UIObject(object):
    """A renderable UI object that belongs to the UI manager.
    
    Attributes:
        name: The unique name of this component. If a component with the same
            name is added to the same parent, the older one will be replaced.
        parent: The component's parent component.
        x:
        y:
        width:
        height:
        texture:
        color:
        alpha:
        surface:
    """
    
    # These won't request redrawing when changed {see UIObject.__setattr__}
    _quiet_properties = ['surface', 'request_redraw']
    
    def __init__(self, **kwargs):
        self.name = 'untitled'
        self.parent = None
        self.children = []
        
        self.x = 0
        self.y = 0

        self.width = 1
        self.height = 1
        
        self.selectable = None
        
        self._texture = None
        self._color = 255, 0, 255
        self.alpha = 255
        
        self.surface = None
        self.on_click = None
        
        self._update_surface()
        
        # This is pretty unrestrictive.. so use with care
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    
    def __setattr__(self, key, value):
        """Notifies `self.request_redraw` when an object attribute is set.
        
        The UI Component polls for redraw requests and updates the surface when
        a request is made.
        
        NOTE: This works - do not modify it (or do so with caution). Messing
        with __setattr__ can be "dangerous".
        
        Replacing __setattr__ removes the need for either a) excessive iteration
        or b) an excessive amount of properties (virtual attributes) for UI
        components. UIObject should be used as the base class for all other UI
        components, allowing __setattr__ to be inherited.
        
        See:
            http://stackoverflow.com/questions/7042152/how-to-i-properly-override-setattr-and-getattribute-on-new-style-classes
            http://stackoverflow.com/questions/17735520/determine-if-given-class-attribute-is-a-property-or-not-python-object
        """
        
        # If it's not a class property
        if (key not in self._quiet_properties and hasattr(self, key) and
                not hasattr(type(self), key)):
            if getattr(self, key) != value: # no need to redraw if nothing changes
                object.__setattr__(self, 'request_redraw', True) 
         
        object.__setattr__(self, key, value)
        
    def render(self, surface):
        if self.request_redraw:
            self._update_surface()
            
        # Draw all children to self
        for child in self.children:
            child.render(self.surface)
            
        # Then draw self..
        surface.blit(self.surface, (self.x, self.y))
        
    def _update_surface(self):
        if self.width < 1 or self.height < 1:
            dims = 1, 1
        else:
            dims = self.width, self.height
            
        self.surface = pygame.Surface(dims)
        
        if self.texture is not None:
            tex = self.texture.copy()
            tex = pygame.transform.scale(tex, dims)
            #self.surface.blit(tex, (0, 0))
            self.surface = tex
        elif self.color is not None:
            self.surface = pygame.Surface(dims)
            self.surface.fill(self.color)
            
        self.surface.set_alpha(self.alpha)
        self.request_redraw = False
        
    def on_key_press(self, key=-1):
        pass
    
    @property
    def bounds(self):
        return (self.x, self.y, self.width, self.height)
    @bounds.setter
    def bounds(self, bounds_):
        if (self.width < 0): self.width = 1
        if (self.height < 0): self.height = 1
        
        self.x, self.y = int(bounds_[0]), int(bounds_[1])
        self.width, self.height = int(bounds_[2]), int(bounds_[3])
    
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, color):
        if len(color) > 3:
            self.alpha = color[3]
        self._color = color[:3]
        self._update_surface()
        
    @property
    def texture(self):
        return self._texture
    @texture.setter
    def texture(self, texture):
        if type(texture) is str:
            self._texture = pygame.image.load(texture).convert_alpha()
        else:
            self._texture = texture

class Bar(UIObject):

    _quiet_properties = ['_foreground_fill', 'foreground_fill']

    """A bar has a border, foreground, and background (three layers)"""
    def __init__(self, **kwargs):
        self._foreground_fill = 1
        
        self.border = UIObject()
        self.background = UIObject()
        self.foreground = UIObject()
        
        self.bordercolor = 0, 0, 0
        
        UIObject.__init__(self, **kwargs)
        
        self.children = [self.border, self.background, self.foreground]

        self._update_surface()
    
    @property
    def foreground_fill(self):
        return self._foreground_fill
    @foreground_fill.setter
    def foreground_fill(self, fill):
        self.foreground.width = int(self.background.width * fill)
        self._foreground_fill = fill

    @property
    def bordercolor(self):
        return self.border.color
    @bordercolor.setter
    def bordercolor(self, color):
        self.border.color = color
    
    @property
    def bgcolor(self):
        return self.background.color
    @bgcolor.setter
    def bgcolor(self, color):
        self.background.color = color
    
    @property
    def fgcolor(self):
        return self.foreground.color
    @fgcolor.setter
    def fgcolor(self, color):
        self.foreground.color = color
    
    @property
    def fgtexture(self):
        return self.foreground.texture
    @fgtexture.setter
    def fgtexture(self, texture):
        self.foreground.texture = texture
    
    @property
    def bounds(self):
        return (self.x, self.y, self.width, self.height)
    @bounds.setter
    def bounds(self, bounds):
        self.x = bounds[0]
        self.y = bounds[1]
        self.width = bounds[2]
        self.height = bounds[3]
        
        self.border.bounds = 0, 0, self.width, self.height
        self.foreground.bounds = 1, 1, self.width-2, self.height-2
        self.background.bounds = 1, 1, self.width-2, self.height-2
        
        self.request_redraw = True
        
class Label(UIObject):

    def __init__(self, **kwargs):
        self.text = "[label]"
        self.font = "default"
        self.font_size = 16
        
        UIObject.__init__(self, **kwargs)
        self._update_surface()
        
    def _update_surface(self):
        f = pygame.font.Font(fonts[self.font][0], fonts[self.font][1])
        self.surface = f.render(str(self.text), 1, self.color)
        self.request_redraw = False

    @property
    def width(self):
        if self.surface is not None:
            return self.surface.get_bounding_rect().width
    @width.setter
    def width(self, width):
        return
        
    @property
    def height(self):
        if self.surface is not None:
            return self.surface.get_bounding_rect().height
    @height.setter
    def height(self, height):
        return
        
class Button(UIObject):
    def __init__(self, **kwargs):
        UIObject.__init__(self, **kwargs)
        self.selectable = True
        
class Cursor(UIObject):
    def __init__(self, **kwargs):
        UIObject.__init__(self, **kwargs)
        self.width = 20
        self.height = 20
        self.texture = pygame.image.load("resources/cursor.png").convert_alpha()
        self.x, self.y = 50, 50
        self.dx, self.dy = 0, 0
        self.sensitivity = 5
        self.pressed = True
        
def load_ui(ini_file, size):
    """Loads a UI from a UI file.
    
    This `.ui` file extension implementation is custom to this project and
    is similar to INI files. The specified file is converted using an INI to
    dict method and the resulting dict is iterated to dynamically create and
    populate a UI.
    
    Args:
        ini_file: A file object or path to an INI file containing the UI scheme.
    Returns:
        int: An error code (0 for no error, 1 if there's an error)
    Raises:
        TODO
    """
    ui_dict = io_utils.ini_to_dict(ini_file)
    ui = UI(size=size)
    
    for name, attrs in ui_dict.iteritems():
        if type(attrs) is dict:
            ctype = UIObject() # if type isn't defined, we resort to this
            preferred_type = 'uiobject'
            
            if 'type' in attrs:
                preferred_type = attrs['type'].lower()
                del attrs['type'] # we got what we want, don't want to inject this later
                
            # create whatever kind of component
            if preferred_type == 'button':  ctype = Button
            elif preferred_type == 'bar':   ctype = Bar
            elif preferred_type == 'label': ctype = Label
            else:                           ctype = UIObject
            
            # Prepare the dict for use as kwargs
            for k, v in attrs.iteritems():
                if type(v) is str:
                    if v.startswith('(') and v.endswith(')'): # cheating.....
                        attrs[k] = tuple([int(s.strip()) for s in v[1:-1].split(',')])
                if k.endswith('texture'): # load some texture.. needed for Bars
                    attrs[k] = io_utils.get_image(v)
            # Check if there's a texture that matches this component's name
            if name in io_utils.image_cache:
                attrs['texture'] = io_utils.get_image(name)
                
            ui[name] = ctype(**attrs)
            
    return ui
    
def calc_center_offset(child, parent, adjust_x=True, adjust_y=True):
    """Calculate the desired top-left (anchor) coordinate of the "child"
    according to its dimensions and the "parent" object's dimensions. 
    
    Assumes child is a UIObject or indexable and parent is indexable.
    """
    if isinstance(child, UIObject):
        child_width, child_height = child.width, child.height
    else:
        child_width, child.height = child[0], child[1]
    
    parent_width, parent_height = parent[0], parent[1]
    
    x = ((parent_width-child_width) / 2) if adjust_x else 0
    y = ((parent_height-child_height) / 2) if adjust_y else 0
    return x, y