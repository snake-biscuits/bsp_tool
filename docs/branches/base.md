## Basics
`base` extents the built-in `struct` module
`LumpClass` definitions help organise & present bytes in a more human-readable form
Handles the majority of the raw bytes -> Python objects translation

## Common members
### `_format`
`struct` string defining a stream of C-like types
Has some subtle rules around aligning to read boundaries

### `_classes`
Applies to members post-intantiation
Helpful for `vector` math & `enum` representation
> TODO: assumptions made about `_classes`  by `as_tuple` / `as_bytes`


## Common methods
### `from_bytes`
Creates a `LumpClass` instance from `bytes`

### `from_stream`
Same as `from_bytes`
Gets `sizeof(self)` so you don't have to

### `as_bytes`
Inverse of `from_bytes`

### `as_cpp`
Presents a `C/C++` equivalent representation to the `LumpClass` definition
**Not a `@staticmethod`!**
Could be better, but decent for machine translation

### `as_tuple`
A `struct` friendly flattened form
Used as an intermediary between full `LumpClass`es & bytes



## `Struct`
For complex C/C++ `struct`s
More memory effecient than `MappedArray`
Less flexible than `MappedArray`, but still powerful

### Translation sample
```c++
struct Example {
    struct { int8_t x, y, z; } origin;
    uint32_t foo: 22;
    uint32_t bar: 10;
}
```
```python
class Example(Struct):
    __slots__ = ["origin", "bitfield"]
    _format = "3bI"
    _arrays = {"origin": [*"xyz"]}
    _bitfields = {"bitfield": {"foo": 22, "bar": 10}}
```


## `MappedArray`
For simple C/C++ `struct`s
Fast & Flexible

Can be nested, though `list` `_mapping`s are preferred
`dict` nested `_mapping`s are used by `Struct._arrays`

Can be defined at runtime:
```python
BitField(_mapping=[*"xyz"], _format="3b").from_bytes("\x07\x06\x01")
```

### Translation sample
```c++
struct Example { int8_t x, y, z; };
```
```python
class Example(MappedArray):
    _mapping = [*"xyz"]
    _format = "3b"
```


## `BitField`
Single Integer -> multiple Python object
Equivalent to C/C++ bitfields (tightly packed integers)

Can be defined at runtime:
```python
BitField(_fields={"foo": 22, "bar": 10}, _format="I").from_bytes("\x07\x06\x01\xFF")
```

### `as_int`
`BitField` only supports single integers at time of writing
So, `as_int` replaces `as_tuple`

### Translation Sample
```c++
struct Example {
    uint32_t foo: 22;
    uint32_t bar: 10;
};
```
```python
class Example(BitField):
    _fields = {"foo": 22, "bar": 10}
    _format = "I"
```
