from collections import namedtuple
import itertools
import os
from typing import Any, Dict, List, Set

import numpy as np
import OpenGL.GL as gl
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GLU import gluPerspective


shader_folder = os.path.join(os.path.dirname(__file__), "shaders")

Renderable = namedtuple("Renderable", ["name", "shader", "vertices", "indices"])
# ^ name: str, shader: str, vertices: List[List[float]], indices: List[int]
StoredRenderable = namedtuple("StoredRenderable", ["name", "vertex_span", "index_span"])
# ^ name: str, vertex_span: (int, int), index_span: (int, int)
# shader uniform settings for each renderable?
Update = namedtuple("Update", ["vertices_start", "vertices", "indices_start", "indices"])
# ^ vertices_start: int, vertices: List[List[float]], indices_start: int, indices: List[int]

attrib_types = {"vec2": (2 * 4, gl.GL_FLOAT),
                "vec3": (3 * 4, gl.GL_FLOAT),
                "vec4": (4 * 4, gl.GL_FLOAT),
                "mat4": (4 * 4 * 4, gl.GL_FLOAT)}
# ^ {"glsl_type": (size, GL_TYPE)}

uniform_setter = {"vec2": lambda uniform_loc, value: gl.glUniform2f(uniform_loc, *value),
                  "vec3": lambda uniform_loc, value: gl.glUniform3f(uniform_loc, *value),
                  "vec4": lambda uniform_loc, value: gl.glUniform4f(uniform_loc, *value),
                  "mat4": lambda uniform_loc, value: gl.glUniformMatrix4fv(uniform_loc, 1, gl.GL_FALSE, value)}
# ^ {"glsl_type": setter_lambda(uniform_location, value)}


