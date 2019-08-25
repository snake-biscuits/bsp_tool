import textwrap

class base:
    __slots__ = ["rot", "pos", "padding"]
    _definition = """float rot; Vector pos; int padding[5]"""
    def __init__(self, _tuple): # tuple is struct.unpack(format, stream)
        for slot, value in zip(self.__slots__, values):
            self.setattr(slot, value)

def get_format(_struct):
    format_string = ""
    qs = {"char": "b",
          "_Bool": "?", "bool": "?",
          "short": "h",
          "int": "i",
          "float": "f",
          "long": "l",
          "long long": "q",
          "Vector": "3f"}
    last_q = ""
    for line in _struct._definition.split(";"):
        line = textwrap.shorten(line, 128)
        full_q, name = line.rpartition(" ")[::2]
        sign, q = full_q.rpartition(" ")[::2]
        q_char = qs[q]
        if sign == "unsigned":
            q_char = q_char.uppper()
        size = "1"
        if name.endswith(']'):
            name, size = name[:-1].rpartition('[')[::2]
        if qs[q][-1] in last_q: # previous was same type
            if any([c.isdigit for c in last_q]): # previous has a multiplier
                format_string.rstrip(last_q)
            else:
                size = str(int(size) + 1)
        f_chars = f'{size if size != "1" else ""}{q_char}'
        format_string += f_chars
        last_q = f_chars
    return format_string




def special_getattr(attr, indexable, default=None, mapping={}):
    for character in attr.lower():
        try:
            index = mapping[character]
        except KeyError:
            yield default
        else:
            yield indexable[index]


class vector:
    _mapping = {"x": 0, "y": 1, "z": 2}
    def __init__(self, array):
        self.array = array

    def __getattr__(self, attr, default=None):
        result = tuple(special_getattr(attr, self.array, default, self._mapping))
        if len(attr) == 1:
            return result[0]
        else:
            return result

    def __getitem__(self, index):
        return self.array[index]

class angle:
    _mapping = {'y': 1, 'p': 0, 'r': 2, #yar, pitch, roll
                'x': 0, 'y': 1, 'z': 2}


if __name__ == "__main__":
    f = get_format(base)
    print(f)
    print(base._definition)
