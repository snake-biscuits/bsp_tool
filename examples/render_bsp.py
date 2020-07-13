import colorsys
import ctypes
import itertools
import math
import time
import struct
import sys

import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import *
from sdl2 import *

from utils import camera
from utils import vector
sys.path.insert(0, "../")
import bsp_tool


camera.sensitivity = 2

# TODO: select shaders and triangulation mode from bsp version & mod
def main(width, height, bsp):
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(bytes(bsp.filename, "utf-8"), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, SDL_WINDOW_OPENGL) #| SDL_WINDOW_BORDERLESS) #SDL_WINDOW_FULLSCREEN
    glContext = SDL_GL_CreateContext(window)
    # GL SETUP
    glClearColor(.5, .5, .5, 0)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glFrontFace(GL_CW)
    glPointSize(4)
    glPolygonMode(GL_BACK, GL_LINE)
    gluPerspective(120, width / height, 0.1, 1000000)
    # BSP => VRAM TRIANGLES
    conversion_start = time.time()
    # v20 (Team Fortress 2) FACES => GEOMETRY
##    all_faces = []
##    all_faces_map = [] # [(start, length), ...]
##    start = 0
##    for face in bsp.FACES:
##        if face.disp_info == -1:
##            f_verts = verts_of(bsp, face) # add to vertex buffer here and fan the indices
##            out = f_verts[:3]
##            f_verts = f_verts[3:]
##            for vert in f_verts:
##                out += [out[0], out[-1], vert]
##            f_verts = out
##            f_verts_len = len(f_verts)
##            all_faces_map.append((start, f_verts_len))
##            start += f_verts_len
##        else: # face is a displacement
##            power = bsp.DISP_INFO[face.disp_info].power
##            f_verts = dispverts_of(bsp, face)
##            f_verts = disp_tris(f_verts, power)
##            f_verts_len = len(f_verts)
##            all_faces_map.append((start, f_verts_len))
##            start += f_verts_len
##        all_faces += f_verts
##    vertices = list(itertools.chain(*itertools.chain(*all_faces)))
##    indices = range(len(vertices))

    # v37 (Titanfall 2) MESHES => GEOMETRY
##    ignore_keywords = ["tools\\",
##                       "world\\atmo",
##                       "world\\dev\\edge_detect",
##                       "decal"]
##    vertices = list(itertools.chain(*bsp.VERTICES))
##    indices = []
##    for i, mesh in enumerate(bsp.MESHES):
##        material = bsp.MATERIAL_SORT[mesh.material_sort]
##        texdata = bsp.TEXDATA[material.texdata]
##        texture_name = bsp.TEXDATA_STRING_DATA[texdata.string_table_index]
##        if any([w in texture_name.lower() for w in ignore_keywords]):
##            # filtering with regex would be neat
##            continue # skip this mesh
##        mesh_vertices = bsp_tool.titanfall2.tris_of(bsp, i)
##        # stitch positions, normals & uvs together into a proper vertex format
##        indices.append([v.position_index for v in mesh_vertices])
##    indices = list(itertools.chain(*indices))

    # v47 (Apex Legends) MESHES => GEOMETRY
    vertices = []
    indices = []
    print(f"Converting {len(bsp.MESHES)} meshes")
    for mesh_index in range(len(bsp.MESHES)):
        for vertex in bsp_tool.apex_legends.tris_of(bsp, mesh_index):
            position = bsp.VERTICES[vertex.position_index]
            normal = bsp.VERTEX_NORMALS[vertex.normal_index]
            uv = vertex.uv
            vertex_data = (*position, *normal, *uv)
##            if vertex_data not in indices:
            vertices.append(vertex_data)
            indices.append(len(indices))
