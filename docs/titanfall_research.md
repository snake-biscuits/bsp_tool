# Titanfall rBSP format research


## Source engine basis

 * Titanfall (2014) was built on a fork of Valve's Source Engine around 2011 (Portal 2's engine)[^Lee]  
 * From here Respawn built on the Valve's variant of the `.bsp` format[^VDC][^VDC_Titanfall]



## Pre-existing research

 * Cra0kalo & ata4 Titanfall 1 lump names[^Cra0]  
 * Titanfall 2 `.bsp` -> `.obj`,[^Warmist] originally by [Icepick](https://titanfallmods.com/) dev [WillCo](https://will.io)  
   Possibly derived from a function BobTheBob found (rediscovered?) in Titanfall 2 which does the same thing



## Current research

* [Legion+ `.bsp` blender converter](https://github.com/r-ex/LegionPlus/blob/main/Legion/RBspLib.h)  
* [Northstar Discord: Modding > Research > Maps](https://discord.com/channels/920776187884732556/925435799057604709)  

This list is incomplete, you can help by expanding it.



## `engine.dll` lump loads table

> NOTE: we mostly use [Ida](https://hex-rays.com/ida-free/) & [010 Editor](https://www.sweetscape.com/download/010editor/)
> TODO: explain `Mod_*` functions
> TODO: explain how tracing error message strings helped us identify these lump reads
> TODO: compare Source Engine (open-source SDK) function calls

> NOTE: lumps indexes are listed in hexadecimal, but unknowns are expressed in decimal
> NOTE: duplicate reads have been traced to version switches (bsp version & lump version)

```
TITANFALL 2 LUMP LOAD FUNCTION ADDRESSES
by BobTheBob & b!scuit

lump 00 loaded @ engine.dll + 00126f1f  ENTITIES
lump 01 loaded @ engine.dll + 001276cb  PLANES
lump 02 loaded @ engine.dll + 001279cb  TEXTURE_DATA
lump 03 loaded @ engine.dll + 001282bb  VERTICES
lump 04 loaded @ engine.dll + 000c8c9e  LIGHTPROBE_PARENT_INFOS
lump 05 loaded @ engine.dll + 000cbb7b  SHADOW_ENVIRONMENTS
lump 06 loaded @ engine.dll + 000c8acc  LIGHTPROBE_BSP_NODES
lump 07 loaded @ engine.dll + 000c8b9c  LIGHTPROBE_BSP_REF_IDS
UNUSED_8 to UNUSED_13
lump 0E loaded @ engine.dll + 001278ef  MODELS
lump 0E loaded @ engine.dll + 000c6fd4  MODELS
UNUSED_15 to UNUSED_23
lump 18 loaded @ engine.dll + 00126f2d  ENTITY_PARTITIONS
UNUSED_25 to UNUSED_28
lump 1D loaded @ engine.dll + 0012755b  PHYSICS_COLLIDE
lump 1E loaded @ engine.dll + 000cc0c1  VERTEX_NORMALS
UNUSED_31 to UNUSED_34
lump 23 loaded @ engine.dll + 000c87f0  GAME_LUMP
lump 24 loaded @ engine.dll + 0c00892c  LEAF_WATER_DATA
UNUSED_37 to UNUSED_39
lump 28 not loaded                      PAKFILE
UNUSED_41
lump 2A loaded @ engine.dll + 000c8461  CUBEMAPS
lump 2B loaded @ engine.dll + 001279dd  TEXTURE_DATA_STRING_DATA
lump 2C loaded @ engine.dll + 001279ff  TEXTURE_DATA_STRING_TABLE
UNUSED_45 to UNUSED_53
lump 36 loaded @ engine.dll + 000c6e71  WORLDLIGHTS
lump 37 loaded @ engine.dll + 000c6ec4  WORLDLIGHT_PARENT_INFO
UNUSED_56 to UNUSED_61
Physics:
lump 3E not loaded                      PHYSICS_LEVEL  (empty, only version matters)
UNUSED_63 to UNUSED_65
lump 42 loaded @ engine.dll + 00127dbc  TRICOLL_TRIS
UNUSED_67
lump 44 loaded @ engine.dll + 00127dcd  TRICOLL_NODES
lump 45 loaded @ engine.dll + 00127d0d  TRICOLL_HEADERS
UNUSED_70
Rendering:
lump 47 loaded @ engine.dll + 000c9cbc  VERTS_RESERVED_0 / UNLIT  (in a for loop?)
lump 47 loaded @ engine.dll + 000c9ea0  VERTS_RESERVED_0 / UNLIT
lump 48 loaded @ engine.dll + 000c9ea0  VERTS_RESERVED_1 / LIT_FLAT
lump 49 loaded @ engine.dll + 000c9ea0  VERTS_RESERVED_2 / LIT_BUMP
lump 4A loaded @ engine.dll + 000c9ea0  VERTS_RESERVED_3 / UNLIT_TS
lump 4B not loaded                      VERTS_RESERVED_4 / BLINN_PHONG
lump 4C not loaded                      VERTS_RESERVED_5
lump 4D not loaded                      VERTS_RESERVED_6
lump 4E not loaded                      VERTS_RESERVED_7
lump 4F loaded @ engine.dll + 000c9b00  MESH_INDICES
lump 50 loaded @ engine.dll + 000ca685  MESHES
lump 51 loaded @ engine.dll + 000c985a  MESH_BOUNDS
lump 52 loaded @ engine.dll + 000ca673  MATERIAL_SORT
lump 53 loaded @ engine.dll + 000c96bc  LIGHTMAP_HEADERS
UNUSED_84
Physics / Visibility:
lump 55 loaded @ engine.dll + 0012740b  CM_GRID
lump 56 loaded @ engine.dll + 00127494  CM_GRID_CELLS
lump 57 loaded @ engine.dll + 0012732f  CM_GEO_SETS
lump 58 loaded @ engine.dll + 001283d8  CM_GEO_SET_BOUNDS
lump 59 loaded @ engine.dll + 0012780b  CM_PRIMITIVES
lump 5A loaded @ engine.dll + 001283d8  CM_PRIMITIVE_BOUNDS
lump 5B loaded @ engine.dll + 00126e1b  CM_UNIQUE_CONTENTS
lump 5C loaded @ engine.dll + 00126ceb  CM_BRUSHES
lump 5D loaded @ engine.dll + 00126b2f  CM_BRUSH_SIDE_PLANE_OFFSETS
lump 5E loaded @ engine.dll + 00126c0b  CM_BRUSH_SIDE_PROPS
lump 5F not loaded                      CM_BRUSH_TEX_VECS     (for bsp compiler?)
lump 60 loaded @ engine.dll + 00127dde  TRICOLL_BEVEL_STARTS
lump 61 loaded @ engine.dll + 00127def  TRICOLL_BEVEL_INDICES
lump 62 loaded @ engine.dll + 000c954c  LIGHTMAP_DATA_SKY
Cascade Shadow Mapping:
lump 63 loaded @ engine.dll + 000cbe87  CSM_AABB_NODES
lump 64 loaded @ engine.dll + 000cbe96  CSM_OBJ_REFS
Lighting:
lump 65 loaded @ engine.dll + 0c8fnoc0  LIGHTPROBES
lump 66 loaded @ engine.dll + 000cbfc2  STATIC_PROP_LIGHTPROBE_INDEX
lump 67 loaded @ engine.dll + 000c8c7a  LIGHTPROBE_TREE
lump 68 loaded @ engine.dll + 000c8c8c  LIGHTPROBE_REFS
lump 69 loaded @ engine.dll + 000c9352  LIGHTMAP_DATA_REAL_TIME_LIGHTS
Visibility:
lump 6A loaded @ engine.dll + 000cacd2  CELL_BSP_NODES
lump 6B loaded @ engine.dll + 000cace3  CELLS
lump 6C loaded @ engine.dll + 000cacf4  PORTALS
lump 6D loaded @ engine.dll + 000cad05  PORTAL_VERTS
lump 6E loaded @ engine.dll + 000cad16  PORTAL_EDGES
lump 6F loaded @ engine.dll + 000cad27  PORTAL_VERT_EDGES
lump 70 loaded @ engine.dll + 000cad38  PORTAL_VERT_REFS
lump 71 loaded @ engine.dll + 000cad49  PORTAL_EDGE_REFS
lump 72 loaded @ engine.dll + 000cad5a  PORTAL_EDGE_ISECT_EDGE
lump 73 loaded @ engine.dll + 000cad6b  PORTAL_EDGE_ISECT_AT_VERT
lump 74 loaded @ engine.dll + 000cad7c  PORTAL_EDGE_ISECT_HEADER
lump 75 loaded @ engine.dll + 000cad8d  OCCLUSION_MESH_VERTS
lump 76 loaded @ engine.dll + 000cad9c  OCCLUSION_MESH_INDICES
lump 77 loaded @ engine.dll + 000cadad  CELL_AABB_NODES
lump 78 loaded @ engine.dll + 000cadbe  OBJ_REFS
lump 79 loaded @ engine.dll + 000cadcf  OBJ_REF_BOUNDS
lump 7A loaded @ engine.dll + 000c9220  LIGHTMAP_DATA_REAL_TIME_LIGHTS_PAGE
Flags:
lump 7B loaded @ engine.dll + 000cade0  LEVEL_INFO
Shadow Meshes:
lump 7C loaded @ engine.dll + 000cbb3a  SHADOW_MESH_OPAQUE_VERTS
lump 7D loaded @ engine.dll + 000cbb4b  SHADOW_MESH_ALPHA_VERTS
lump 7E loaded @ engine.dll + 000cbb5c  SHADOW_MESH_INDICES 
lump 7F loaded @ engine.dll + 000cbb6a  SHADOW_MESH_MESHES
```



## Extreme SIMD transcript & C++ `intrinsics.hpp`

Transribed from: [GDC 2018: Extreme SIMD - Optimized Collision Detection in Titanfall](https://www.youtube.com/watch?v=6BIfqfC1i7U)

### Bounding Volume Heirarchies (AABB Trees)

```
BVH4 NODE (64 bytes)

|       0       |       1       |       2       |       3       |
| Min X | Max X | Min X | Max X | Min X | Max X | Min X | Max X |  128bits (for SSE SIMD registers)
| Min Y | Max Y | Min Y | Max Y | Min Y | Max Y | Min Y | Max Y |
| Min Z | Max Z | Min Z | Max Z | Min Z | Max Z | Min Z | Max Z |
| Index    | 01 | Index    | 23 | Index    | cm | Index    | XX |

| 8b |
| 16bit |
| 24bit    | 8b |
|     32bit     |
```

* 16bits per min/max (signed short?)
* collision detection performed on the whole node, one axis at a time
* Index is 24 bits (object mapped to depends on type flag)

```
[01] = 8 bits, split into 4 for 0 child type & 1 child type
[23] = 8 bits, split into 4 for 2 child type & 3 child type
[cm] = "8 bit index into 32-bit collision mask array"
       e.g. TITAN | PLAYER | WATER | BULLETS
[XX] = b"\x00\x00" (assumed)
```

> NOTE: Collision masks might be related to Quake / Source Contents flags (compiled into brush geo, but also present in players etc.)


### Bounding Volume Trees & Construction / Mapping

BVH2 Construction:
 * Multiple methods; use the split that minimises Surface Area Heuristic
   - Recurse until splits increase Surface Area Heuristic[^SAH]
   - SAH tightly packs dense groups of triangles

> NOTE: Bounding Volume Heirarchy 2 is the same as Binary Space Partitioning
> -- splitting a space in a heirarchy, with each member as a parent of max 2 children.
> -- In the case of `.bsp` files, these nodes are collision volumes, the type of the final children may vary.

Added a limit: node box size increased by half player capsule radius.  
makes tree shallower, saves memory and results in fewer tests (dynamically)

Split methods:
 1)
   * Sort all box centers along each axis
   * try all front/back splits (get SAH of both sides)
   * base strategy
 2)
   * Split big geo from little geo
   * Separate playspace and oob geo (skybox etc)
 3)
   * Grid, split at regular intervals
   * Split big objects on opposite sides of the tree within a large AABB?
   * Tight AABBs for either side
   * Some primitives appear more than once
   * (Not effective / commonly used, Big-Little seems to have performed better)
    
Greedy Top-Down merge BVH2 -> BVH4
 * Sometimes assymetric nodes
   - Tweak the subtree cost function to aim for better use of 4 node system
    
    
The collsion detection uses Divide by 0 Black Magic to catch edge cases. This involves some specificly ordered arguments to Min/Max


### Divide by 0 Black Magic

Test 4 AABBS (SIMD makes testing 4 at once optimal)

```C++
#include <xmmintrin.h>
// unknowns: capsuleSizeonAxis (const Vector); rcpQueryDir (Vector);
// -- earliestHitTime (float);
// this is all performed on 4 AABBs at once
// Find when the AABB around the swept capsule first hits the plane for each node
// AABB face. A point query uses a 0-sized capsule.
// This assumes that decoding the AABB mins/maxs shifted them so the query origin
// is at (0, 0, 0). [standard simplification step]
// "capsuleSizeOnAxis" is precomputed by projecting the capsule on each axis.
// "rcpQueryDir" is also precomputed; this is "1 / D.xyz" using "D", with +0.0f
const __m128 termMinX = (minX - capsuleSizeonAxis.x) * rcpQueryDir.x;  // 2 instructions
const __m128 termMaxX = (maxX + capsuleSizeonAxis.x) * rcpQueryDir.x;
const __m128 termMinY = (minY - capsuleSizeonAxis.y) * rcpQueryDir.y;
const __m128 termMaxY = (maxY + capsuleSizeonAxis.y) * rcpQueryDir.y;
const __m128 termMinZ = (minZ - capsuleSizeonAxis.z) * rcpQueryDir.z;
const __m128 termMaxZ = (maxZ + capsuleSizeonAxis.z) * rcpQueryDir.z;
// Find the enter and leave time for each axis independently.  [Time = lerp(a, b, T)]
// The order of the arguments to Min/Max is crucial for edge cases in SSE!
// NOTE: edge cases are handled incorrectly for HLSL / ARM.
// NOTE: NaN evaluates to False, & Min/Max are ternaries, second arg returns
const __m128 tMinX = Min(termMaxX, termMinX);  // 1 instruction
const __m128 tMaxX = Max(termMinX, termMaxX);
// NOTE: This is robust for SSE, assuming rcpQueryDir can only be +inf, never -inf!
// if termMinX is NaN, termMaxX is +inf, so tMinX =  NaN & tMaxX = +inf
// if termMaxX is NaN, termMinX is -inf, so tMinX = -inf & tMaxX =  NaN
// if the box happends to be flat, tMinX = tMaxX = NaN.
// In all cases, these values are effectively ignored by the min/max chains
// to calculate overall tMin/tMax.  That means we'll always test any
// box if the ray lies in the plane of its face.
const __m128 tMinY = Min(termMaxY, termMinY);
const __m128 tMaxY = Max(termMinY, termMaxY);
// NOTE: This is robust for SSE
const __m128 tMinZ = Min(termMaxZ, termMinZ);
const __m128 tMaxZ = Max(termMinZ, termMaxZ);
// Find the latest time any AABB plane is entered (tMin)
// Find the earliest time and AABB plane is exited (tMax)
// "if we enter before we leave, we hit: keep this box"
// "if we leave before we enter, we missed: ignore this box"
// NOTE: argument order still matters for SSE catching the NaN case.
//  -- this time the order also works for HLSL, but not ARM.
const __m128 tMin = Max(tMinZ, Max(tMinY, Max(tMinX, Simd_LoadZero())));  // 4 instructions
const __m128 tMax = Min(tMaxZ, Min(tMaxY, Min(tMaxX, earliestHitTime)));
const int keepFlags = _mm_movemask_ps(_mm_cplt_ps(tMin, tMax));  // 2 instructions
```

Alternative "Normal" Approach:

```C++
const __m128 tMinX = Min(termMinX, termMaxX);
const __m128 tMaxX = Max(termMinX, termMaxX);
// if termMinX or termMaxX is NaN, then tMinX & box is flattened to one side.
// if termMinX is NaN, termMaxX is +/-inf; tMinX = tMaxX = +/-inf: Cull;
// (HLSL always suppresses NaNs, so this case always goes through)
// if termMaxX is NaN, tMinX = tMaxX = NaN, allow hit if other dimensions hit
// (ARM always passes NaNs like this, then breaks later)
// Technically, this treats the maxs as part of the box and mins as not.
// This can be robust, but requires duplicate geo / padded AABBs.
```

AABB Decode Boilerplate:

```
// using x axis as example
// outside recursive loop
__m128 decodeScale = _mm_set1_ps(bvh->decodeScale);
__m128 relOrgX = _mm_set1_ps(bvh->origin.x - ray->origin.x);
// inside recursive loop
__m128i packedMinMaxX = _mm_load_si128(node->minMax[0]);
__m128i packedMinX = _m_unpacklo_epi16(_mm_setzero_si128(), packedMinMaxX);
__m128i packedMaxX = _m_unpackhi_epi16(_mm_setzero_si128(), packedMinMaxX);
__m128 minX = Simd_Mad(_mm_cvtepi32_ps(packedMinX), decodeScale, relOrgX);
__m128 maxX = Simd_Mad(_mm_cvtepi32_ps(packedMaxX), decodeScale, relOrgX);
```

Explanation:
  * branchless code to find traversal order using bit manipulation & magic numbers
  * keepFlags has buts set for boxes the ray hit
  * want front-to-back order to visit leaves & recurse nodes
  * order info is in `tMin` / `tMax`
  * `tMin` / `tMax` give same order unless one box holds the other
  * `-tMax` visits inner then outer; usually better than `tMin`, visit playable space first.

This method always writes all boxes, but this is OK.
So, how to order the boxes?

Broken "simple" code:

```C++
int index[4] = {0, 1, 2, 3};
int a = 0, b = 1, c = 2, d = 3;
index[a] = (b < a) + (c < a) + (d < a);
index[b] = (a < b) + (c < b) + (d < b);
index[c] = (a < c) + (b < c) + (d < c);
index[d] = (a < d) + (b < d) + (c < d);
// need tiebreaker cases
// orders must be consistent
// a < c: c>b>a   OK
// c < a: c>b>a>c ??
// one test must always be on left, another but always be on right.
index[a] = !(a < b) + !(a < c) + !(a < d);
index[b] =  (a < b) + !(b < c) + !(b < d);
index[c] =  (a < c) +  (b < c) + !(c < d);
index[d] =  (a < d) +  (b < d) +  (c < d);
// if a = b = c = d: index = [3, 2, 1, 0]
// 6 tests, 24 possible solutions
// now with SIMD swizzles...
// need 6 results, get 8
/* 
|   |  5  |  4  |  3  |     |     |  2  |  1  |  0  |
|   | b<d | a<d | a<c | b<b | d<d | c<d | b<c | a<b |
| a |     |  X  |  X  |     |     |     |     |  X  |
| b |  X  |     |     |     |     |     |  X  |  X  |
| c |     |     |  X  |     |     |  X  |  X  |     |
| d |  X  |  X  |     |     |     |  X  |     |     |
*/
// (dcba<ddcb) for 210  &  (baab<ddcb) for 543
// - dcba is unswizzled; index 0 on right
// - d<d & b<b always 0; ddcb used twice (recycle)
// And now in code:
const __m128 t_dcba = tMax;
const __m128 t_ddcb = _mm_shuffle_ps(t_dcba, t_dcba, _MM_SHUFFLE(3, 3, 2, 1));
const __m128 t_baab = _mm_shuffle_ps(t_dcba, t_dcba, _MM_SHUFFLE(1, 0, 0, 1));
const int dd_cd_bc_ab = _mm_movemask_ps(_mm_cmplt_ps(t_dcba, t_ddcb));
const int bd_ad_ac_bb = _mm_movemask_ps(_mm_cmplt_ps(t_baab, t_ddcb));
// Could do "(bd_ad_ac_bb << 4) | dd_cd_bc_ab", leaves 2 0s in the middle
// Instead: "(bd_ad_ac_bb << 2) | dd_cd_bc_ab", get rid of the 0s
// Using multiply add a single x64 "lea" instruction is used.
// This is OK to do because the non-zero bits can't overlap.
const int bd_ad_ac_cd_bc_ab = bd_ad_ac_bb * 4 + dd_cd_bc_ab;
// Now, turn the mask into indices.
// Count bits from current test; each index looks at 3 bits, picked via mask.
// Flip any bits where "b" the test should be negated.
// test for index B is (a < b) + !(b < c) + !(b < d)
// - so ^ 0x22 flips bc & bd
const int index_a = _mm_popcnt_u32((~bd_ad_ac_cd_bc_ab       ) & 0x19);
const int index_b = _mm_popcnt_u32(( bd_ad_ac_cd_bc_ab ^ 0x22) & 0x23);
const int index_c = _mm_popcnt_u32(( bd_ad_ac_cd_bc_ab ^ 0x04) & 0x0E);
const int index_d = _mm_popcnt_u32(( bd_ad_ac_cd_bc_ab       ) & 0x34);
// now limit to boxes that pass (force fails to +inf, always sorted last.
// all kept boxes forced to front this way
// culled order is borked, but OK since ignored.
```

```C++
// Modify tMax calculation above to get unclamped max time,
// order of boxes which end outside the current query range will be OK
const __m128 tMaxRaw = Min(tMaxZ, Min(tMaxY, Min(tMaxX, g_simd_inf)));
const __m128 tMax = Min(tMaxRaw, earliestHitTime);
// Split keepflags to remember mask kept in SSE register
const __m128 maskKept = _mm_cmplt_ps(tMin, tMax);
const int keepFlags = _mm_movemask_ps(maskKept);
// Modify t_dcba init to force culled boxes to +inf
const __m128 t_dcba = _mm_blendv_ps(g_simd_inf, tMaxRaw, maskKept);
```

Now must limit by node type (node / leaf); parallel tests in integer registers (`isNode`/`isLeaf`)  
Modify 6-bit compare masks as if `tMax` set to `+inf`
`a<b forced to 0 if a == +inf, else 1 if b == +inf`

Algorithm: (order matters)

```
- set   bits in mask where 2nd argument should be +inf
- clear bits in mask where 1st argument should be +inf

|        |               CLEAR               |                SET                |     |
|        |        BYTE 0         |        BYTE 1         |        BYTE 2         |     |
|        |  5  |  4  |  3  |  2  |  1  |  0  |  5  |  4  |  3  |  2  |  1  |  0  | HEX |
|        | b<d | a<d | a<c | c<d | b<c | a<b | b<d | a<d | a<c | c<d | b<c | a<b |     |
| a=+inf |     |  X  |  X  |     |     |  X  |     |     |     |     |     |     | 640 |
| b=+inf |  X  |     |     |     |  X  |     |     |     |     |     |     |  X  | 881 |
| c=+inf |     |     |     |  X  |     |     |     |     |  X  |     |  X  |     | 10A |
| d=+inf |     |     |     |     |     |     |  X  |  X  |     |  X  |     |     | 034 |
```

This exploits patterns in the data:
 1) Each bit appears only once
 2) Inverting inputs inverts outputs
 3) Inverted inputs are more convenient

