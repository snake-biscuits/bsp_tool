# `.bsp` Essential lumps

## Entities

The Entities lump is present in every bsp format[citation needed]
Struture is essentially identical to that in `.map` & `.vmf` files (level editor saves)

Each variant of entity or "`classname`" is linked to a class hard-coded into the engine.[^Admer_ents]
These entities are exposed to the editor via `.def` or `.fgd` files, depending on editor.
Valve's Worldcraft & Hammer editors use `.fgd` as can [Trenchbroom](github.com/TrenchBroom/TrenchBroom)

Entities describe dynamic elements which can be interfaced with via scripts or entity IO


### Entity IO

The Entity IO (Input/Output) system is available in almost every Quake-based game engine.
Respawn's Titanfall fork of the Source Engine entirely removes Entity IO[^Slothy]

> TODO: Triggers & Buttons

> TODO: Scripts



## Models (Level Geometry)

> NOTE: `Model[0]` is always worldspawn; static "world" geometry with pre-baked lighting & physics

> NOTE: Other Models are always centered on `0, 0, 0`, their true position comes from the associated entity


### Worldspawn

> TODO



## Mesh data

> TODO

Valve:
```
Model -> Face -> SurfEdge -> Edge -> Vertex
```

Respawn:
```
Model -> Mesh -> MeshIndices -\
             \-> MaterialSort -> VertexReservedX
```


### Triangle Soup

> TODO

Source uses Faces & Displacements (and also Primitives for fixing up T-junctions[^flipcode])

Displacements are the closest

> TODO: Learn how Radiant "Patches" are compiled into Geometry



## Visibility Data

> TODO: Portals, Leaves, VisClusters



## Static Lighting Data

> TODO: Lightmaps, Lightprobes, WorldLights

> TODO: Quake 3 Lightmap Textures

> TODO: Early Quake / Source Lightmap Compression



## Static Props

Static Props are mostly found in Source Engine branches, these draw from external model files.
Each prop is named in the `.bsp` for the engine to cache at load time.
In Source, each prop is essentially welded onto the viscluster it appears in.
However, the CS:GO branch fuses props into one big triangle soup for a low rendering cost.

Props consume a lot of geo so you generally want to unload them when not on-screen.
This is especially true of older rendering approaches like BSP.
So you can expect to find Static Props tied to visibility systems.
A fair chunk of StaticProp fields are filters for the rendering config.
e.g. Only render from X or less units away, do not render at Direct X level Y.


More Quake-based engines tend to use triangle soups to directly bake models into maps.
Triangle soups are still a bit more complex but are quite basic.
Unlike Source Engine static props they cannot have LoD (Level of Detail) substitution.
Matching with level geo is much easier as they are rendered with the same shaders and lightmaps tho.
Sort of a happy medium, embedding bsps is also possible in some engines, but such knowledge is arcane.[^Admer_magic]

> NOTE: Not every engine allows for static props, Triangle Soups likely fill this gap for those engines



## References

[^Admer_magic]: Admer456 on Twitter: [embedding `.bsp` with `env_sprite`](https://twitter.com/theAdmer456/status/1317930920003981313)  
[^Admer_ents]: Admer456 on Youtube: [Half-Life SDK Programming #2: Creating a new entity](https://www.youtube.com/watch?v=ECp6o6ex0Ok&list=PLZmAT317GNn19tjUoC9dlT8nv4f8GHcjy&index=4)  
[^Slothy]: Rackspace on Youtube: [Jon Shiring Public Tech Talk at Rackspace](https://www.youtube.com/watch?v=ayF8e8q_aA8)  
[^flipcode]: Jacco Bikker on flipcode: [Building a 3D Portal Engine - Issue 17 - End Of Transmission](https://www.flipcode.com/archives/Building_a_3D_Portal_Engine-Issue_17_End_Of_Transmission_.shtml)  

> TODO: useful timestamps for Youtube references
