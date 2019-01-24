from OpenGL.GL import *
from PyQt5 import QtCore, QtOpenGL, QtWidgets
from PyQt5.QtCore import Qt
import sys
import numpy as np
import pyrr
import os
from PyQt5.QtWidgets import (QGridLayout, QColorDialog, QWidget, QSlider, QFormLayout, QMainWindow, QAction,
                             QFileDialog, QComboBox)
import math


class _window(QtOpenGL.QGLWidget):
    def __init__(self, major=4, minor=4):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(major, minor)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        self.timer = QtCore.QElapsedTimer()
        super(_window, self).__init__(fmt, None)
        self.paintGL = None

    def initializeGL(self):
        pass

    def paintGL(self):
        self.init()
        self.render()
        self.paintGL = self.render

    def init(self):
        pass

    def render(self):
        pass


class Window(_window):
    def __init__(self, data_filepath, major=4, minor=4):
        super(Window, self).__init__(major=major, minor=minor)
        # self.resize(width, height)
        self.points = []
        self.point_size = 1
        self.background_color = (0.3, 0.3, 0.1, 1)
        self.deltaTime = 0
        self.lastFrame = 0
        self.lastX = 0
        self.lastY = 0
        self.cameraMode = False
        self.first_mouse = True
        self.keys = [False] * 17000000
        self.vao = None
        self.camera = Camera(
            width=self.width(),
            height=self.height(),
            zNear=0.1,
            zFar=1000.0,
            position=pyrr.Vector3([0.0, 0.0, 40.0]),
            up=pyrr.Vector3([0, 1, 0])
        )

        self.projection = self.camera.GetPerspectiveMatrix()
        self.view = self.camera.GetViewMatrix()
        self.model = pyrr.matrix44.create_identity()

        self.data_filepath = data_filepath

    def keyPressEvent(self, evt):
        self.keys[evt.key()] = True

    def keyReleaseEvent(self, evt):
        self.keys[evt.key()] = False

    def resizeEvent(self, QResizeEvent):
        self.camera.cameraWidth = QResizeEvent.size().width()
        self.camera.cameraHeight = QResizeEvent.size().height()

    def mousePressEvent(self, evt):
        if evt.button() == Qt.LeftButton:
            self.cameraMode = True

    def mouseMoveEvent(self, evt):
        if self.first_mouse:
            self.first_mouse = False
            self.lastX = evt.x()
            self.lastY = evt.y()
        xoffset = evt.x() - self.lastX
        yoffset = self.lastY - evt.y()
        self.lastX = evt.x()
        self.lastY = evt.y()

        if self.cameraMode:
            self.camera.mouseCall(xoffset, yoffset)

    def mouseReleaseEvent(self, evt):
        if evt.button() == Qt.LeftButton:
            self.lastX = evt.x()
            self.lastY = evt.y()
            self.cameraMode = False
            self.first_mouse = True

    def cameraMove(self, ):
        if self.keys[Qt.Key_Up] or self.keys[Qt.Key_W]:
            self.camera.keyboardCall('FORWARD', self.deltaTime)
        if self.keys[Qt.Key_Down] or self.keys[Qt.Key_S]:
            self.camera.keyboardCall('BACKWARD', self.deltaTime)
        if self.keys[Qt.Key_Left] or self.keys[Qt.Key_A]:
            self.camera.keyboardCall('LEFT', self.deltaTime)
        if self.keys[Qt.Key_Right] or self.keys[Qt.Key_D]:
            self.camera.keyboardCall('RIGHT', self.deltaTime)

    def setPoints(self, data_filepath):
        self.points = []
        if data_filepath is not None and os.path.isfile(data_filepath):
            for xyz in open(data_filepath, 'r'):
                if len(xyz.split(' ')) == 3:
                    for v in xyz.split(' '):
                        v = float(v.strip())
                        v *= 10.0
                        self.points.append(v)
        self.g_vertex_buffer_data = np.array(self.points, 'f')

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.g_vertex_buffer_data.itemsize * len(self.g_vertex_buffer_data),
                     self.g_vertex_buffer_data, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.g_vertex_buffer_data.itemsize * 3, ctypes.c_void_p(0))
        glBindVertexArray(0)

    def init(self):
        print("Created context with size: {width}x{height}".format(width=self.width(), height=self.height()))
        print(("Using OpenGL version: %s") % glGetString(GL_VERSION).decode("utf-8"))

        self.vao = glGenVertexArrays(1)
        self.vertex_buffer = glGenBuffers(1)

        self.setPoints(self.data_filepath)
        # vertex shader
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, "#version 400\n"
                               "layout (location = 0) in vec3 pos;\n"
                               "uniform mat4 projection;\n"
                               "uniform mat4 view;\n"
                               "uniform mat4 model;\n"
                               "uniform float pointSize;\n"
                               "void main() {\n"
                               "mat4 mvp = projection * view * model;\n"
                               "gl_PointSize = pointSize;\n"
                               "gl_Position = mvp * vec4(pos, 1);\n"
                               "}\n")
        glCompileShader(vertex)
        success = glGetShaderiv(vertex, GL_COMPILE_STATUS)
        if not success:
            infoLog = glGetShaderInfoLog(vertex)
            print(infoLog.decode("utf-8"))

        # fragment shader
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, "#version 400\n"
                                 "layout( location = 0 ) out vec4 FragColor;\n"
                                 "void main() {\n"
                                 "FragColor  = vec4(1.0, 1.0, 1.0, 1.0);\n"
                                 "}\n")
        glCompileShader(fragment)
        success = glGetShaderiv(fragment, GL_COMPILE_STATUS)
        if not success:
            infoLog = glGetShaderInfoLog(fragment)
            print(infoLog.decode("utf-8"))

        # // Shader Program
        self.programId = glCreateProgram()
        glAttachShader(self.programId, vertex)
        glAttachShader(self.programId, fragment)
        glLinkProgram(self.programId)
        success = glGetProgramiv(self.programId, GL_LINK_STATUS)

        if not success:
            infoLog = glGetProgramInfoLog(self.programId)
            print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog)

        glDeleteShader(vertex)
        glDeleteShader(fragment)

        glEnable(GL_PROGRAM_POINT_SIZE)

    def draw_scene(self):
        try:
            glClear(GL_COLOR_BUFFER_BIT)
            glClearColor(self.background_color[0], self.background_color[1], self.background_color[2],
                         self.background_color[3])
            glViewport(0, 0, self.width(), self.height())

            self.projection = self.camera.GetPerspectiveMatrix()
            self.view = self.camera.GetViewMatrix()

            glUseProgram(self.programId)
            glUniformMatrix4fv(glGetUniformLocation(self.programId, "projection"), 1, GL_FALSE, self.projection)
            glUniformMatrix4fv(glGetUniformLocation(self.programId, "view"), 1, GL_FALSE, self.view)
            glUniformMatrix4fv(glGetUniformLocation(self.programId, "model"), 1, GL_FALSE, self.model)
            glUniform1fv(glGetUniformLocation(self.programId, "pointSize"), 1, self.point_size)
            glBindVertexArray(self.vao)
            glDrawArrays(GL_POINTS, 0, int(len(self.points) / 3))
            glUseProgram(0)
        except Exception as e:
            print(e)

    def render(self):
        currentFrame = float(self.timer.elapsed()) / 1000.0
        self.deltaTime = currentFrame - self.lastFrame
        self.lastFrame = currentFrame
        self.cameraMove()
        self.draw_scene()
        self.update()