> NOTE: `is a node / leaf` rather than `not a node / leaf`
> NOTE: `(mask | ~set) & clear` rather than `(mask | set) & ~clear`

get masks from 4 bit child type
* "childType - 1" underflows if and only if childType == 0 (BVH Node)
* underflow makes upper 28 bits set
* no underflow leaves upper 28 bits clear
* C++ standard defines this behaviour (if unsigned)

a 28-bit isNode mask has been made
* bitwise AND with hex constant for each box (see above table)
* - + a bit for "this box index is a node"
* bitwise OR these constants together
* separate into parts at end

```C++
const u32 nodeBits0 = (childType0 - 1u) & 0x64010;
const u32 nodeBits1 = (childType1 - 1u) & 0x88120;
const u32 nodeBits2 = (childType2 - 1u) & 0x10A40;
const u32 nodeBits3 = (childType3 - 1u) & 0x03480;
const u32 nodeBits = (nodeBits0 | nodeBits1 | nodeBits2 | nodeBits3) >> 4;
const u32 isKeptNode = nodeBits & keepFlags;  // only 4 lowest bits matter
const u32 bd_ad_ac_cd_bc_ab = bd_ad_ac_bb * 4 + dd_cd_bc_ab;
const u32 bd_ad_ac_cd_bc_ab_nodes =  // (mask | ~set) & clear;
         (bd_ad_ac_cd_bc_ab | (~nodeBits >> 4)) & (nodeBits >> 10);
```

