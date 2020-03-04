"""Can unpack a variety of Valve text-formats including .vmt & the Client Schema"""
#TODO: spot keys that appear more than once and pluralise
## e.g. "visgroupid" "7"\n"visgroupid" "8" = {'visgroupid': ['7', '8']}
#TODO: Functions for handling the horrible visgroup system
import io
import textwrap

def pluralise(word):
    if word.endswith('f'): # self -> selves
        return word[:-1] + 'ves'
    elif word.endswith('y'): # body -> bodies
        return word[:-1] + 'ies'
    elif word.endswith('ex'): # vertex -> vertices
        return word[:-2] + 'ices'
    else: # side -> sides
        return word + 's'

def singularise(word):
    if word.endswith('ves'): # self <- selves
        return word[:-3] + 'f'
    elif word.endswith('ies'): # body <- bodies
        return word[:-3] + 'y'
    elif word.endswith('ices'): # vertex <- vertices
        return word[:-4] + 'ex'
    elif word.endswith('s'): # side <- sides
        return word[:-1]
    else: # assume word is already singular
        return word

class scope:
    """Handles a string used to index a multi-dimensional dictionary, correctly reducing nested lists of dictionaries"""
    def __init__(self, strings=[]):
        self.strings = strings

    def __len__(self):
        """Returns depth, ignoring plural indexes"""
        return len(filter(lambda x: isinstance(x, str), self.strings))

    def __repr__(self):
        """Returns scope as a string that can index a deep dictionary"""
        scope_string = ''
        for string in self.strings:
            if isinstance(string, str):
                scope_string += f"['{string}']"
            elif isinstance(string, int):
                scope_string += f"[{string}]"
        return scope_string

    def add(self, new):
        self.strings.append(new)

    def reduce(self, count):
        for i in range(count):
            try:
                if isinstance(self.strings[-1], int):
                    self.strings = self.strings[:-2]
                else:
                    self.strings = self.strings[:-1]
            except:
                break


def namespace_from(text_file):
    """String or .vmf file to nested namespace"""
    if isinstance(text_file, io.TextIOWrapper):
        file_iter = text_file.readlines()
    elif isinstance(text_file, str):
        file_iter = text_file.split('\n')
    else:
        raise RuntimeError(f'Cannot construct dictionary from {type(text_file)}!')
    namespace_nest = namespace({})
    current_scope = scope([])
    previous_line = ''
    for line_number, line in enumerate(file_iter):
        try:
            new_namespace = namespace({'_line': line_number})
            line = line.rstrip('\n')
            line = textwrap.shorten(line, width=200) # cleanup spacing, may break at 200+ chars
            if line == '' or line.startswith('//'): # ignore blank / comments
                continue
            elif line =='{': # START declaration
                current_keys = eval(f'namespace_nest{current_scope}.__dict__.keys()')
                plural = pluralise(previous_line)
                if previous_line in current_keys: # NEW plural
                    exec(f'namespace_nest{current_scope}[plural] = [namespace_nest{current_scope}[previous_line]]')
                    exec(f'namespace_nest{current_scope}.__dict__.pop(previous_line)')
                    exec(f'namespace_nest{current_scope}[plural].append(new_namespace)')
                    current_scope = scope([*current_scope.strings, plural, 1]) # why isn't this a method?
                elif plural in current_keys: # APPEND plural
                    current_scope.add(plural)
                    exec(f"namespace_nest{current_scope}.append(new_namespace)")
                    current_scope.add(len(eval(f'namespace_nest{current_scope}')) - 1)
                else: # NEW singular
                    current_scope.add(previous_line)
                    exec(f'namespace_nest{current_scope} = new_namespace')
            elif line == '}': # END declaration
                current_scope.reduce(1)
            elif '" "' in line: # KEY VALUE
                key, value = line.split('" "')
                key = key.lstrip('"')
                value = value.rstrip('"')
                exec(f'namespace_nest{current_scope}[key] = value')
            elif line.count(' ') == 1:
                key, value = line.split()
                exec(f'namespace_nest{current_scope}[key] = value')
            previous_line = line.strip('"')
        except Exception as exc:            
            print(f'error on line {line_number:04d}:\n{line}\n{previous_line}')
            raise exc
    return namespace_nest

    