class Camera:
    defaultCameraYaw = -90.0
    defaultCameraPitch = 0.0
    defaultCameraSpeed = 40.0
    defaultCameraSensitivity = 0.10
    defaultCameraFOV = 45.0

    def __init__(self, width, height, zNear, zFar, position=pyrr.Vector3([0.0, 0.0, 0.0]),
                 up=pyrr.Vector3([0.0, 1.0, 0.0]),
                 yaw=defaultCameraYaw, pitch=defaultCameraPitch):
        self.cameraNear = zNear
        self.cameraFar = zFar
        self.cameraPosition = position
        self.worldUp = up
        self.cameraUp = up
        self.cameraYaw = yaw
        self.cameraPitch = pitch
        self.cameraWidth = width
        self.cameraHeight = height
        self.cameraSpeed = self.defaultCameraSpeed
        self.cameraSensitivity = self.defaultCameraSensitivity
        self.cameraFront = pyrr.Vector3([0.0, 0.0, 1.0])
        self.cameraFOV = self.defaultCameraFOV
        self.cameraRight = 0
        self.updateCameraVectors()

    def GetViewMatrix(self):
        return pyrr.matrix44.create_look_at(eye=self.cameraPosition,
                                            target=self.cameraPosition + self.cameraFront,
                                            up=self.cameraUp
                                            )

    def GetPerspectiveMatrix(self):
        return pyrr.matrix44.create_perspective_projection(fovy=self.cameraFOV,
                                                           aspect=pyrr.trig.aspect_ratio(self.cameraWidth,
                                                                                         self.cameraHeight),
                                                           near=self.cameraNear,
                                                           far=self.cameraFar
                                                           )

    def viewPortTransormation(self, p):
        normalizedp = 0.5 * p + pyrr.Vector3([0.5, 0.5, 0.5])
        offset = pyrr.Vector3(0.0, 0.0, self.cameraNear)
        size = pyrr.Vector3(self.cameraWidth, self.cameraHeight, self.cameraFar - self.cameraNear)
        return offset + normalizedp * size

    def keyboardCall(self, direction, deltaTime):
        cameraVelocity = self.cameraSpeed * deltaTime

        if direction == 'FORWARD':
            self.cameraPosition = self.cameraPosition + self.cameraFront * cameraVelocity
        if direction == 'BACKWARD':
            self.cameraPosition = self.cameraPosition - self.cameraFront * cameraVelocity
        if direction == 'LEFT':
            self.cameraPosition = self.cameraPosition - self.cameraRight * cameraVelocity
        if direction == 'RIGHT':
            self.cameraPosition = self.cameraPosition + self.cameraRight * cameraVelocity

    def mouseCall(self, xoffset, yoffset, constrainPitch=True):
        xoffset_t = xoffset * self.cameraSensitivity
        yoffset_t = yoffset * self.cameraSensitivity
        self.cameraYaw = self.cameraYaw + xoffset_t
        self.cameraPitch = self.cameraPitch + yoffset_t

        if constrainPitch:
            if self.cameraPitch > 89.0:
                self.cameraPitch = 89.0
            if self.cameraPitch < -89.0:
                self.cameraPitch = -89.0

        self.updateCameraVectors()

    def scrollCall(self, yoffset):
        if 1.0 <= self.cameraFOV <= 45.0:
            self.cameraFOV = self.cameraFOV - yoffset
        if self.cameraFOV <= 1.0:
            self.cameraFOV = 1.0
        if self.cameraFOV >= 45.0:
            self.cameraFOV = 45.0

    def updateCameraVectors(self):
        front = pyrr.Vector3([0.0, 0.0, 0.0])
        front.x = math.cos(np.radians(self.cameraYaw)) * math.cos(np.radians(self.cameraPitch))
        front.y = math.sin(np.radians(self.cameraPitch))
        front.z = math.sin(np.radians(self.cameraYaw)) * math.cos(np.radians(self.cameraPitch))

        self.cameraFront = pyrr.vector3.normalize(front)
        self.cameraRight = pyrr.vector3.normalize(pyrr.vector3.cross(self.cameraFront, self.worldUp))
        self.cameraUp = pyrr.vector3.normalize(pyrr.vector3.cross(self.cameraRight, self.cameraFront))

    @staticmethod
    def calculate_up(lookAt, pos):
        """
        calculate new lookUp vector of camera
        :param lookAt: camera lookat vector
        :param x: camera position x
        :param y: camera position y
        :param z: camera position z
        :return: new lookup vector
        """
        yDir = pyrr.Vector3([0, 1, 0])
        viewDir = pyrr.vector3.normalize(lookAt - pos)
        rightDir = pyrr.vector3.normalize(pyrr.vector3.cross(viewDir, yDir))
        return pyrr.vector3.normalize(pyrr.vector3.cross(rightDir, viewDir))