class Manager:
    hidden: Set[Renderable]
    renderables: Dict[str, Set[StoredRenderable]]
    # ^ {"shader": {StoredRenderable}}
    shaders: Dict[str, Dict[str, int]]
    # ^ {"vertex_shader": {"fragment_shader", id}}
    # vertex shaders are matched to renderables' vertex formats
    # fragment shaders allow for a range of "render modes" (flat, textured, unlit, BRDF...)
    # NOTE: some shaders do texture sampling etc. at the vertex level
    # this can be handy for performance (good for LoDs)
    # TODO: a way of tagging LoD shader changes for renderables based on a distance
    uniforms: Dict[str, Dict[Any, int]]  # where "Any" is (str, str)
    # ^ {"shader_program": {("uniform_name", "glsl_type"): id}}
    # uniforms are matched to shader file
    update_queue: List[Update]
    vertex_formats: Dict[str, List[Any]]  # where "Any" is (str, str)
    # ^ {"vertex_shader": [("attribute", "glsl_type")]}

    # TODO: mapping matching uniforms to update methods
    # maybe some system for constant values vs queued uniform updates
    # also interpolating between updates as a flag?
    # TODO: matching some uniform values to renderables (uniform buffer?)
    # TODO: instance rendered renderables with positions etc in uniform buffer

    def __init__(self, size=256*10**6):  # size is in bytes (default 256MB)
        self.buffer_size = size
        self.renderables = dict()
        self.buffer_update_queue = list()

        vertex_shaders, fragment_shaders = dict(), dict()
        # ^ {"shader_filename": """shader_text"""}
        global shader_folder
        for shader_file in os.listdir(shader_folder):
            with open(os.path.join(shader_folder, shader_file)) as shader_text:
                if shader_file.endswith(".vert"):
                    vertex_shaders[shader_file] = shader_text.read()
                elif shader_file.endswith(".frag"):
                    fragment_shaders[shader_file] = shader_text.read()

        for vertex_shader_name, vertex_shader_text in vertex_shaders.items():
            uniforms, layouts = dict(), dict()
            # ^ {"uniform": }, {("attrib", glsl_type): location}
            for line in vertex_shader_text.split(";"):
                line = line.split()
                if line[0] == "uniform":
                    # "uniform", ~precision, glsl_type, uniform
                    glsl_type, uniform = line[-2], line[-1]
                    uniforms[uniform] = glsl_type
                elif line[0] == "layout(location":
                    # "layout(location", "=", location + ")", "in", ~precision, glsl_type, attribute
                    location = int(line[2][:-1])
                    glsl_type, attribute = line[-2], line[-1]
                    layouts[(attribute, glsl_type)] = location

            self.vertex_formats[vertex_shader_name] = sorted(layouts, key=lambda k: layouts[k])
            self.uniforms[vertex_shader_name] = uniforms
            # TODO: get fragment shader uniforms & texture samplers
        # TODO: configure vertex attribs for each shader (set_shader method?)
            ...
        # TODO: match vertex shaders to fragment shaders

    def init_GL(self):
        gl.glClearColor(0.25, 0.25, 0.5, 0.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gluPerspective(90, 1, 0.1, 1024)
        gl.glTranslate(0, 0, -8)
        gl.glPointSize(4)
        self.import_shader("mesh_flat")

    def compile_shaders(self):
        global shader_folder
        for vertex_shader_name in self.shaders:
            for fragment_shader_name in self.shaders[vertex_shader_name]:
                with open(os.path.join(shader_folder, vertex_shader_name)) as vertex_shader_file:
                    vertex_shader_text = vertex_shader_file.read()
                with open(os.path.join(shader_folder, fragment_shader_name)) as fragment_shader_file:
                    fragment_shader_text = fragment_shader_file.read()
                vertex_shader = compileShader(vertex_shader_text, gl.GL_VERTEX_SHADER)
                fragment_shader = compileShader(fragment_shader_text, gl.GL_FRAGMENT_SHADER)
                shader = compileProgram(vertex_shader, fragment_shader)
                gl.glLinkProgram(shader)  # CHECK: can you compile the vertex shader once then link multiple times?
                self.shaders[vertex_shader_name][fragment_shader_name] = shader
                gl.glUseProgram(shader)
                for uniform, glsl_type in self.uniforms[vertex_shader_name]:
                    self.uniforms[fragment_shader_name][(uniform, glsl_type)] = gl.glGetUniformLocation(shader, uniform)
                for uniform, glsl_type in self.uniforms[fragment_shader_name]:
                    self.uniforms[fragment_shader_name][(uniform, glsl_type)] = gl.glGetUniformLocation(shader, uniform)

    def init_buffers(self):
        self.VERTEX_BUFFER = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VERTEX_BUFFER)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.buffer_size, None, gl.GL_DYNAMIC_DRAW)
        self.INDEX_BUFFER = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.INDEX_BUFFER)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.buffer_size, None, gl.GL_DYNAMIC_DRAW)
        # shader attrib pointers, must be post buffer setup
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 12, gl.GLvoidp(0))

    def draw(self):
        gl.glUseProgram(self.shaders["basic"])
        gl.glDrawElements(gl.GL_TRIANGLES, self.draw_length, gl.GL_UNSIGNED_INT, gl.GLvoidp(0))

    def update(self):
        if len(self.update_queue) > 0:
            vertices, indices = self.update_queue.pop(0)
            self.update_buffers(vertices, indices)
        view_matrix = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
        # update frequently updated shader uniforms; have a queue / cooldowns?
        gl.glUseProgram(self.basic_shader)
        gl.glUniformMatrix4fv(self.matrix_location, 1, gl.GL_FALSE, view_matrix)

    def update_buffers(self):
        if len(self.update_queue) == 0:
            return
        update = self.update_queue.pop(0)
        vertex_data = itertools.chain(*update.vertices)
        vertex_data = np.array(vertex_data, dtype=np.float32)
        # TODO: add an offset
        index_data = np.array(update.indices, dtype=np.uint32)
        gl.glBufferSubData(self.VERTEX_BUFFER, 0, len(vertex_data) * 4, vertex_data)
        gl.glBufferSubData(self.INDEX_BUFFER, 0, len(index_data) * 4, index_data)

    def add_renderable(self, renderable: Renderable):
        if renderable.shader not in self.shaders:
            raise RuntimeError(f"{renderable.shader} not loaded! cannot add renderable '{renderable.name}'")
        # TODO: pick a stretch of memory to fit vertex /index data into
        # use self.buffer_size & self.renderables[shader].allocated
        # need methods for finding & merging spans
        vertex_start = 0
        vertex_size = sum([attrib_types[g][0] for a, g in self.vertex_formats[renderable.shader]])
        flat_vertices = itertools.chain(*renderable.vertices)  # List[List[float]] --> List[float]

        index_start = 0
        offset_indices = [i + (vertex_start // vertex_size) for i in renderable.indices]

        update = Update(vertex_start, flat_vertices, 0, offset_indices)
        self.update_queue.append(update)

        vertex_span = (vertex_start, len(renderable.vertices) * vertex_size)
        index_span = (index_start, len(renderable.indices) * 4)
        stored_renderable = StoredRenderable(renderable.name, vertex_span, index_span)
        self.renderables[renderable.shader].add(stored_renderable)
        # TODO: add to buffer update queue, possibly mutating an existing entry?
