import OpenGL.GL as gl
from PyQt5 import QtCore, QtGui, QtWidgets

from . import camera
from . import render
from . import vector


camera.keybinds = {camera.FORWARD: [QtCore.Qt.Key_W],
                   camera.BACK: [QtCore.Qt.Key_S],
                   camera.LEFT: [QtCore.Qt.Key_A],
                   camera.RIGHT: [QtCore.Qt.Key_D],
                   camera.UP: [QtCore.Qt.Key_Q],
                   camera.DOWN: [QtCore.Qt.Key_E]}


class Viewport(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Viewport, self).__init__(parent=None)
        self.render_manager = render.Manager()
        self.camera = camera.Camera((0, 0, 0))  # start camera at origin
        self.clock = QtCore.QTimer()
        self.clock.timeout.connect(self.update)
        self.keys = set()
        self.last_mouse_position = vector.vec2()
        self.mouse_position = vector.vec2()

    def initializeGL(self):
        self.render_manager.init_GL()
        self.render_manager.init_buffers()
        self.clock.start(15)  # tick length in milliseconds
        self.last_mouse_position = vector.vec2(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y())

    def keyPressEvent(self, event):
        self.keys.add(event.key())

    def keyReleaseEvent(self, event):
        self.keys.discard(event.key())

    def update(self):
        tick_length = self.clock.interval() - self.clock.remainingTime()
        self.makeCurrent()
        gl.glRotate(30 * tick_length, 1, 0, 1.25)  # orbit camera
        self.mouse_position = vector.vec2(QtGui.QCursor.pos().x(), QtGui.QCursor.pos().y())
        mouse_motion = self.mouse_position - self.last_mouse_position
        self.last_mouse_position = self.mouse_position
        self.camera.update(mouse_motion, self.keys, tick_length)
        self.render_manager.update()
        self.doneCurrent()
        super(Viewport, self).update()  # calls paintGL

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        self.camera.set()
        # set camera rotation
        # draw 2d skybox
        # move camera
        self.render_manager.draw()
        # origin marker
        gl.glUseProgram(0)
        gl.glBegin(gl.GL_LINES)
        gl.glColor(1, 0, 0)  # X+
        gl.glVertex(0, 0, 0)
        gl.glVertex(1, 0, 0)
        gl.glColor(0, 1, 0)  # Y+
        gl.glVertex(0, 0, 0)
        gl.glVertex(0, 1, 0)
        gl.glColor(0, 0, 1)  # Z+
        gl.glVertex(0, 0, 0)
        gl.glVertex(0, 0, 1)
        gl.glEnd()


def view_bsp(bsp):  # so far rBSP only
    app = QtWidgets.QApplication([])
    viewport = Viewport()
    viewport.setGeometry(128, 64, 576, 576)

    # just grab the first mesh of a rBSP
    special_vertices = bsp.vertices_of_mesh(0)

    vertices = list()
    for vertex in special_vertices:
        position = bsp.VERTICES[vertex.position_index]
        normal = bsp.VERTEX_NORMALS[vertex.normal_index]
        vertices.append((position, normal, vertex.uv))  # universal format

    indices = [i for i, v in enumerate(vertices)]

    viewport.show()
    mesh_0 = render.Renderable("Mesh 0", "mesh_flat", vertices, indices)
    viewport.render_manager.add_renderable(mesh_0)
    app.exec_()
