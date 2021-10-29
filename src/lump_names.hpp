#pragma once


namespace bsp_tool {
    namespace id_software::quake3 {
        char lump_names[17][64] = {"Entities", "Textures", "Planes", "Nodes", "Leaves",
                                   "LeafFaces", "LeafBrushes", "Models", "Brushes",
                                   "BrushSides", "Vertices", "MeshVertices", "Effects",
                                   "Faces", "Lightmaps", "LightVolumes", "Visibility"};
    }
    namespace valve_software::source {
        char lump_names[64][64] = {"Entities", "Planes", "TextureData", "Vertices", "Visibility",
                                   "Nodes", "TexInfo", "Faces", "Lighting", "Occlusion",
                                   "Leaves", "FaceIDs", "Edges", "SurfEdges", "Models",
                                   "WorldLights", "LeafFaces", "LeafBrushes", "Brushes",
                                   "BrushSides", "Areas", "AreaPortals", "Unused22", "Unused23",
                                   "Unused24", "Unused25", "DisplacementInfo", "OriginalFaces",
                                   "PhysicsDisplacement", "PhysicsCollide", "VertexNormals",
                                   "VertexNormalIndices", "DisplacementLightmapAlphas",
                                   "DisplacementVertices", "DisplacementLightmapSamplePosition",
                                   "GameLump", "LeafWaterData", "Primitives", "PrimitiveVertices",
                                   "PrimitiveIndices", "PakFile", "ClipPortalVertices", "Cubemaps",
                                   "TextureDataStringData", "TextureDataStringTable", "Overlays",
                                   "LeafMinDistToWater", "FaceMacroTextureInfo", "DisplacementTriangles",
                                   "PhysicsCollideSurface", "WaterOverlays", "LeafAmbientIndexHDR",
                                   "LeafAmbientIndex", "LightingHDR", "WorldLightsHDR",
                                   "LeafAmbientLightingHDR", "LeafAmbientLighting", "XZipPakFile",
                                   "FacesHDR", "MapFlags", "OverlayFades", "Unused61", "Unused62", "Unused63"};
    }
    namespace respawn_entertainment::titanfall {
        char lump_names[128][64] = {"Entities", "Planes", "TextureData", "Vertices", "Unused04", "Unused05",
                                    "Unused06", "Unused07", "Unused08", "Unused09", "Unused10", "Unused11",
                                    "Unused12", "Unused13", "Models", "Unused15", "Unused16", "Unused17",
                                    "Unused18", "Unused19", "Unused20", "Unused21", "Unused22", "Unused23",
                                    "EntityPartitions", "Unused25", "Unused26", "Unused27", "Unused28",
                                    "PhysicsCollide", "VertexNormals", "Unused31", "Unused32", "Unused33",
                                    "Unused34", "GameLump", "LeafWaterData", "Unused37", "Unused38", "Unused39",
                                    "PakFile", "Unused41", "Cubemaps", "TextureDataStringData", "TextureDataStringTable",
                                    "Unused45", "Unused46", "Unused47", "Unused48", "Unused49", "Unused50",
                                    "Unused51", "Unused52", "Unused53", "WorldLights", "WorldLightParentInfo",
                                    "Unused56", "Unused57", "Unused58", "Unused59", "Unused60", "Unused61",
                                    "PhysicsLevel", "Unused63", "Unused64", "Unused65", "TriCollTris",
                                    "Unused67", "TriCollNodes", "TriCollHeaders", "PhysTris", "VertsUnlit",
                                    "VertsLitFlat", "VertsLitBump", "VertsUnlitTS", "VertsReserved4",
                                    "VertsReserved5", "VertsReserved6", "VertsReserved7", "MeshIndices",
                                    "Meshes", "MeshBounds", "MaterialSort", "LightmapHeaders",
                                    "LightmapDataDXT5", "CMGrid", "CMGridCells", "CMGeoSets", "CMGeoSetBounds",
                                    "CMPrimitives", "CMPrimitiveBounds", "CMUniqueContents", "CMBrushes",
                                    "CMBrushSidePlaneOffsets", "CMBrushSideProps", "CMBrushTexVecs",
                                    "TriCollBevelStarts", "TriCollBevelIndices", "LightmapDataSky",
                                    "CSMAABBNodes", "CSMObjRefs", "LightProbes", "StaticPropLightProbeIndex",
                                    "LightProbeTree", "LightProbeRefs", "LightmapDataRealTimeLights",
                                    "CellBspNodes", "Cells", "Portals", "PortalVerts", "PortalEdges",
                                    "PortalVertEdges", "PortalVertRefs", "PortalEdgeRefs", "PortalEdgeIsectEdge",
                                    "PortalEdgeIsectAtVert", "PortalEdgeIsectHeader", "OcclusionMeshVerts",
                                    "OcclusionMeshIndices", "CellAABBNodes", "ObjRefs", "ObjRefBounds",
                                    "LightmapDataRealTimeLightPage", "LevelInfo", "ShadowMeshOpaqueVerts",
                                    "ShadowMeshAlphaVerts", "ShadowMeshIndices", "ShadowMeshMeshes"};
    }
}

