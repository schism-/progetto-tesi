from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

from OpenGL.arrays import vbo

from OpenGL.GL.ARB.vertex_buffer_object import *

from utility.mvertex    import mVertex
from utility.mnormal    import mNormal
from utility.mtexcoord  import mTexCoord
from utility.mface      import mFace
from utility.mmesh      import mMesh

from utility.drawfunctions import *

from utility.gui.button import Button

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

mesh = None
thread = None
buttonThread = None

'''
    ========== UTILITY FUNCTIONS ==========
'''

def IsExtensionSupported (TargetExtension):
    """ Accesses the rendering context to see if it supports an extension.
	Note, that this test only tells you if the OpenGL library supports
	the extension. The PyOpenGL system might not actually support the extension.
    """
    Extensions = glGetString (GL_EXTENSIONS)
    # python 2.3
    # if (not TargetExtension in Extensions):
    #	gl_supports_extension = False
    #	print "OpenGL does not support '%s'" % (TargetExtension)
    #	return False

    # python 2.2
    Extensions = Extensions.split ()
    found_extension = False
    for extension in Extensions:
            if extension == TargetExtension:
                    found_extension = True
                    break;
    if (found_extension == False):
            gl_supports_extension = False
            print "OpenGL rendering context does not support '%s'" % (TargetExtension)
            return False

    gl_supports_extension = True

    # Now determine if Python supports the extension
    # Exentsion names are in the form GL_<group>_<extension_name>
    # e.g.  GL_EXT_fog_coord 
    # Python divides extension into modules
    # g_fVBOSupported = IsExtensionSupported ("GL_ARB_vertex_buffer_object")
    # from OpenGL.GL.EXT.fog_coord import *
    if (TargetExtension [:3] != "GL_"):
            # Doesn't appear to following extension naming convention.
            # Don't have a means to find a module for this exentsion type.
            return False

    # extension name after GL_
    afterGL = TargetExtension [3:]
    try:
            group_name_end = afterGL.index ("_")
    except:
            # Doesn't appear to following extension naming convention.
            # Don't have a means to find a module for this exentsion type.
            return False

    group_name = afterGL [:group_name_end]
    extension_name = afterGL [len (group_name) + 1:]
    extension_module_name = "OpenGL.GL.ARB.%s" % (extension_name)

    import traceback
    try:
            __import__ (extension_module_name)
            print "PyOpenGL supports '%s'" % (TargetExtension)
    except:
            traceback.print_exc()
            print 'Failed to import', extension_module_name
            print "OpenGL rendering context supports '%s'" % (TargetExtension),
            return False

    return True

'''
    =========== MAIN FUNCTIONS ============
'''
def try1():
    import time
    time.sleep(3)
    print "AHAHAHAHAHAH!"

def init(width, height):

    global g_fVBOSupported, mesh, mouseInteractor, b1, b2
    #Check for VBOs Support
    g_fVBOSupported = IsExtensionSupported("GL_ARB_vertexbuffer_object")

    #Defining all interface objects
    buttonColor = (0.7, 0.7, 0.7)
    buttonOutlineColor = (0.8, 0.8, 0.8)
    b1 = Button( 20, 20, 100, 30, buttonColor, buttonOutlineColor, 'Button 1')
    b2 = Button( 20, 60, 100, 30, buttonColor, buttonOutlineColor, 'Button 2')

    b1.setCallback(try1)
    b2.setCallback(try1)

    glClearColor(0.6, 0.6, 0.6, 0.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glEnable( GL_LIGHTING )
    glEnable( GL_LIGHT0 )
    glLightModeli( GL_LIGHT_MODEL_TWO_SIDE, 0 )
    lP = 1000
    glLightfv( GL_LIGHT0, GL_POSITION, [lP, lP, lP, 1] )
    lA = 0.8
    glLightfv( GL_LIGHT0, GL_AMBIENT, [lA, lA, lA, 1] )
    lD = 1
    glLightfv( GL_LIGHT0, GL_DIFFUSE, [lD, lD, lD, 1] )
    lS = 1
    glLightfv( GL_LIGHT0, GL_SPECULAR, [lS, lS, lS, 1] )
    
    glMaterialfv( GL_FRONT_AND_BACK, GL_AMBIENT, [0.1, 0.1, 0.1, 1] )
    glMaterialfv( GL_FRONT_AND_BACK, GL_DIFFUSE, [0.2, 0.2, 0.2, 1] )
    glMaterialfv( GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1] )
    glMaterialf( GL_FRONT_AND_BACK, GL_SHININESS, 50 )
    
    mouseInteractor = MouseInteractor( .01, 1 , [b1, b2])

    #LOAD MODEL
    mesh = mMesh(g_fVBOSupported)
   
    start = time()
    mesh.loadOBJModel('../res/elf-tri.obj')
    print "Model loaded in %f" %(time() - start)
    print

    mesh.VBOVertices = vbo.VBO(mesh.vertices)
    mesh.VBONormals = vbo.VBO(mesh.normals)
    
def drawScene():
    global mouseInteractor, mesh, SHAPE, thread, buttonThread
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()
    xSize, ySize = glutGet( GLUT_WINDOW_WIDTH ), glutGet( GLUT_WINDOW_HEIGHT )
    gluPerspective(60, float(xSize) / float(ySize), 0.1, 1000)
    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    glTranslatef( 0, -1, -30 )
    mouseInteractor.applyTransformation()

    #Draw all the stuff here
    mesh.VBOVertices.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, mesh.VBOVertices)

    mesh.VBONormals.bind()
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 0, mesh.VBONormals)
    
    glDrawArrays(GL_TRIANGLES, 0, len(mesh.vertices))

    #Draw all the interface here
    glDisable( GL_LIGHTING )
    
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, float(xSize), float(ySize), 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    global b1,b2
    b1.drawButton()
    b2.drawButton()

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
