from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Button(object):

    def __init__(self, x, y, w, h, c, oc, label):
        self.x = x      #X position on the screen
        self.y = y      #Y position on the screen
        self.w = w      #Width
        self.h = h      #Height
        self.c = c      #Colour (r,g,b)
        self.oc = oc    #Outline Colour (r,g,b)
        self.label = label
        self.fontx = self.x + (self.w - len(self.label) * glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord('a'))) / 2
        self.fonty = self.y + (self.h + 14) / 2;

        self.highlighted = False
        self.disabled = False
        self.callback = None

    def setCallback(self, c):
        self.callback = c
        
    def drawButton(self):
        
        if (self.disabled):
            glColor3f(0.4, 0.4, 0.4)
        else:
            glColor3f(0.0, 0.0, 0.0)
        
        glRasterPos3f( self.fontx, self.fonty, 0 )
        for c in self.label:
            glutBitmapCharacter( GLUT_BITMAP_TIMES_ROMAN_24, ord(c) )

        if (self.disabled):
            temp = (0.5 * x for x in self.c)
            glColor3f(*temp)
        else:
            if (self.highlighted):
                temp = (1.2 * x for x in self.c)
                glColor3f(*temp)
            else:
                glColor3f(*self.c)
    
        glBegin(GL_QUADS)
        glVertex2i( self.x          , self.y      )
        glVertex2i( self.x          , self.y + self.h )
        glVertex2i( self.x + self.w , self.y + self.h )
        glVertex2i( self.x + self.w , self.y      )
        glEnd();

        '''
        Draw an outline around the button with width 3
        '''
        glLineWidth(2)

        glColor3f(*self.oc)

        glBegin(GL_LINE_STRIP)
        glVertex2i( self.x + self.w , self.y      )
        glVertex2i( self.x          , self.y      )
        glVertex2i( self.x          , self.y + self.h )
        glEnd()

        bottomOutline = (0.5 * x for x in self.oc)
        glColor3f(*bottomOutline);

        glBegin(GL_LINE_STRIP)
        glVertex2i( self.x          , self.y + self.h )
        glVertex2i( self.x+self.w   , self.y + self.h )
        glVertex2i( self.x+self.w   , self.y      )
        glEnd()

        glLineWidth(1)

        