class MyWindow(QMainWindow):
    def __init__(self, width=1920, height=1080):
        super().__init__()
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.resize(width, height)
        self.initUI()
        self.createActions()
        self.createMenus()
        self.pointFileNames = {}
        self.segmentationFileNames = {}

    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ExistingFile
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Points File", "",
                                                  "Points File (*.pts)", options=options)
        if fileName:
            self.mywidget.setPoints(fileName)

    def openFolder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DirectoryOnly
        options |= QFileDialog.ShowDirsOnly
        folderName = QFileDialog.getExistingDirectory(self, "Select Folder containing points",
                                                      "G:/projects/PointCNN/data/shapenet_partseg", options=options)

        if folderName and os.path.isdir(folderName):
            self.pointFileNames = {'train': {},
                                   'validation': {},
                                   'test': {}}
            self.segmentationFileNames = {'train': {},
                                          'validation': {},
                                          'test': {}}
            for root, subd, files in os.walk(folderName):
                for file in files:
                    key = file[:-4]
                    type = 'default'
                    if 'train' in root:
                        type = 'train'
                    elif 'val' in root:
                        type = 'validation'
                    elif 'test' in root:
                        type = 'test'

                    if str(file).endswith(".pts"):
                        self.pointFileNames[type][key] = os.path.join(root, file)
                    if str(file).endswith(".seg"):
                        self.segmentationFileNames[type][key] = os.path.join(root, file)
            self.pointsCombobox.addItems(self.pointFileNames['train'].keys())

    def createActions(self):
        self.openAct = QAction("Open")
        self.openAct.triggered.connect(self.openFile)
        self.openFolderAct = QAction("Open Folder")
        self.openFolderAct.triggered.connect(self.openFolder)

    def createMenus(self):
        filemenu = self.menuBar().addMenu("File")
        filemenu.addAction(self.openAct)
        filemenu.addAction(self.openFolderAct)

    def keyPressEvent(self, evt):
        super().keyPressEvent(evt)
        self.mywidget.keyPressEvent(evt)

    def keyReleaseEvent(self, evt):
        super().keyReleaseEvent(evt)
        self.mywidget.keyReleaseEvent(evt)

    def datasetChanged(self, index):
        key = list(self.pointFileNames['train'].keys())[index]
        fileName = self.pointFileNames['train'][key]
        self.mywidget.setPoints(data_filepath=fileName)

    def addSlider(self, layout, text="Slider", min=1, max=10, step=1, callback=None):
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(1)
        slider.setSingleStep(step)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setFocusPolicy(Qt.NoFocus)
        if callback:
            slider.valueChanged.connect(callback)
        layout.addRow(text, slider)

    def update_point_size(self, value):
        self.mywidget.point_size = float(value) * 1.0

    def update_color(self, color):
        color = np.array([color.red(), color.green(), color.blue(), color.alpha()])
        self.mywidget.background_color = color / 255.0

    def initUI(self):
        # Create some widgets (these won't appear immediately):
        self.leftWidget = QWidget()
        self.pointsCombobox = QComboBox()
        self.pointsCombobox.setFocusPolicy(Qt.NoFocus)
        self.pointsCombobox.currentIndexChanged.connect(self.datasetChanged)
        self.leftWidget.setLayout(QFormLayout())
        self.leftWidget.layout().addRow("Point sets", self.pointsCombobox)
        self.addSlider(self.leftWidget.layout(), text="Point Size", max=15, callback=self.update_point_size)
        cDialog = QColorDialog(self)
        cDialog.currentColorChanged.connect(self.update_color)
        cDialog.setWindowFlags(Qt.Widget)
        cDialog.setOptions(QColorDialog.DontUseNativeDialog | QColorDialog.NoButtons)
        cDialog.setFocusPolicy(Qt.NoFocus)
        self.leftWidget.layout().addRow(cDialog)

        self.leftWidget.setFixedWidth(600)
        self.mywidget = Window(data_filepath=None)

        # Put the widgets in a layout (now they start to appear):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mywidget, 0, 1)
        layout.addWidget(self.leftWidget, 0, 0)
        self.widget.setLayout(layout)


def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = MyWindow()
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
