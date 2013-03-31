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

def drawAxis():
    glColor(1.0, 0.0, 0.0)
    glBegin(GL_LINE_STRIP)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.5, 0.0, 0.0)
    glEnd()
    glBegin(GL_LINE_STRIP)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.5, 0.0)
    glEnd()
    glBegin(GL_LINE_STRIP)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.5)
    glEnd()
    glColor(0.0, 0.0, 0.0)
    glRasterPos3f( 0.5, 0.0, 0.0 )
    glutBitmapCharacter( GLUT_BITMAP_TIMES_ROMAN_10, ord('x') )
    glRasterPos3f( 0.0, 0.5, 0.0 )
    glutBitmapCharacter( GLUT_BITMAP_TIMES_ROMAN_10, ord('y') )
    glRasterPos3f( 0.0, 0.0, 0.5 )
    glutBitmapCharacter( GLUT_BITMAP_TIMES_ROMAN_10, ord('z') )

def drawBBox(bbox):
    bbox_idx = [
                [0, 3, 2, 1],
                [4, 5, 6, 7],
                [0, 4, 7, 3],
                [1, 2, 6, 5],
                [0, 1, 5, 4],
                [2, 3, 7, 6]
               ]
    
    for face in bbox_idx:
        glBegin(GL_LINE_STRIP)
        for idx in face:
            glVertex3f(*bbox[idx])
        glVertex3f(*bbox[face[0]])
        glEnd()

'''
    =========== MAIN FUNCTIONS ============
'''

def loadModel(m, path, segpath):
    m.loadModel(path, segpath)
    m.VBOVertices = vbo.VBO(m.seqVertices)
    m.VBONormals = vbo.VBO(m.normals)
    m.VBOColors = vbo.VBO(m.colors)

def drawModel(m, quadric):
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
    
    glDrawArrays(GL_TRIANGLES, 0, len(m.seqVertices))
    
    for s in m.components.keys():
        for comp in m.components[s]:
            points = comp.contactSlots
            for data in points:
                for p in data['points']:
                    glPushMatrix()
                    glTranslatef(*p)
                    gluSphere(quadric,0.1,16,16)
                    glPopMatrix()
    

def drawBBoxes(m):
    for s in m.components.keys():
        for c in m.components[s]:
            drawBBox(c.bbox)

def init(width, height):

    global g_fVBOSupported, meshes_loaded, gui_objects, mouseInteractor, quadric
    #Check for VBOs Support
    g_fVBOSupported = IsExtensionSupported("GL_ARB_vertexbuffer_object")
    quadric = gluNewQuadric()
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
    lP = 7
    lA = 0.1
    lD = 0.2
    lS = 0.5
    glEnable( GL_LIGHTING )
    glEnable( GL_LIGHT0 )
    glLightModelfv( GL_LIGHT_MODEL_AMBIENT, [1.0, 1.0, 1.0, 1] )
    glLightfv( GL_LIGHT0, GL_POSITION, [lP, lP, lP, 1] )
    glLightfv( GL_LIGHT0, GL_AMBIENT, [lA, lA, lA, 1] )
    glLightfv( GL_LIGHT0, GL_DIFFUSE, [lD, lD, lD, 1] )
    glLightfv( GL_LIGHT0, GL_SPECULAR, [lS, lS, lS, 1] )
    
    glEnable( GL_LIGHT1 )
    glLightModelfv( GL_LIGHT_MODEL_AMBIENT, [0.4, 0.4, 0.4, 1] )
    glLightfv( GL_LIGHT1, GL_POSITION, [-lP/2.0, lP, lP, 1] )
    glLightfv( GL_LIGHT1, GL_AMBIENT, [lA, lA, lA, 1] )
    glLightfv( GL_LIGHT1, GL_DIFFUSE, [lD, lD, lD, 1] )
    glLightfv( GL_LIGHT1, GL_SPECULAR, [lS, lS, lS, 1] )
    
    glMaterialfv( GL_FRONT_AND_BACK, GL_AMBIENT, [1.0, 1.0, 1.0, 1] )
    glMaterialfv( GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 1.0, 1.0, 1] )
    glMaterialfv( GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1] )
    glMaterialf( GL_FRONT_AND_BACK, GL_SHININESS, 50 )
    
    mouseInteractor = MouseInteractor( .01, 1 , gui_objects)

    #LOAD MODEL
    start = time()

    mesh = mMesh(g_fVBOSupported)
    mesh2 = mMesh(g_fVBOSupported)
    mesh3 = mMesh(g_fVBOSupported)
    mesh4 = mMesh(g_fVBOSupported)
    
    #loadModel(mesh, '../res/tele-aliens/shapes/42.off', '../res/tele-aliens/gt/42.seg')
    loadModel(mesh, '../res/chairs/shapes/1.off', '../res/chairs/gt/1.seg')
    #loadModel(mesh2, '../res/chairs/shapes/9.off', '../res/chairs/gt/9.seg')

    
    #loadModel(mesh, '../res/chairs/json', '0')

    meshes_loaded.append(mesh)
    #meshes_loaded.append(mesh2)

    
    print "Models loaded in %f" %(time() - start)
    print
    
def drawScene():
    
    global gui_objects, meshes_loaded, quadric
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()
    xSize, ySize = glutGet( GLUT_WINDOW_WIDTH ), glutGet( GLUT_WINDOW_HEIGHT )
    gluPerspective(60, float(xSize) / float(ySize), 0.1, 1000)
    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    glTranslatef( 0, 0, -5 )
    mouseInteractor.applyTransformation()

    #Draw axis (for reference)
    drawAxis()
    
    #Draw all the stuff here
    glPushMatrix()
    for m in meshes_loaded:
        drawModel(m, quadric)
        glTranslatef( 3.5, 0, 0 )
    glPopMatrix()
    
    if (True):
        glPushMatrix()
        for m in meshes_loaded:
            drawBBoxes(m)
            glTranslatef( 3.5, 0, 0 )
        glPopMatrix()

            
    #Draw all the interface here
    glDisable( GL_LIGHTING )
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, float(xSize), float(ySize), 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
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
