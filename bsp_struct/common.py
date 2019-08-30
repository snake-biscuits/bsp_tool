import copy
import textwrap

# generate a container class, struct.iter_pack & struct.format from C code
# use "vector" for struct elements of len [3]
class base:
    __slots__ = ["i"]
    _definition = "int i"
    _vectors = {"v": {"x": 0, "y": 1, "z": 2}}
    def __init__(self, _tuple): # tuple is struct.unpack(format, stream)
        for slot, value in zip(self.__slots__, _tuple):
            if slot in self._vectors:
                mapping = self._vectors[slot]
                self.setattr(slot, vector(value, mapping))
            else:
                self.setattr(slot, value)

    def flat_tuple(self):
        "recreate the tuple this instance was initialised from"
        _tuple = []
        for slot in self.__slots__:
            value = self.getattr(slot)
            if not isinstance(value, (list, tuple, vector)):
                _tuple.append(value)
            elif isinstance(value, vector):
                for x in value.array:
                    _tuple.append(x)
            else:
                for x in value:
                    _tuple.append(x)
        return _tuple


def get_format(_struct): # check for and skip comments
    format_string = []
    qualifiers = {"char": [1, "b"],
                  "_Bool": [1, "?"], "bool": [1, "?"],
                  "short": [1, "h"],
                  "int": [1, "i"],
                  "float": [1, "f"],
                  "long": [1, "l"],
                  "long long": [1, "q"],
                  "Vector": [3, "f"]}
    last_qualifier = [0, "0"]
    for line in _struct._definition.split(";")[:-1]:
        line = textwrap.shorten(line, 128)
        qualifier, name = line.rpartition(" ")[::2]
        signed, qualifier = qualifier.rpartition(" ")[::2]
        current = copy.deepcopy(qualifiers[qualifier])
        if signed == "unsigned":
            current[1] = current[1].upper()
        if name.endswith(']'):
            current[0] *= int(name.rstrip(']').rpartition('[')[2])
        if last_qualifier[1] == current[1]:
            format_string.pop(-1)
            current[0] += last_qualifier[0]
        format_string.append(current)
        last_qualifier = current
    format_string = ''.join([f'{s}{q}' for s, q in format_string])
    return format_string


def special_getattr(attr, indexable, default=None, mapping={}):
    for character in attr.lower():
        try:
            index = mapping[character]
            yield indexable[index]
        except KeyError:
            yield default


class vector:
    _mapping = {"x": 0, "y": 1, "z": 2}
    def __init__(self, array, mapping=self._mapping):
        self.array = array
        self._mapping = mapping

    def __getattr__(self, attr, default=None):
        result = tuple(special_getattr(attr, self.array, default, self._mapping))
        if len(attr) == 1:
            return result[0]
        else:
            return result

    def __getitem__(self, index):
        return self.array[index]

class angle:
    _mapping = {'y': 1, 'p': 0, 'r': 2, # yar, pitch, roll
                'x': 0, 'y': 1, 'z': 2}


if __name__ == "__main__":
    f = get_format(base)
##    for lump in struct.iter_unpack(LUMP_FORMAT, RAW_LUMP):
##        master.lump.append(lump_class(lump))
