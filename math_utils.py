import math

def circle_collision(a, b):
    """Checks if two circles collide.
    
    Args:
        a (circle): The first circle for which to check for collision.
        b (circle): The second circle for which to check for collision.
    Returns:
        bool: True if the two circles collide.
    """
    return math.hypot(b.x-a.x, b.y-a.y) <= b.radius+a.radius

def point_in_rect(*args):
    point = args[0]
    rect = args[1]
    
    try:
        px, py = point.x, point.y
    except:
        px, py = point[0], point[1]
    
    return (rect.x <= px <= rect.x+rect.width and
            rect.y <= py <= rect.y+rect.height)