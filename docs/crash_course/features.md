# Engine Features & Design Differences

Respawn Source (Titanfall etc.) use a Squirrel VM for `vscripts` (code which interacts with entities).
This is a Source Engine feature introduced near the Left 4 Dead branch to allow for more complex IO.

Vampire - The Masquerade: Bloodlines is an older Source fork which uses Python2 for level scripts.

What makes the Respawn Source variant special is it entirely removes Source's Entity IO & scripts everything.
This allows for much finer, performance optimised control of systems with quite a bit of complexity.
Respawn's approach to design is quite different to Valve's focusing on tightly desiging a single game at a time.
Years of high-pressure crunching (bi-annual CoD releases under Activision as Infinity Ward) probably contributed to this style.
Valve, on the other hand, seem to design their systems around general use.
A design process where teams are fluid & designs are often experimental makes this a near nessecity.
With direction being vague up until close to release, Valve's slow development process creates many tools.
If this were not the case, little progress would be made, with many half-finished games frequently being thrown out or archived.


Still, moving away from Entity IO towards more scripted interactions in vscript is a nice change.
In Quake, GoldSrc & Source, adding new entities required modifying the engine in C++.
Meaning Source Ports & Forks are essential

One of the great benefits to using an engine is being able to recycle old creations
```
HL2:Ep2 Antlion Guard -> L4D2 spitter
HL2 Combine Energy Ball -> Portal Energy Ball
HL2 AI Voicelines -> TF2 Voicelines -> L4D Radio / CSGO Buy Wheel -> Portal 2 Co-op "Ping" -> Apex Legends Pinging
```

## Entity IO

> TODO: break down Source entity connections


### AddOutput

> TODO: Entity hacking magic


### Scripts

> TODO: VtM:B Python scripts

> TODO: `vscripts`



## Triangle Soups
    
> TODO: Lightmap seams, baked physics, vis splitting, 



## Texture Streaming

> TODO: Titanfall 2 GDC Talks



## PakFiles

> TODO: Quake .pak, Quake3 .pak3, .vpk

> TODO: Filesystem mounting

> TODO: embedded cubemaps & patch materials, custom assets


## Complimentary Files

### Lump Files

> TODO: link to lump breakdown


### AI Navigation

> TODO: .ain, .nm, popfiles


### External entities

> TODO: Quake3 .ent, Respawn .ent, Vindictus


### Cache

> TODO: Source soundcache, particle manifests


## Source Ports

> TODO


## Engine Licensing

> TODO



## References

> TODO: Admer456 Half-Life SDK, PlanetVampire VtM:B SDK, Dark Messiah SDK, Tactical Intevention SDK
