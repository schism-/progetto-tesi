'''
Created on 28/gen/2013

@author: Christian
'''

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Slider(object):
    
    def __init__(self, h, x, y):
        self.w = int( h / 10 )
        self.h = h
        self.x = x
        self.y = y 
        self.c = (0.7, 0.7, 0.7)
        
        self.enableHighlighting = False
        self.enableCallback = False
        self.type = "Slider"
        
        self.hor_m_pt = int( self.x + int(self.w / 2) )
        self.ver_m_pt = int( self.y + int(self.h / 2) )
        
        self.offset = 0
        self.normOffset = 0.0
        
    def checkHit(self, x, y, click):
        if ((x > self.x) and (x < self.x + self.w)):
            if ((y > self.y) and (y < self.y + self.h)):
                if (click):
                    self.offset = int(self.ver_m_pt - y)
                    self.normOffset = (self.ver_m_pt - y) / (self.h / 2.0)
                return True
        self.offset = 0
        self.normOffset = 0.0
        return False
    
    def mouseUp(self):
        self.offset = 0
        self.normOffset = 0.0
    
    def draw(self):
        
        glRasterPos3f( self.hor_m_pt - 30, self.y - 20, 0 )
        for c in str(self.normOffset):
            glutBitmapCharacter( GLUT_BITMAP_TIMES_ROMAN_24, ord(c) )
        
        glColor3f( 0.0, 0.0, 0.0 )
        glBegin(GL_LINE_STRIP)
        glVertex2i( self.hor_m_pt - int( (self.w + 4) / 2 ) , self.ver_m_pt - int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt + int( (self.w + 4) / 2 ) , self.ver_m_pt - int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt + int( (self.w + 4) / 2 ) , self.ver_m_pt + int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt - int( (self.w + 4) / 2 ) , self.ver_m_pt + int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt - int( (self.w + 4) / 2 ) , self.ver_m_pt - int( int(self.h / 10) / 2) - self.offset )
        glEnd()
        
        glColor3f(*(0.7 * x for x in self.c))
        glBegin(GL_QUADS)
        glVertex2i( self.hor_m_pt - int( (self.w + 4) / 2 ) , self.ver_m_pt - int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt + int( (self.w + 4) / 2 ) , self.ver_m_pt - int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt + int( (self.w + 4) / 2 ) , self.ver_m_pt + int( int(self.h / 10) / 2) - self.offset )
        glVertex2i( self.hor_m_pt - int( (self.w + 4) / 2 ) , self.ver_m_pt + int( int(self.h / 10) / 2) - self.offset )
        glEnd()
        
        glColor3f( 0.0, 0.0, 0.0 )
        glBegin(GL_LINE_STRIP)
        glVertex2i( self.hor_m_pt - int( self.w / 2 ) , self.ver_m_pt )
        glVertex2i( self.hor_m_pt + int( self.w / 2 ) , self.ver_m_pt )
        glEnd()
        
        glColor3f( 0.0, 0.0, 0.0 )
        glBegin(GL_LINE_STRIP)
        glVertex2i( self.x          , self.y      )
        glVertex2i( self.x          , self.y + self.h )
        glVertex2i( self.x + self.w , self.y + self.h )
        glVertex2i( self.x + self.w , self.y      )
        glVertex2i( self.x          , self.y      )
        glEnd()
        
        glColor3f(*self.c)
        glBegin(GL_QUADS)
        glVertex2i( self.x          , self.y      )
        glVertex2i( self.x          , self.y + self.h )
        glVertex2i( self.x + self.w , self.y + self.h )
        glVertex2i( self.x + self.w , self.y      )
        glEnd()
        
        
        