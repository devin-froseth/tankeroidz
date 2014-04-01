import math

def circle_collision(a, b):
    """Checks if two circles collide.
    
    Args:
        a (circle): The first circle for which to check for collision.
        b (circle): The second circle for which to check for collision.
    Returns:
        True if the two circles collide.
    """
    return math.hypot(b.x-a.x, b.y-a.y) <= b.radius+a.radius

def point_in_rect(point, rect):
    """Checks if the given point is within the bounds of the given rectangle.
    
    Args:
        point: A tuple or point object containing x and y values.
        rect: A tuple or rect object containing x, y, width, and height values.
    Returns:
        True if the point is in the rectangle.
    """
    if hasattr(point, 'x') and hasattr(point, 'y'):
        px, py = point.x, point.y
    elif isinstance(point, (list, tuple)):
        px, py = point[:2]
    
    if (hasattr(rect, 'x') and hasattr(rect, 'y') and
        hasattr(rect, 'width') and hasattr(rect, 'height')):
        rx, ry, rw, rh = rect.x, rect.y, rect.width, rect.height
    elif isinstance(rect, (list, tuple)):
        rx, ry, rw, rh = point[:4]
        
    return (rw <= px <= rx+rw) and (ry <= py <= ry+rh)