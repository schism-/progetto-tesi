from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

from OpenGL.arrays import vbo

from OpenGL.GL.ARB.vertex_buffer_object import *

from utility.check_extension import *

from utility.mvertex    import mVertex
from utility.mnormal    import mNormal
from utility.mtexcoord  import mTexCoord
from utility.mface      import mFace
from utility.mmesh      import mMesh

from utility.drawfunctions import *

from utility.gui.button import Button
from utility.gui.slider import Slider

from mouseInteractor import MouseInteractor

import numpy

from time import time

'''
    ========== GLOBAL VARIABLES & CONSTANTS ==========
'''

ESCAPE = '\033'             # Octal value for 'esc' key
SCREEN_SIZE = (800, 600)
SHAPE = ''
lastx=0
lasty=0

meshes_loaded = []

gui_objects = []
thread = None
buttonThread = None

'''
    ========== UTILITY FUNCTIONS ==========
'''

def try1():
    import time
    time.sleep(3)
    print "AHAHAHAHAHAH!"

def loadElephant():
    global meshes_loaded
    #LOAD MODEL
    new_mesh = mMesh(g_fVBOSupported)
   
    start = time()
    new_mesh.loadOBJModel('../res/elephant.obj')
    print "Model loaded in %f" %(time() - start)
    print

    new_mesh.VBOVertices = vbo.VBO(new_mesh.vertices)
    new_mesh.VBONormals = vbo.VBO(new_mesh.normals)
    
    meshes_loaded = [new_mesh]

'''
    =========== MAIN FUNCTIONS ============
'''

def loadModel(m, path, segpath):
    m.loadModel(path, segpath)
    m.VBOVertices = vbo.VBO(m.vertices)
    m.VBONormals = vbo.VBO(m.normals)
    m.VBOColors = vbo.VBO(m.colors)

def drawModel(m):
    m.VBOVertices.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, m.VBOVertices)

    m.VBONormals.bind()
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 0, m.VBONormals)
    
    if (m.VBOColors is not None):
        m.VBOColors.bind()
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(3, GL_FLOAT, 0, m.VBOColors)
    else:
        glDisableClientState(GL_COLOR_ARRAY)
        pass
    
    glDrawArrays(GL_TRIANGLES, 0, len(m.vertices))

def init(width, height):

    global g_fVBOSupported, meshes_loaded, gui_objects, mouseInteractor
    #Check for VBOs Support
    g_fVBOSupported = IsExtensionSupported("GL_ARB_vertexbuffer_object")

    #Defining all interface objects
    buttonColor = (0.7, 0.7, 0.7)
    buttonOutlineColor = (0.8, 0.8, 0.8)
    
    b1 = Button( 20, 20, 160, 30, buttonColor, buttonOutlineColor, 'Load Elephant')
    b1.setCallback(loadElephant)
    
    b2 = Button( 20, 60, 160, 30, buttonColor, buttonOutlineColor, 'Try.')
    b2.setCallback(try1)

    sl1 = Slider( 150, SCREEN_SIZE[0] - 50, 50 )
    
    gui_objects.append(b1)
    gui_objects.append(b2)
    gui_objects.append(sl1)
    
    glClearColor(0.6, 0.6, 0.6, 0.0)
    
    #Define openGL rendering behaviours
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    
    #Define lightning
    glEnable( GL_LIGHTING )
    glEnable( GL_LIGHT0 )
    glLightModeli( GL_LIGHT_MODEL_TWO_SIDE, 0 )
    lP = 600
    glLightfv( GL_LIGHT0, GL_POSITION, [lP, lP, lP, 1] )
    lA = 0.8
    glLightfv( GL_LIGHT0, GL_AMBIENT, [lA, lA, lA, 1] )
    lD = 1
    glLightfv( GL_LIGHT0, GL_DIFFUSE, [lD, lD, lD, 1] )
    lS = 1
    glLightfv( GL_LIGHT0, GL_SPECULAR, [lS, lS, lS, 1] )
    
    glMaterialfv( GL_FRONT_AND_BACK, GL_AMBIENT, [0.1, 0.1, 0.1, 1] )
    glMaterialfv( GL_FRONT_AND_BACK, GL_DIFFUSE, [0.4, 0.4, 0.4, 1] )
    glMaterialfv( GL_FRONT_AND_BACK, GL_SPECULAR, [0.7, 0.6, 0.6, 1] )
    glMaterialf( GL_FRONT_AND_BACK, GL_SHININESS, 50 )
    
    mouseInteractor = MouseInteractor( .01, 1 , gui_objects)

    #LOAD MODEL
    mesh = mMesh(g_fVBOSupported)
    mesh_2 = mMesh(g_fVBOSupported)
    mesh_3 = mMesh(g_fVBOSupported)
    start = time()
    loadModel(mesh, '../res/chairs/shapes/102.off', '../res/chairs/gt/102.seg')
    loadModel(mesh_2, '../res/chairs/shapes/103.off', '../res/chairs/gt/103.seg')
    loadModel(mesh_3, '../res/chairs/shapes/109.off', '../res/chairs/gt/109.seg')
    print "Models loaded in %f" %(time() - start)
    print
    
    meshes_loaded.append(mesh)
    meshes_loaded.append(mesh_2)
    meshes_loaded.append(mesh_3)
    
def drawScene():
    
    global gui_objects, meshes_loaded
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()
    xSize, ySize = glutGet( GLUT_WINDOW_WIDTH ), glutGet( GLUT_WINDOW_HEIGHT )
    gluPerspective(60, float(xSize) / float(ySize), 0.1, 1000)
    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    glTranslatef( 0, 0, -5 )
    mouseInteractor.applyTransformation()

    #Draw all the stuff here

    for m in meshes_loaded:
        drawModel(m)
        glTranslatef( 2, 0, 0 )

    #Draw all the interface here
    glDisable( GL_LIGHTING )
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, float(xSize), float(ySize), 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
    
    for obj in gui_objects:
        obj.draw()

    glEnable( GL_LIGHTING )
    
    glutSwapBuffers()

def resizeWindow(width, height):
    if height == 0:
        height = 1

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0 , float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def keyboardHandler(*args):
    global SHAPE
    if args[0] == ESCAPE:
        sys.exit()
    elif args[0] == 't':
        SHAPE = 'TRIANGLE'
    elif args[0] == 'c':
        SHAPE = 'CUBE'
    elif args[0] == 's':
        SHAPE = 'SQUARE'
    elif args[0] == 'd':
        SHAPE = 'CUBE2'
    elif args[0] == 'm':
        SHAPE = 'MESH'
    elif args[0] == 'p':
        SHAPE = 'POINT_CLOUD'

def mainLoop():
    glutInit(sys.argv)
    glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH )
    glutInitWindowSize(*SCREEN_SIZE)
    glutInitWindowPosition(1000, 200)

    window = glutCreateWindow("MyMesh 0.1")
    
    init(*SCREEN_SIZE)
    mouseInteractor.registerCallbacks()

    glutDisplayFunc(drawScene)
    glutIdleFunc(drawScene)
    glutReshapeFunc(resizeWindow)
    glutKeyboardFunc(keyboardHandler)

    glutMainLoop()
    
if __name__ == "__main__":
    mainLoop()
