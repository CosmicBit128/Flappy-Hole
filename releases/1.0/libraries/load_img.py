import pygame as pg

class ImageError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

# Load an image
def load_img(image: str | pg.Surface, crop: None | tuple[int, int, int, int] = None, dark_mode=False, ratio: tuple[int, int] = (2, 2)) -> pg.Surface:
    """
    Loads an image from a file or a Pygame Surface, optionally crops it, and resizes it by a factor.
    
    Parameters:
    image (str or pygame.Surface): The file path to the image or a Pygame Surface object.
    crop (tuple, optional): A tuple (x, y, width, height) defining the crop area. Defaults to None.
    ratio (tuple or float): A tuple (width_factor, height_factor) or a single float for uniform scaling. Defaults to (2, 2).

    Returns:
    pygame.Surface: The processed Pygame Surface object.
    
    Raises:
    TypeError: If `image` is neither a string nor a Pygame Surface object.
    FileNotFoundError: If the image file cannot be loaded.
    """

    if isinstance(image, str):
        try:
            texture =pg.image.load(image)
        except pg.error as e:
            raise ImageError(f"Unable to load image file '{image}': {e}")
    elif isinstance(image, pg.Surface):
        texture = image.convert_alpha()
    else:
        raise TypeError("`image` should be a file path or Pygame Surface object")

    if crop:
        image_out = texture.subsurface(pg.Rect(crop[0], crop[1], crop[2], crop[3]))
    else:
        image_out = texture

    if dark_mode:
        darken = pg.Surface(image_out.get_size(), pg.SRCALPHA)
        darken.fill((0, 0, 0))
        darken.set_alpha(96)

        image_out.blit(darken, (0, 0))
        
    return pg.transform.scale_by(image_out, ratio)
