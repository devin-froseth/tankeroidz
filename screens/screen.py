class Screen(object):
    def __init__(self, game, *args, **kwargs):
        self.state = 0
        self.game = game
        self.create(*args, **kwargs)
        
    def create(self, *args, **kwargs):
        """Called when a screen is initialized."""
        return
    
    def handle_input(self, event):
        """The screen deals with the specified event."""
        return
        
    def update(self):
        """Updates the screen every tick."""
        return
        
    def render(self):
        """Render the screen every tick."""
        return
        
    def enter(self):
        """Called when the screen is loaded."""
        return
        
    def exit(self):
        """Called when the screen is exited."""
        return
        
    def set_state(self, state):           
        self.state = state