Then get destination indices as before, but with modified node mask. Leaf mask code is the same, but `(1u - childTypeN)` to decode

> TODO: FIFO order code
> TODO: Fast path code
> TODO: triangle collision ...

`*** END OF TRANSCRIPT ***`



## using `supported/titanfall.md` & "coverage"

> TODO: explain what is listed & how coverage is calculated


## `.bsp` Lumps

from `bsp_tool/branches/respawn/titanfall2.py`

> TODO: explain `branch_script` layout  
> TODO: database normalisation / optimisation  
> TODO: `.bsp` design patterns  
> TODO: byte-alignment, padding & SIMD registers


### Known lump changes from Titanfall -> Titanfall 2:

New:
```
UNUSED_4 -> LIGHTPROBE_PARENT_INFOS
UNUSED_5 -> SHADOW_ENVIRONMENTS
UNUSED_6 -> LIGHTPROBE_BSP_NODES
UNUSED_7 -> LIGHTPROBE_BSP_REF_IDS
UNUSED_55 -> WORLD_LIGHT_PARENT_INFOS
UNUSED_122 -> LIGHTMAP_DATA_RTL_PAGE
```

Deprecated:
```
LEAF_WATER_DATA
PHYSICS_LEVEL
PHYSICS_TRIANGLES
```


