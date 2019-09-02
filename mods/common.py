# generate a container class, struct.iter_pack & struct.format from C code
import copy
import textwrap

class base:
    __slots__ = []
    _format = ""
    _arrays = {}
    def __init__(self, _tuple): # tuple from: struct.unpack(format, stream)
        i = 0
        for attr in self.__slots__:
            if attr in self._arrays:
                array = self._arrays[attr]
                if isinstance(array, (dict, list)):
                    length = len(array)
                    vec = mapped_array(_tuple[i:i + length], mapping=array)
                    setattr(self, attr, vec)
                    i += length
                else: # integer denoting array length
                    setattr(self, attr, _tuple[i:i + array])
                    i += array
            else:
                setattr(self, attr, _tuple[i])
                i += 1

    def __repr__(self):
        return f"{self.__class__.__name__}({self.flat()})"

    def flat(self):
        """recreate the iterable this instance was initialised from"""
        _tuple = []
        for slot in self.__slots__:
            value = getattr(self, slot)
            if not isinstance(value, (list, tuple, mapped_array)):
                _tuple.append(value)
            else:
                for x in value:
                    _tuple.append(x)
        return _tuple


##def get_format(definition):
##    format_string = []
##    qualifiers = {"char": [1, "b"],
##                  "_Bool": [1, "?"], "bool": [1, "?"],
##                  "short": [1, "h"],
##                  "int": [1, "i"],
##                  "float": [1, "f"],
##                  "long": [1, "l"],
##                  "long long": [1, "q"],
##                  "Vector": [3, "f"]}
##    last_qualifier = [0, "0"]
##    for line in definition.split(";")[:-1]:
##        line = textwrap.shorten(line, 128)
##        qualifier, name = line.rpartition(" ")[::2]
##        signed, qualifier = qualifier.rpartition(" ")[::2]
##        # ^ perhaps use regex to handle this and comments
##        current = copy.deepcopy(qualifiers[qualifier])
##        if signed == "unsigned":
##            current[1] = current[1].upper()
##        if name.endswith(']'):
##            current[0] *= int(name.rstrip(']').rpartition('[')[2])
##        if last_qualifier[1] == current[1]:
##            format_string.pop(-1)
##            current[0] += last_qualifier[0]
##        format_string.append(current)
##        last_qualifier = current
##    format_string = ''.join([f'{s}{q}' for s, q in format_string])
##    return format_string


##def class_from(definition):
##    """Takes a struct definition in C, and returns a python class
##The returned class contains a format string for struct.unpack"""
##    class out(base):
##        __slots__ = [...]
##        _format = ...
##        ...
##    return out


class mapped_array: # generate a new mapping from list of string
    _mapping = [*"xyz"]
    def __init__(self, array, mapping=_mapping):
        if isinstance(mapping, dict):
            self._mapping = list(mapping.keys())
            i = 0
            for segment_key, segment_map in mapping.items():
                segment = array[i:i + len(segment_map)]
                segment_array = mapped_array(segment, mapping=segment_map)
                setattr(self, segment_key, segment_array)
                i += len(segment_map)
        else: # list of strings
            for attr, value in zip(mapping, array):
                setattr(self, attr, value)
            self._mapping = mapping

    def __getitem__(self, index):
        return getattr(self, self._mapping[index])

    def __iter__(self):
        return iter([getattr(self, a) for a in self._mapping])

    def __repr__(self):
        out = []
        for attr, value in zip(self._mapping, self):
            out.append(f"{attr}: {value}")
        return f"<mapped_array ({', '.join(out)})>"

##class angle:
##    _mapping = {'y': 1, 'p': 0, 'r': 2, # yaw, pitch, roll
##                'x': 0, 'y': 1, 'z': 2}
##    #@property
##    #yaw()


if __name__ == "__main__":
    # class 'base' tests
    class example(base):
        __slots__ = ["id", "position", "data"]
        _format = "i3f4i"
        _arrays = {"position": [*"xyz"], "data": 4}
    
    e = example((0, .1, .2, .3, 4, 5, 6, 7))
    
    # NEW BSP LUMP LOADING STRUCTURE:
##    for lump in struct.iter_unpack(LUMP_FORMAT, RAW_LUMP):
##        master.lump.append(lump_class(lump))
