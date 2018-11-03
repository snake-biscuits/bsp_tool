import enum
import itertools
from OpenGL.GL import *


class texture:
    """Holds the pixels of a texture + some metadata"""
    __slots__ = ('filename', 'width', 'height', 'pixel_format', 'bpp',
                 'pixels', '_pixel_size', '_row_size')
    
    def __init__(self, filename: str, width: int, height: int, pixel_format: OpenGL.constant.IntConstant, bpp: int, pixels: bytes):
        self.filename = filename
        self.width = width
        self.height = height
        self.pixel_format = pixel_format # order of colour channels (plugged directly into glTexImage2D)
        # glTexImage2D also requires a type field (2nd last argument)
        # this is related to _pixel_size
        # self._pixel_size = 8, GL_UNSIGNED_BYTE
        # self._pixel_size = 16, GL_UNSIGNED_SHORT
        # may as well add a method that give all glTexImage2D args after target
        self.bpp = bpp
        self.pixels = pixels
        
        self._pixel_size = self.bpp // 8
        self._row_size = self._pixel_size * width

    def __iter__(self):
        return iter([bytes(self.pixels[i:i + self._pixel_size]) for i in range(0, len(self.pixels), self._pixel_size)])

    def __getitem__(self, index):
        """expects index in form (x, y) from top left"""
        x, y = index
        pixel_start = self._pixel_size * x + self._row_size * y
        return self.pixels[pixel_start:pixel_start + self._pixel_size]

    def __setitem__(self, index, value):
        """expects value to be list of ints or bytestring of size self._pixel_size"""
        mutable_pixels = list(self.pixels)
        
        if isinstance(index, slice):
            start, stop, step = index.indices(self.width * self.height)
            pixels = stop - start
            stop = start + pixels * self._pixel_size
            step *= self._pixel_size
        else:
            x, y = index
            start = pixel_size * x + row_size * y
            stop = start + self._pixel_size
            step = 1
            
        mutable_pixels[start:stop:step] = value
        self.pixels = bytes(mutable_pixels)

    def __repr__(self):
        return f'Texture({self.filename}, {self.width} x {self.height}, {self.pixel_format.name}, {self.bpp} Bits-per-pixel)'

    def scale(self, x, y): # don't allow negatives!
        """Linear interpolation ONLY\nPlease keep your dimensions to powers of 2"""
        if self.width % 1 / x != 0.0 or (x > 1 and x % 1 != 0):
            raise RuntimeError('Cannot Smoothly Scale X-Axis')
        if self.height % 1 / y != 0.0 or (y > 1 and y % 1 != 0):
            raise RuntimeError('Cannot Smoothly Scale Y-Axis')
        x = int(x) if x >= 1 else x
        y = int(y) if y >= 1 else y
        
        new_width = int(self.width * x)
        new_height = int(self.height * y)
        
        pixel_skip_step = self._pixel_size * int(1 / x)
        new_row_size = new_width * self._pixel_size
        row_skip_step = new_row_size * int(1 / y)

        
        new_rows = []
        if x < 1:
            for i in range(0, len(self.pixels), pixel_skip_step):
                new_rows.append(self.pixels[i:i + self._pixel_size])
        elif x > 1 and isinstance(x, int):
            for i in range(0, len(self.pixels), self._pixel_size):
                new_rows.append(self.pixels[i:i + self._pixel_size] * x)
        else: # x == 1
            new_rows = [self.pixels]
        new_rows = b''.join(new_rows)
        
        new_pixels = []
        if y < 1:
            for j in range(0, len(new_rows), row_skip_step):
                new_pixels.append(new_rows[j:j + new_row_size])
        elif y > 1 and isinstance(y, int):
            for j in range(0, len(new_rows), new_row_size):
                new_pixels.append(new_rows[j:j + new_row_size] * y)
        else:
            new_pixels = [new_rows]
        new_pixels = b''.join(map(bytes, new_pixels))
        
        return texture(self.filename, new_width, new_height, self.pixel_format, self.bpp, new_pixels)


    def flip(self, axis):
        new_pixels = []
        if axis.upper() == 'X':
            for i in range(0, len(self.pixels), self._row_size):
                # flip a pixel at a time to preserve pixel_format
                new_pixels.append(bytes(reversed(self.pixels[i:i + self._row_size])))

            return texture(self.filename, self.width, self.height, self.pixel_format, self.bpp, b''.join(new_pixels))

    

def load_BMP(filename):
    filename = filename + '.bmp' if not filename.lower().endswith('.bmp') else filename
    file = open(filename, 'rb')
    magic = file.read(2)
    if magic != b'BM':
        raise RuntimeError(f'{filename} is not a supported .bmp file!')
    filesize = int.from_bytes(file.read(4), 'little')
    file.seek(10)
    pixel_array_start = int.from_bytes(file.read(4), 'little')
    dib_header_size = int.from_bytes(file.read(4), 'little')
    if dib_header_size != 40:
        raise RuntimeError(f'{filename} is not a supported .bmp file!')
    width = int.from_bytes(file.read(4), 'little')
    height = int.from_bytes(file.read(4), 'little')
    file.seek(28)
    bpp = int.from_bytes(file.read(2), 'little')
    file.seek(30)
    compression_method = int.from_bytes(file.read(4), 'little')
    if compression_method == 0:
        if bpp == 24:
            pixel_format = GL_BGR
        else:
            raise RuntimeError('Figure out the GL_ equivalent of your pixel format and paste it here')
    else:
        raise RuntimeError(f'Cannot decompress {filename}')
    file.seek(pixel_array_start)
    # rows are padded to nearest 4 BYTES
    # stick to powers of two and it shouldn't matter
    pixels = file.read()
    file.close()    
    return texture(filename, width, height, pixel_format, bpp, pixels)

