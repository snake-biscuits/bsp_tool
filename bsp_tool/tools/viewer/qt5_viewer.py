import OpenGL.GL as gl
from PyQt5 import QtCore, QtWidgets

from . import render_manager


class Viewport(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Viewport, self).__init__(parent=None)
        self.render_manager = render_manager.RenderManager()
        self.clock = QtCore.QTimer()
        self.clock.timeout.connect(self.update)

    def initializeGL(self):
        self.render_manager.init_GL()
        self.render_manager.init_buffers()
        self.clock.start(15)  # tick_length in milliseconds

    def update(self, tick_length=0.015):
        self.makeCurrent()
        gl.glRotate(30 * tick_length, 1, 0, 1.25)  # orbit camera
        self.render_manager.update()
        self.doneCurrent()
        super(Viewport, self).update()  # calls paintGL

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.render_manager.draw()


if __name__ == "__main__":
    import sys

    from .. import bsp_tool

    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook  # Python Qt Debug

    app = QtWidgets.QApplication(sys.argv)
    window = Viewport()
    window.setGeometry(128, 64, 576, 576)

    angel_city = bsp_tool.load_bsp("E:/Mod/Titanfall/maps/mp_angel_city.bsp")

    special_vertices = angel_city.vertices_of_mesh(0)

    vertices = list()
    for vertex in special_vertices:
        position = angel_city.VERTICES[vertex.position_index]
        normal = angel_city.VERTEX_NORMALS[vertex.normal_index]
        vertices.append((position, normal, vertex.uv))  # universal format

    indices = [i for i, v in enumerate(vertices)]
    mesh_0 = render_manager.Renderable("Mesh 0", "mesh_flat", vertices, indices)

    window.render_manager.add_renderable(mesh_0)
    window.show()
    app.exec_()
