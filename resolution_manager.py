"""
Resolution manager for handling different screen resolutions.

Scales coordinates from the base 1920x1080 resolution to any target resolution.
"""
import logging

logger = logging.getLogger('mtgalog')


class ResolutionManager:
    """Manages coordinate scaling for different resolutions."""
    
    # Base resolution that all coordinates are defined for
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    
    def __init__(self, target_width, target_height):
        """Initialize resolution manager.
        
        Args:
            target_width: Target screen width
            target_height: Target screen height
        """
        self.target_width = target_width
        self.target_height = target_height
        self.scale_x = target_width / self.BASE_WIDTH
        self.scale_y = target_height / self.BASE_HEIGHT
        
        logger.info(f"Resolution scaling: {self.BASE_WIDTH}x{self.BASE_HEIGHT} -> "
                   f"{target_width}x{target_height} "
                   f"(scale: {self.scale_x:.3f}x, {self.scale_y:.3f}y)")
    
    def scale_point(self, x, y):
        """Scale a single point coordinate.
        
        Args:
            x: X coordinate at base resolution
            y: Y coordinate at base resolution
            
        Returns:
            tuple: (scaled_x, scaled_y)
        """
        return (int(x * self.scale_x), int(y * self.scale_y))
    
    def scale_bbox(self, x1, y1, x2, y2):
        """Scale a bounding box.
        
        Args:
            x1, y1: Top-left corner at base resolution
            x2, y2: Bottom-right corner at base resolution
            
        Returns:
            tuple: (scaled_x1, scaled_y1, scaled_x2, scaled_y2)
        """
        return (int(x1 * self.scale_x), int(y1 * self.scale_y),
                int(x2 * self.scale_x), int(y2 * self.scale_y))
    
    def scale_coordinate_dict(self, coord_dict):
        """Scale an entire dictionary of coordinates.
        
        Args:
            coord_dict: Dictionary mapping keys to coordinate tuples
            
        Returns:
            dict: New dictionary with scaled coordinates
        """
        scaled_dict = {}
        for key, value in coord_dict.items():
            if isinstance(value, tuple):
                if len(value) == 2:
                    # Point coordinate (x, y)
                    scaled_dict[key] = self.scale_point(value[0], value[1])
                elif len(value) == 4:
                    # Bounding box (x1, y1, x2, y2)
                    scaled_dict[key] = self.scale_bbox(value[0], value[1], value[2], value[3])
                else:
                    # Unknown format, keep original
                    scaled_dict[key] = value
            else:
                scaled_dict[key] = value
        
        return scaled_dict
    
    def scale_cards_in_hand(self, cards_tuple):
        """Scale the cards_in_hand tuple of coordinates.
        
        Args:
            cards_tuple: Tuple of (x, y) coordinates
            
        Returns:
            tuple: Tuple of scaled coordinates
        """
        return tuple(self.scale_point(x, y) for x, y in cards_tuple)
    
    @classmethod
    def from_window_coordinates(cls, window_coords):
        """Create ResolutionManager from window coordinates.
        
        Args:
            window_coords: Tuple of (x1, y1, x2, y2) window coordinates
            
        Returns:
            ResolutionManager: Initialized resolution manager
        """
        width = window_coords[2] - window_coords[0]
        height = window_coords[3] - window_coords[1]
        return cls(width, height)
    
    @classmethod
    def get_supported_resolutions(cls):
        """Get list of commonly supported resolutions.
        
        Returns:
            list: List of (width, height, name) tuples
        """
        return [
            (1920, 1080, "Full HD (1920x1080)"),
            (1680, 1050, "WSXGA+ (1680x1050)"),
            (1600, 900, "HD+ (1600x900)"),
            (1440, 900, "WXGA+ (1440x900)"),
            (1366, 768, "HD (1366x768)"),
            (1280, 1024, "SXGA (1280x1024)"),
            (1280, 800, "WXGA (1280x800)"),
            (1280, 720, "HD (1280x720)"),
        ]


def create_scaled_coordinates(resolution_manager, base_text_loc_dict, base_cord_class):
    """Create scaled versions of coordinate dictionaries and classes.
    
    Args:
        resolution_manager: ResolutionManager instance
        base_text_loc_dict: Base text location dictionary
        base_cord_class: Base Cord class
        
    Returns:
        tuple: (scaled_text_loc_dict, scaled_cord_dict)
    """
    # Scale text location dictionary
    scaled_text_loc = resolution_manager.scale_coordinate_dict(base_text_loc_dict)
    
    # Scale Cord class attributes
    scaled_cord = {}
    for attr_name in dir(base_cord_class):
        if not attr_name.startswith('_'):
            attr_value = getattr(base_cord_class, attr_name)
            if isinstance(attr_value, tuple):
                if attr_name == 'cards_in_hand':
                    # Special handling for cards_in_hand
                    scaled_cord[attr_name] = resolution_manager.scale_cards_in_hand(attr_value)
                elif len(attr_value) == 2:
                    # Point coordinate
                    scaled_cord[attr_name] = resolution_manager.scale_point(attr_value[0], attr_value[1])
                else:
                    scaled_cord[attr_name] = attr_value
    
    return scaled_text_loc, scaled_cord


# Example usage
if __name__ == "__main__":
    # Test different resolutions
    resolutions = ResolutionManager.get_supported_resolutions()
    
    print("Supported Resolutions:")
    for width, height, name in resolutions:
        print(f"  {name}")
        rm = ResolutionManager(width, height)
        
        # Test scaling a point
        original = (1665, 1000)  # Play button at 1920x1080
        scaled = rm.scale_point(*original)
        print(f"    Play button: {original} -> {scaled}")
    
    # Test scaling a bounding box
    print("\nBounding Box Scaling (1920x1080 -> 1280x720):")
    rm = ResolutionManager(1280, 720)
    bbox = (1650, 980, 1830, 1020)
    scaled_bbox = rm.scale_bbox(*bbox)
    print(f"  Original: {bbox}")
    print(f"  Scaled:   {scaled_bbox}")

