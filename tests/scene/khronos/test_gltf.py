from bsp_tool.scene import khronos
from bsp_tool.utils import physics
# from bsp_tool.utils import quaternion
from bsp_tool.utils import vector


def test_cube():
    # test cube
    aabb = physics.AABB.from_mins_maxs(
        vector.vec3(-1, -1, -1),
        vector.vec3(+1, +1, +1))
    cube_model = aabb.as_model()
    # w/ rotation
    cube_model.angles.z = 45

    cube = khronos.Gltf.from_models({
        "cube": cube_model})

    assert cube.models == {"cube": cube_model}

    assert len(cube.json.keys()) > 0
    # TODO: verify json
    # -- base json
    # -- all model entries
    # -- all material entries
    # -- all buffers
    # -- all accessors
    # -- all primitives
    # -- angles quaternion

    # TODO: using glTF spec
    # -- Y+ Up
    # -- ?inverted? polygon winding order

    assert len(cube.buffers) > 0
    # TODO: verify buffers
    # -- vertex buffer
    # -- index buffer
