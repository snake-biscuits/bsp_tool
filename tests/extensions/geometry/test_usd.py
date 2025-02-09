from bsp_tool.extensions.geometry import usd
from bsp_tool.utils import physics
from bsp_tool.utils import vector


def test_cube():
    aabb = physics.AABB.from_mins_maxs(
        vector.vec3(-1, -1, -1),
        vector.vec3(+1, +1, +1))
    cube_model = aabb.as_model()
    cube_model.angles.z = 45
    cube = usd.Usd.from_models({"cube": cube_model})

    lines = list(cube.lines())
    assert len(lines) != 0
    # TODO: assert lines look like a .usda w/ the intended layout
    # top-level metadata
    assert lines[0] == "#usda 1.0"
    assert lines[1] == "("
    assert lines[2] == '    defaultPrim = "root"'
    assert lines[3] == f"    metersPerUnit = {cube.meters_per_unit}"
    assert lines[4] == '    upAxis = "Z"'
    assert lines[5] == ")"
    assert lines[6] == ""
    # root Xform
    assert lines[7] == 'def Xform "root" ('
    assert lines[8] == ")"
    assert lines[9] == "{"
    # model metadata
    assert lines[10] == '    def Xform "cube"'
    assert lines[11] == "    {"
    assert lines[12] == f"        float3 xformOp:rotateXYZ = {tuple(cube_model.angles)}"
    assert lines[13] == f"        float3 xformOp:scale = {tuple(cube_model.scale)}"
    assert lines[14] == f"        double3 xformOp:translate = {tuple(cube_model.origin)}"
    operation_order = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
    assert lines[15] == f"        uniform token[] xformOpOrder = {operation_order}"
    assert lines[16] == ""
    # TODO:
    # -- Mesh
    # -- vertex data (positions, normals & uvs)
    # -- polygon indices & counts
    # -- mesh subsets (MaterialBindingAPI)
    # -- materials