################################################################################
##           MUCH OF THE CODE AFTER THIS POINT IS COPIED FROM:                ##
##      https://developer.valvesoftware.com/wiki/Valve_Texture_Format         ##
################################################################################


class VTF_FORMAT(enum.Enum): # Map RAW (uncompressed) formats to GL_ equivalents
    NONE = -1
    RGBA8888 = 0
    ABGR8888 = 2 # GL_BGRA not equivalent
    RGB888 = 3
    BGR888 = 4
    RGB565 = 5
    I8 = 6
    IA88 = 7
    P8 = 8
    A8 = 9
    RGB888_BLUESCREEN = 10
    BGR888_BLUESCREEN = 11
    ARGB8888 = 12
    BGRA8888 = 13
    DXT1 = 14
    DXT3 = 15
    DXT5 = 16
    BGRX8888 = 17
    BGR565 = 18
    BGRX5551 = 19
    BGRA4444 = 20
    DXT1_ONEBITALPHA = 21
    BGRA5551 = 22
    UV88 = 23
    UVWQ8888 = 24
    RGBA16161616F = 25
    RGBA16161616 = 26
    UVLX8888 = 27


VTF_GL_FORMAT = {VTF_FORMAT.RGBA8888: GL_RGBA, VTF_FORMAT.RGB888: GL_RGB,
                 VTF_FORMAT.BGR888: GL_BGR}

class VTF_FLAGS(enum.Enum):
    # From *.txt config file
    POINTSAMPLE = 0x00000001
    TRILINEAR = 0x00000002
    CLAMPS = 0x00000004
    CLAMPT = 0x00000008
    ANISOTROPIC = 0x00000010
    HINT_DXT5 = 0x00000020
    PWL_CORRECTED = 0x00000040
    NORMAL = 0x00000080
    NOMIP = 0x00000100
    NOLOD = 0x00000200
    ALL_MIPS = 0x00000400
    PROCEDURAL = 0x00000800
    # Automatically generated by vtex from texture data.
    ONEBITALPHA = 0x00001000
    EIGHTBITALPHA = 0x00002000
    # Newer flags from *.txt config file
    ENVMAP = 0x00004000
    RENDERTARGET = 0x00008000
    DEPTHRENDERTARGET = 0x00010000
    NODEBUGOVERRIDE = 0x00020000
    SINGLECOPY	= 0x00040000
    PRE_SRGB = 0x00080000
    NODEPTHBUFFER = 0x00800000
    CLAMPU = 0x02000000
    VERTEXTEXTURE = 0x04000000
    SSBUMP = 0x08000000
    BORDER = 0x20000000


def load_VTF(filename, level_of_detail, frame=1):
    filename = filename + '.vtf' if not filename.lower().endswith('.vtf') else filename
    file = open(filename, 'rb')
    magic = file.read(4)
    if magic != b'VTF\x00':
        raise RuntimeError(f'Encountered Invalid Magic Number: ({magic}) while loading {filename}')
    major_version = int.from_bytes(file.read(4), 'little')
    minor_version = int.from_bytes(file.read(4), 'little')
    header_size = int.from_bytes(file.read(4), 'little')
    width = int.from_bytes(file.read(2), 'little')
    height = int.from_bytes(file.read(2), 'little')
    flags = int.from_bytes(file.read(4), 'little')
    frames = int.from_bytes(file.read(2), 'little') # 1 = still image, if > 1 return multiple textures
    first_frame = int.from_bytes(file.read(2), 'little')
    file.seek(52)
    high_format = int.from_bytes(file.read(4), 'little')
    
    mipmap_count = ...
    low_format = ...
    low_width = ...
    low_height = ...
    if major_version == 7 and minor_version >= 3: # 7.3 TF2 Beta, 7.4 Orange Box
        # Source Engine ??? src/public/vtf/vtf.h
        # VTF 7.3 Disk Format
        # NOTE: After the header is the array of ResourceEntryInfo structures,
        # number of elements in the array is defined by "numResources".
        # there are entries for:
        #    eRsrcLowResImage = low-res image data
        #    eRsrcSheet = sheet data
        #    eRsrcImage = image data
        #
        # For each mip level (starting with 1x1, and getting larger)
        #   for each animation frame
        #       for each face
        #           store the image data for the face
        #
        # In memory, we store the data in the following manner:
        #   for each animation frame
        #       for each face
        #           for each mip level (starting with the largest, and getting smaller)
        #               store the image data for the face
        depth = ...
        resources_count = ...
    pixel_format = VTF_GL_FORMAT[VTF_FORMAT(high_format)]


if __name__ == "__main__":
    obsolete = load_BMP('materials/obsolete.bmp')
    grid = bytes(range(16))
    ascii_texture = texture('ascii', 4, 4, GL_BGR, 8, grid)
    
    def ascii_repr(tex):
        out = ''
        for y in range(tex.height):
            y = tex.height - y
            for x in range(tex.width):
                out += chr(97 + (sum(tex[(x, y)]) // tex._pixel_size))
            out += '\n'
        print(out)
    
    ascii_repr(ascii_texture)
    ascii_repr(ascii_texture.scale(2, .5))

    ascii_repr(obsolete.scale(.25, .125))

    sky = load_VTF('materials/skybox/sky_upwardside.vtf', 0)
    # HAVE FUN :3
    ascii_repr(sky.scale(.125, .25))
