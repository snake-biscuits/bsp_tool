# Lump Relationship Maps

Examples taken from `respawn.titanfall`

> TODO: could we use SQL -> ERD?


### Legend

```
~>   Implicit   can be calculated
->   Direct     take an index
-?>  Maybe      assumed connection
\->  Secondary  one of many connections
|    Parallel   index either lump
```


## Top-level

Working relationship
`Quartermaster  relationship  Agent  relationship  Agent`
```
CMGrid ~> CMGridCell -> CMGeoSet
Entity -> Model ~> CMGridCell
```


## Context

Private Relationship
`Agent  relationship  Agent`
```
CMGeoSet | CMGeoSetBounds
```


## Branching Subsystem

Polycule
`Agent  relationship  multliple Agents`
```
CMGeoSet -> CMBrush
        \-> Tricoll
```


## Branch of Subsystem
Family
`Agent  relationship  Child  relationship  Child`
```
CMBrush -> CMBrushSideProperty -> TextureData -> TextureDataStringTable -> TextureDataStringData
       \-> CMBrushSidePlaneOffset -> Planes
```
