# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  
Current development is focused on bringing new maps to Titanfall 1 & 2 and Counter-Strike: Online 2


## Installation
To use the latest version, clone from git:
```
$ git clone git@github.com:snake-biscuits/bsp_tool.git
```

Or to use the latest stable release, install via [pip](https://pypi.org/project/bsp-tool/) (Python 3.7+):
```
pip install bsp_tool
```

> NOTE: The last PyPi release (v0.2.2) is close to a year old  
> v0.3.0 has made many [changes](./CHANGELOG.md) and is the recommended version


## Fair Use
**Please do not use `bsp_tool` to copy or steal another creator's work**  
The primary goal of `bsp_tool` is to extend community mapping tools  

### Always
  - **Ask** the creator's permission before touching their work  
  - **Understand** that by default creator's works are under copyright  
    - [US Law Copyright FAQ](https://www.copyright.gov/help/faq/faq-general.html#mywork)
    - [US Copyright Duration](https://www.copyright.gov/help/faq/faq-duration.html)
      - [Circular 15a](https://www.copyright.gov/circs/circ15a.pdf)  
  - **Contact** the original creator to get their permission  
    - This can get complicated  
    - Some creators don't hold the copyright on their works  
      - often because of Company / Publisher contracts  
  - **Credit** the original creator; once you have permission to share a derivative work  
  - **Support** the official release

**DO NOT** use this tool to steal another creator's work  
**DO** use this tool to understand the .bsp format(s) and create more specific tools

> Be aware that this gets even more complicated with commercial projects


## Usage

To load a .bsp file in python:

```python
>>> import bsp_tool
>>> bsp_tool.load_bsp("map_folder/filename.bsp")
<ValveBsp filename.bsp (VBSP version 20) at 0x00...>
```

Full documentation: [snake-biscuits.github.io/bsp_tool/](https://snake-biscuits.github.io/bsp_tool/)

## Supported Games
  * [Id Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software)
    - [Quake](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake.py)
    - [Quake III Arena](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/id_software/quake3.py)
  * [Infinity Ward](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward)
    - [Call of Duty (2003)](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/infinity_ward/call_of_duty1.py)
  * [Nexon](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon)
    - [Counter-Strike: Online 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/cso2.py)
    - [Vindictus](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/nexon/vindictus.py)
  * [Respawn Entertainment](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn)
    - [Titanfall](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall.py)
    - [Titanfall 2](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/titanfall2.py)
    - [Apex Legends](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/respawn/apex_legends.py)
  * [Valve Software](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve)
    - [Counter-Strike: Global Offensive](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/cs_go.py)
    - [Counter-Strike: Source](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/cs_source.py)
    - [Orange Box](https://github.com/snake-biscuits/bsp_tool/tree/master/bsp_tool/branches/valve/orange_box.py)