class namespace: # DUNDER METHODS ONLY!
    """Nested Dicts -> Nested Objects"""
    def __init__(self, nested_dict):
        for key, value in nested_dict.items() if isinstance(nested_dict, dict) else nested_dict.__dict__.items():
            if isinstance(value, dict):
                self[key] = namespace(value)
            elif isinstance(value, list):
                self[key] = [namespace(i) for i in value]
            else:
                self[key] = value
    
    def __setitem__(self, index, value):
        setattr(self, str(index), value)
    
    def __getitem__(self, index):
        return self.__dict__[str(index)]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__.keys())

    def __repr__(self):
        attrs = [a if ' ' not in a else f'"{a}"' for a in self.__dict__.keys()]
        return f"namespace([{', '.join(attrs)}])"

    def items(self): # fix for lines_from
        for k, v in self.__dict__.items():
            yield (k, v)


def dict_from(namespace_nest):
    out = dict()
    for key, value in namespace_nest.__dict__.items():
        if isinstance(value, namespace):
            out[key] = dict_from(value)
        elif isinstance(value, list):
            out[key] = [dict_from(i) for i in value]
        else:
            out[key] = value
    return out


def lines_from(_dict, tab_depth=0): # rethink & refactor
    '''Takes a nested dictionary (which may also contain lists, but not tuples)
from this a series of strings resembling valve's text format used in .vmf files
are generated approximately one line at a time'''
    tabs = '\t' * tab_depth
    for key, value in _dict.items():
        if isinstance(value, (dict, namespace)): # another layer
            value = (value,)
        elif isinstance(value, list): # collection of plurals
            key = singularise(key)
        else: # key-value pair
            if key == '_line':
                continue
            yield f'{tabs}"{key}" "{value}"\n'
            continue
        for item in value:
            yield f'{tabs}{key}\n{tabs}' + '{\n' # open into the next layer
            for line in lines_from(item, tab_depth + 1): # recurse down
                yield line
    if tab_depth > 0:
        yield '\t' * (tab_depth - 1) + '}\n' # close the layer


def export(_dict, outfile):
    """Don't forget to close the file afterwards!"""
    print('Exporting {outfile.name} ... ', end='')
    for line in lines_from(_dict): # using a buffer to write in chunks may be wise
        outfile.write(line) # ''.join([line for line in lines_from(_dict)]) also works
    print('Done!')


def add_visgroups(vmf, visgroup_dict): # work in progress
    """Add visgroups defined in a some object"""
    # FORMAT (TOP: [INNER1, INNER2: []])
    if 'visgroups' not in vmf:
        vmf['visgroups'] = []
    if 'visgroup' in vmf.visgroups:
        vmf.visgroups['visgroups'] = [visgroup]
    if 'visgroups' not in vmf.visgroups:
        vmf.visgroups['visgroups'] = []

    visgroups = vmf.visgroups.visgroups
    max_id = max([v.visgroupid for v in visgroups])

    def recurse(iterable):
        ...
    
    for v in visgroup_dict:
        max_id += 1
        ...
        

if __name__ == "__main__":
##    from time import time
##    times = []
##    for i in range(16):
##        start = time()
##        # vmf = dict_from(open('mapsrc/test.vmf'))
##        # vmf = dict_from(open('mapsrc/test2.vmf'))
##        vmf = dict_from(open('mapsrc/sdk_pl_goldrush.vmf'))
##        time_taken = time() - start
##        print(f'import took {time_taken:.3f} seconds')
##        times.append(time_taken)
##    print(f'average time: {sum(times) / 16:.3f}')
    pass

    # filter(lambda x: x['material'] != 'TOOLS/TOOLSNODRAW' and x['material'] != 'TOOLS/TOOLSSKYBOX', all_sides)
    # [e['classname'] for e in vmf.dict['entities']]
    # all_ents_with_outputs = [e for e in vmf.entities if hasattr(e, 'connections')]
    # all_connections = [e.connections for e in all_ents_with_outputs]
    # #now add all referenced targetnames to list
    # #and create a top-down map of these ents
