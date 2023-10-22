## Meta
### Structure
Branches are grouped by developer
In some cases the format developer is ambiguous
Most `developer.branch` pairing should be intuitive, but YMMV



## `developers`
A list of all developers
```python
[branch for dev in developers for branch in dev.scripts]
```


## `with_magic`
Dictionary for selecting branches from the first 4 bytes of a `.bsp` file


## `identify`
Dictionary for selecting branches from the first 8 bytes of a `.bsp` file
Has a few collisions, defaults to the most common implementations
[GitHub Issue](https://github.com/snake-biscuits/bsp_tool/issues/17) tracking colliding branches


## `source_based`
List of branches with version lumps


## `quake_based`
List of branches with unversioned lumps


## `of_engine`
Dict listing lumps for various named engines

Major named engine groups include:
 * GoldSrc
 * Id Tech 2
 * Id Tech 3
 * Source
 * Titanfall