##            else:
##                indices.append(indices.index(vertex_data))
    vertices = list(itertools.chain(*vertices))

    conversion_end = time.time()
    print(bsp.filename.upper(), end=" ")
    print(f"{bsp.bytesize // 1024:,}KB BSP", end=" >>> ")
    print(f"{len(vertices) // 9:,} TRIS", end=" & ")
    print(f"{(len(vertices) * 4) // 1024:,}KB VRAM")
    print(f"Converted to geometry in {(conversion_end - conversion_start) * 1000:,.3f}ms")

    VERTEX_BUFFER, INDEX_BUFFER = glGenBuffers(2)
    # VERTICES
    glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)
    # INDICES
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 4, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW)

    # SHADER SELECTION
    shader_folder = "shaders/"
    render_mode = "flat"
    major, minor = glGetIntegerv(GL_MAJOR_VERSION), glGetIntegerv(GL_MINOR_VERSION)
    print(f"OpenGL Version {major}.{minor}")
    if major >= 4: # Assuming GLSL 450
        USING_ES = False
        shader_folder += "450_CORE"    
    elif major == 3: # if GLSL 450 not supported, use GLES 300
        USING_ES = True
        shader_folder += "300_ES"
    else:
        raise NotImplementedError("GLSL Version ({major, minor}) is unsupported (too low)!")

    # SHADER COMPILATION
    compile_shader = lambda filename, shader_type: compileShader(open(filename, "rb"), shader_type)
    # brush_shader
    vert_shader = compile_shader(f"{shader_folder}/brush.v", GL_VERTEX_SHADER)
    frag_shader = compile_shader(f"{shader_folder}/brush_{render_mode}.f", GL_FRAGMENT_SHADER)
    brush_shader = compileProgram(vert_shader, frag_shader)
    glLinkProgram(brush_shader)
    # mesh_shader (rBSP: TitanFall2 & Apex Legends)
    vert_shader = compile_shader(f"{shader_folder}/mesh.v", GL_VERTEX_SHADER)
    frag_shader = compile_shader(f"{shader_folder}/mesh_{render_mode}.f", GL_FRAGMENT_SHADER)
    mesh_shader = compileProgram(vert_shader, frag_shader)
    glLinkProgram(mesh_shader)
    # debug_mesh_shader
    vert_shader = compile_shader(f"{shader_folder}/mesh_debug.v", GL_VERTEX_SHADER)
    frag_shader = compile_shader(f"{shader_folder}/mesh_debug.f", GL_FRAGMENT_SHADER)
    debug_mesh_shader = compileProgram(vert_shader, frag_shader)
    glLinkProgram(debug_mesh_shader)
    del vert_shader, frag_shader
    
    # SHADER VERTEX FORMAT
    # BSP FACES
    glEnableVertexAttribArray(0) # vertexPosition
    glEnableVertexAttribArray(1) # vertexNormal
    glEnableVertexAttribArray(2) # vertexTexcoord
    glEnableVertexAttribArray(3) # vertexLightmapCoord
    glEnableVertexAttribArray(4) # reflectivityColour
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 52, GLvoidp(0))
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_TRUE,  52, GLvoidp(12))
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 52, GLvoidp(24))
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 52, GLvoidp(32))
    glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 52, GLvoidp(40))
    # rBSP MESHES
    glEnableVertexAttribArray(5) # vertexPosition
    glEnableVertexAttribArray(6) # vertexNormal
    glEnableVertexAttribArray(7) # vertexTexCoord
    glVertexAttribPointer(5, 3, GL_FLOAT, GL_FALSE, 32, GLvoidp(0))
    glVertexAttribPointer(6, 3, GL_FLOAT, GL_TRUE,  32, GLvoidp(12))
    glVertexAttribPointer(7, 2, GL_FLOAT, GL_FALSE, 32, GLvoidp(24))

    # SHADER UNIFORMS
    if USING_ES:
        glUseProgram(brush_shader)
        attrib_position = glGetAttribLocation(brush_shader, "vertexPosition")
        attrib_normal = glGetAttribLocation(brush_shader, "vertexNormal")
        attrib_texture_uv = glGetAttribLocation(brush_shader, "vertexTexCoord")
        attrib_lightmap_uv = glGetAttribLocation(brush_shader, "vertexLightCoord")
        attrib_colour_uv = glGetAttribLocation(brush_shader, "vertexColour")
        glUseProgram(0)

    # INPUT STATE
    keys = []
    mousepos = vector.vec2()
    view_init = vector.vec3(0, 0, 32), None, 128
    VIEW_CAMERA = camera.freecam(*view_init)

    # SDL EVENT STATE
    event = SDL_Event()
    SDL_GL_SetSwapInterval(0)
    SDL_CaptureMouse(SDL_TRUE)
    SDL_SetRelativeMouseMode(SDL_TRUE)
    SDL_SetWindowGrab(window, SDL_TRUE)
    SDL_WarpMouseInWindow(window, width // 2, height // 2)

    end_of_previous_tick = time.time()
    tickrate = 120
    while True:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT or event.key.keysym.sym == SDLK_ESCAPE and event.type == SDL_KEYDOWN:
                SDL_GL_DeleteContext(glContext)
                SDL_DestroyWindow(window)
                return SDL_Quit()
            if event.type == SDL_KEYDOWN:
                if event.key.keysym.sym not in keys:
                    keys.append(event.key.keysym.sym)
            if event.type == SDL_KEYUP:
                while event.key.keysym.sym in keys:
                    keys.remove(event.key.keysym.sym)
            if event.type == SDL_MOUSEBUTTONDOWN:
                if event.button.button not in keys:
                    keys.append(event.button.button)
            if event.type == SDL_MOUSEBUTTONUP:
                while event.button.button in keys:
                    keys.remove(event.button.button)
            if event.type == SDL_MOUSEMOTION:
                mousepos += vector.vec2(event.motion.xrel, event.motion.yrel)
                SDL_WarpMouseInWindow(window, width // 2, height // 2)
            if event.type == SDL_MOUSEWHEEL:
                VIEW_CAMERA.speed += event.wheel.y * 32

        dt = time.time() - end_of_previous_tick
        while dt >= 1 / tickrate:
            # TICK START
            VIEW_CAMERA.update(mousepos, keys, 1 / tickrate)
            if SDLK_BACKQUOTE in keys: # ~: debug print
                print(VIEW_CAMERA)
                while SDLK_BACKQUOTE in keys: # print once until pressed again
                    keys.remove(SDLK_BACKQUOTE)
            if SDLK_r in keys: # R: reset camera
                VIEW_CAMERA = camera.freecam(*view_init)
            if SDLK_LSHIFT in keys: # LShift: Increase camera speed
                VIEW_CAMERA.speed += 5
            if SDLK_LCTRL in keys: # LCtrl: reduce camera speed
                VIEW_CAMERA.speed -= 5
            # TICK END
            dt -= 1 / tickrate
            end_of_previous_tick = time.time()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        VIEW_CAMERA.set()
        glUseProgram(debug_mesh_shader)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, GLvoidp(0))
        glUseProgram(0)
        glBegin(GL_LINES)
        glColor(1, 0, 0)
        glVertex(0, 0, 0)
        glVertex(128, 0, 0)
        glColor(0, 1, 0)
        glVertex(0, 0, 0)
        glVertex(0, 128, 0)
        glColor(0, 0, 1)
        glVertex(0, 0, 0)
        glVertex(0, 0, 128)
        glEnd()
        glPopMatrix()
        SDL_GL_SwapWindow(window)

def verts_of(bsp, face):
    """Format: [Position, Normal, TexCoord, LightCoord, Colour]"""
    verts, uvs, uv2s = [], [], []
    first_edge = face.first_edge
    for surfedge in bsp.SURFEDGES[first_edge:first_edge + face.num_edges]:
        edge = bsp.EDGES[surfedge] if surfedge >= 0 else bsp.EDGES[-surfedge][::-1] # ?
        verts.append(bsp.VERTICES[edge[0]])
        verts.append(bsp.VERTICES[edge[1]])
    verts = verts[::2] # edges likely aren't this simple
    # github.com/VSES/SourceEngine2007/blob/master/src_main/engine/matsys_interface.cpp
    # SurfComputeTextureCoordinate & SurfComputeLightmapCoordinate
    tex_info = bsp.TEXINFO[face.tex_info] # index error?
    tex_data = bsp.TEXDATA[tex_info.tex_data]
    texture = tex_info.texture
    lightmap = tex_info.lightmap
    normal = lambda P: (P.x, P.y, P.z) # return the normal of plane (P)
    for vert in verts:
        uv = [vector.dot(vert, normal(texture.s)) + texture.s.offset,
              vector.dot(vert, normal(texture.t)) + texture.t.offset]
        uv[0] /= tex_data.view_width if tex_data.view_width != 0 else 1
        uv[1] /= tex_data.view_height if tex_data.view_height != 0 else 1
        uvs.append(vector.vec2(*uv))
        uv2 = [vector.dot(vert, normal(lightmap.s)) + lightmap.s.offset,
               vector.dot(vert, normal(lightmap.t)) + lightmap.t.offset]
        uv2[0] -= face.lightmap_texture_mins_in_luxels.s
        uv2[1] -= face.lightmap_texture_mins_in_luxels.t
        try:
            uv2[0] /= face.lightmap_texture_size_in_luxels.s
            uv2[1] /= face.lightmap_texture_size_in_luxels.t
        except ZeroDivisionError:
            uv2 = [0, 0]
        uv2s.append(uv2)
    vert_count = len(verts)
    normal = [bsp.PLANES[face.plane_num].normal] * vert_count # X Y Z
    colour = [tex_data.reflectivity] * vert_count # R G B
    return list(zip(verts, normal, uvs, uv2s, colour))

def dispverts_of(bsp, face): # add format argument (lightmap uv, 2 uvs, etc)
    """vertex format [Position, Normal, TexCoord, LightCoord, Colour]
    normal is inherited from face
    returns rows, not tris"""
    verts = verts_of(bsp, face)
    if face.disp_info == -1:
        raise RuntimeError("face is not a displacement!")
    if len(verts) != 4:
        raise RuntimeError("face does not have 4 corners (probably t-junctions)")
    disp_info = bsp.DISP_INFO[face.disp_info]
    start = list(disp_info.start_position)
    start = [round(x, 1) for x in start] # approximate match
    round_verts = []
    for vert in [v[0] for v in verts]:
        round_verts.append([round(x, 1) for x in vert])
    if start in round_verts: # "rotate"
        index = round_verts.index(start)
        verts = verts[index:] + verts[:index]
    A, B, C, D = [vector.vec3(*v[0]) for v in verts]
    Auv, Buv, Cuv, Duv = [vector.vec2(*v[2]) for v in verts]
    Auv2, Buv2, Cuv2, Duv2 = [vector.vec2(*v[3]) for v in verts] # scale is wrong
    AD = D - A
    ADuv = Duv - Auv
    ADuv2 = Duv2 - Auv2
    BC = C - B
    BCuv = Cuv - Buv
    BCuv2 = Cuv2 - Buv2
    power2 = 2 ** disp_info.power
    full_power = (power2 + 1) ** 2
    start = disp_info.disp_vert_start
    stop = disp_info.disp_vert_start + full_power
    new_verts, uvs, uv2s = [], [], []
    for index, disp_vert in enumerate(bsp.DISP_VERTS[start:stop]):
        t1 = index % (power2 + 1) / power2
        t2 = index // (power2 + 1) / power2
        bary_vert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
        disp_vert = [x * disp_vert.distance for x in disp_vert.vector]
        new_verts.append([a + b for a, b in zip(bary_vert, disp_vert)])
        uvs.append(vector.lerp(Auv + (ADuv * t1), Buv + (BCuv * t1), t2))
        uv2s.append(vector.lerp(Auv2 + (ADuv2 * t1), Buv2 + (BCuv2 * t1), t2))
    normal = [verts[0][1]] * full_power
    colour = [verts[0][4]] * full_power
    verts = list(zip(new_verts, normal, uvs, uv2s, colour))
    return verts

def disp_tris(verts, power):
    """takes flat array of verts and arranges them in a patterned triangle grid
    expects verts to be an array of length ((2 ** power) + 1) ** 2"""
    power2 = 2 ** power
    power2A = power2 + 1
    power2B = power2 + 2
    power2C = power2 + 3
    tris = []
    for line in range(power2):
        line_offset = power2A * line
        for block in range(2 ** (power - 1)):
            offset = line_offset + 2 * block
            if line % 2 == 0: # |\|/|
                tris.append(verts[offset + 0])
                tris.append(verts[offset + power2A])
                tris.append(verts[offset + 1])
                tris.append(verts[offset + power2A])
                tris.append(verts[offset + power2B])
                tris.append(verts[offset + 1])
                tris.append(verts[offset + power2B])
                tris.append(verts[offset + power2C])
                tris.append(verts[offset + 1])
                tris.append(verts[offset + power2C])
                tris.append(verts[offset + 2])
                tris.append(verts[offset + 1])
            else: #|/|\|
                tris.append(verts[offset + 0])
                tris.append(verts[offset + power2A])
                tris.append(verts[offset + power2B])
                tris.append(verts[offset + 1])
                tris.append(verts[offset + 0])
                tris.append(verts[offset + power2B])
                tris.append(verts[offset + 2])
                tris.append(verts[offset + 1])
                tris.append(verts[offset + power2B])
                tris.append(verts[offset + power2C])
                tris.append(verts[offset + 2])
                tris.append(verts[offset + power2B])
    return tris


if __name__ == "__main__":
    width, height = 1280, 720

##    mod = bsp_tool.team_fortress2
##    folder = "D:/SteamLibrary/steamapps/common/Team Fortress 2/tf/maps/"
####    filename = "cp_cloak.bsp"
##    folder, filename = "../maps/", "pl_upward.bsp"

##    bsp = bsp_tool.bsp(folder + filename, mod)

##    mod = bsp_tool.titanfall2
##    folder = "E:/Mod/Titanfall2/"
####    mapname = "mp_colony02"
####    mapname = "mp_crashsite3"
##    mapname = "mp_drydock"
####    mapname = "mp_glitch"
####    mapname = "mp_lf_uma"
####    mapname = "mp_relic02"
##    filename = f"{mapname}/maps/{mapname}.bsp"

    mod = bsp_tool.apex_legends
    folder = "E:/Mod/ApexLegends/maps/"
##    filename = "mp_rr_canyonlands_staging.bsp"
##    filename = "mp_rr_canyonlands_mu1_night.bsp"
    filename = "mp_rr_canyonlands_mu2.bsp"
    
    bsp = bsp_tool.bsp(folder + filename, mod, lump_files=True)

    try:
        main(1280, 720, bsp)
    except Exception as exc:
        SDL_Quit()
        raise exc
