import itertools
from OpenGL.GL import *
import vector

bpp_of = {GL_BGR: 24}

class texture:
    """Holds the pixels of a texture + some metadata"""
    __slots__ = 'filename', 'width', 'height', 'pixel_format', 'bpp',
                'pixels', '_pixel_size', '_row_size'
    
    def __init__(self, filename: str, width: int, height: int, pixel_format: OpenGL.constant.IntConstant, pixels: bytes):
        self.filename = filename
        self.width = width
        self.height = height
        self.pixel_format = pixel_format
        self.bpp = bpp_of[pixel_format]
        self.pixels = pixels
        self._pixel_size = self.bpp // 8
        self._row_size = self._pixel_size * width

    def __getitem__(self, index):
        """expect index in form (x, y) from top left"""
        x, y = index
        pixel_start = pixel_size * x + row_size * y
        return self.pixels[pixel_start:pixel_start + self._pixel_size]

    def rotate(self, times): # glRotate may be good enough for cubemaps
        """rotate 90 * times degrees"""
        times = times % 4
        if times == 2:
            ...
        # map indices in self.pixels to a x, y coord
        # modify pixels
        # new_pixels = self.pixels[]
        return texture(self.filename, self.width, self.height, self.pixel_format,
                       new_pixels)

    def scale(self, x, y):
        """linear interpolation ONLY"""
        if x % 2 != 0:
            raise RuntimeError("You're not my Power 2")
        if y % 2 != 0:
            raise RuntimeError("Can't get no kicks just out of you")
        pixel_count - self.width * self.height
        ps = self._pixel_size
        new_pixels = [self.pixels[i:i + ps] for i in range(0, pixel_count, ps * int(1 / x))]
        rs = self._row_size
        new_pixels = [self.pixels[i:i + rs] for i in range(0, pixel_count, rs * int(1 / y))]
        new_pixels = bytes(itertools.chain(*new_pixels))
        new_width = int(width * x)
        new_height = int(height * y)
        return texture(self.filename, new_width, new_height, self.pixel_format,
                       new_pixels)


def load_BMP(filename):
    file = open(filename, 'rb')
##    file.read(...)
    ...
    return texture(filename, width, height, pixel_format)
