# bsp_tool
 A library for .bsp file analysis & modification

`bsp_tool` provides a Command Line Interface for exploring & editing .bsp files  
Current development is focused on bringing new maps to Titanfall 1 & 2 and Counter-Strike: Online 2  

## Installation
To use / contribute to the latest version, clone this package
```
git clone git@github.com:snake-biscuits/bsp_tool.git
```

Or to use the latest stable release, install via [pip](https://pypi.org/project/bsp-tool/) (Python 3.7+)
```
pip install bsp_tool
```

> The last PyPi release (v0.2.2) is close to a year old  
> v0.3.0 has made many [changes](./CHANGELOG.md) and is the recommended version

## Fair Use & Commercial Works
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


## Guides
[Basic Usage](./usage.html) <!-- Split up / include links to the wiki -->
<!-- [BSP format crash course](...) # include branch specific pages -->
<!-- Links & credits to other community tools -->

## Supported Games
  * [Id Software](./id_software/SUPPORTED.html)
  * [Infinity Ward](./infinity_ward/SUPPORTED.html)
  * [Nexon](./nexon/SUPPORTED.html)
  * [Respawn Entertainment](./respawn/SUPPORTED.html)
  * [Valve Software](./valve/SUPPORTED.html)

## .bsp Format Reference
  [Timeline of "relevant" games](./timeline/games.html)  
  [Game engine bloodline](./timeline/engines.html)

## [Changelog](./CHANGELOG.html)
You can see a list of all changes in the [changelog](./CHANGELOG.html)


## Contributing
At present the easiest way to contribute to the project is to add or extend a "branch script" for a game `bsp_tool` doesn't yet fully support  
[Learn More](https://github.com/snake-biscuits/bsp_tool/wiki)