### Rough map of the relationships between lumps:

> NOTE: parallel means each entry is paired with an entry of the same index in the parallel lump
> -- this means you can collect only the data you need, but increases the chance of storing redundant data

```
             /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
            \--> .flags (VertexReservedX)     \--> VertexNormal
             \-> VertexReservedX               \-> .uv

MeshBounds & Mesh are parallel

ShadowEnvironment -> ShadowMesh -> ShadowMeshIndices -> ShadowMeshOpaqueVertex
                                                   \-?> ShadowMeshAlphaVertex

LightmapHeader -> LIGHTMAP_DATA_SKY
              \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

PORTAL LUMPS:
Portal -?> PortalEdge -> PortalVertex
PortalEdgeRef -> PortalEdge
PortalVertRef -> PortalVertex
PortalEdgeIntersect -> PortalEdge?
                   \-> PortalVertex

PortalEdgeIntersectHeader -> ???
PortalEdgeIntersectHeader is parallel w/ PortalEdge
NOTE: titanfall 2 only seems to care about PortalEdgeIntersectHeader & ignores all other lumps
-- though this is a code branch that seems to be triggered by something about r1 maps, maybe a flags lump?
NOTE: there are also always as many vert refs as edge refs
PortalEdgeRef is parallel w/ PortalVertRef (both 2 bytes per entry, so not 2 verts per edge?)

??? WorldLight <-?-> WorldLightParentInfo -?> Model

CM_* LUMPS:
the entire GM_GRID lump is always 28 bytes (SpecialLumpClass? flags & world bounds?)

Cell -?> Primitive | PrimitiveBounds
    \-?> GeoSet | GeoSetBounds

Brush -> BrushSidePlane -> Plane
     \-> BrushSideProperties | BrushSideTextureVector

BrushSideProps is parallel w/ BrushTexVecs
Primitives is parallel w/ PrimitiveBounds
GeoSets is parallel w/ GeoSetBounds
PrimitiveBounds & GeoSetBounds use the same type (loaded w/ the same function in engine.dll)
```
> TODO: `TRICOLL_*` LUMPS



## References

[^Lee]: Steve Lee on Youtube: [Why Making Titanfall was Hard - interview with 2 design leads at Respawn](https://www.youtube.com/watch?v=ZT9yVUDDUJg)
[^VDC]: Valve Developer Community: [BSP File Format](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format)
[^VDC_Titanfall]: Valve Developer Community: [Titanfall BSP](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall)
[^Cra0]: Cra0kalo: [Titanfall BSPInspect](https://dev.cra0kalo.com/?p=202)
[^Warmist]: warmist on GitHub [titanfallMapExporter](https://github.com/warmist/titanfallMapExporter/blob/master/titanfallMapExporter.py)
[^SAH]: [Surface Area Heuristic](https://medium.com/@bromanz/how-to-create-awesome-accelerators-the-surface-area-heuristic-e14b5dec6160)
