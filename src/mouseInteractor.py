# helper class for mouse interaction
# 
# Copyright (C) 2007  "Peter Roesch" <Peter.Roesch@fh-augsburg.de>
#
# This code is licensed under the PyOpenGL License.
# Details are given in the file license.txt included in this distribution.

import sys
import math

from interactionMatrix import InteractionMatrix

import threading

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print ''' Error: PyOpenGL not installed properly !!'''
    sys.exit(  )

thread = None
buttonThread = None

class MouseInteractor ( object ):
    """Connection between mouse motion and transformation matrix"""
    def __init__( self, translationScale=0.1, rotationScale=.2, interface=[]):
        self.scalingFactorRotation = rotationScale
        self.scalingFactorTranslation = translationScale
        self.rotationMatrix = InteractionMatrix( )
        self.translationMatrix = InteractionMatrix( )
        self.mouseButtonPressed = None
        self.oldMousePos = [ 0, 0 ]
        self.interface = interface

    def mouseButton( self, button, mode, x, y ):
        """Callback function for mouse button."""
        if mode == GLUT_DOWN:
            guiPressed, bPressed = self.checkGUI(x, y)
            if (not guiPressed):
                self.mouseButtonPressed = button                    
            else:
                #Some button of the GUI was pressed (saved in bPressed)
                
                #Don't register the button click as a simple mouse action (to disable model re-rendering)
                self.mouseButtonPressed = None
                
                if (bPressed.disabled == False):
                    print 'button pressed'
                    bPressed.disabled = True
        
                    global thread, buttonThread
                    thread = threading.Thread(target=bPressed.callback)
                    thread.start()
                    
                    #Saving in a global variable, so other methods know what button to enable when the thread is done
                    buttonThread = bPressed
                    print "Thread status: " + str(thread.is_alive())
                    
                    print "Doing other stuff blah blah blah"
        else:
            self.mouseButtonPressed = None
    
        if (not self.checkGUI(x, y)[0]):
            self.oldMousePos[0], self.oldMousePos[1] = x, y
            glutPostRedisplay( )

    def mouseMotion( self, x, y ):
        """Callback function for mouse motion.
        Depending on the button pressed, the displacement of the
        mouse pointer is either converted into a translation vector
        or a rotation matrix."""

        deltaX = x - self.oldMousePos[ 0 ]
        deltaY = y - self.oldMousePos[ 1 ]
        if self.mouseButtonPressed == GLUT_RIGHT_BUTTON:
            tX = deltaX * self.scalingFactorTranslation
            tY = deltaY * self.scalingFactorTranslation
            self.translationMatrix.addTranslation(tX, -tY, 0)
        elif self.mouseButtonPressed == GLUT_LEFT_BUTTON:
            rY = deltaX * self.scalingFactorRotation
            self.rotationMatrix.addRotation(rY, 0, 1, 0)
            rX = deltaY * self.scalingFactorRotation
            self.rotationMatrix.addRotation(rX, 1, 0, 0)
        else:
            if (not self.checkGUI(x, y)[0]):
                tZ = deltaY * self.scalingFactorTranslation
                self.translationMatrix.addTranslation(0, 0, tZ)
    
        self.oldMousePos[0], self.oldMousePos[1] = x, y
        glutPostRedisplay( )

    def mousePassiveMotion(self, x, y):
        for b in self.interface:
            if self.checkButton(x, y, b):
                b.highlighted = True
            else:
                b.highlighted = False

    def applyTransformation( self ):
        global thread, buttonThread
        if(not(thread == None)):
            if (not thread.is_alive()):
                print "Thread is done!"
                buttonThread.disabled = False
                thread = None
                  
        """Concatenation of the current translation and rotation
          matrices with the current OpenGL transformation matrix"""

        glMultMatrixf( self.translationMatrix.getCurrentMatrix() )
        glMultMatrixf( self.rotationMatrix.getCurrentMatrix() )

    def registerCallbacks( self ):
        """Initialise glut callback functions."""
        glutMouseFunc( self.mouseButton )
        glutMotionFunc( self.mouseMotion )
        glutPassiveMotionFunc( self.mousePassiveMotion );

    def checkGUI(self, x, y):
        somethingPressed = False
        buttonPressed = None
        for b in self.interface:
            if (self.checkButton(x, y, b)):
                somethingPressed = True
                buttonPressed = b
        
        return (somethingPressed, buttonPressed)

    def checkButton(self, x, y, b):
        if ((x > b.x) and (x < b.x + b.w)):
            if ((y > b.y) and (y < b.y + b.h)):
                return True
        return False
        
