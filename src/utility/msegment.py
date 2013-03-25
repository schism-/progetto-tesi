import math
import os
import random
import numpy
from time import time

from OpenGL.GL.ARB.vertex_buffer_object import *
from numpy.ma.core import sqrt

from OBB import obb
from curvature import *
from ConnectedComponents import *



class mSegment:
    def __init__(self, segmentId=0, name='', nameComp= -1):

        self.name = name
        self.path = ''
        
        self.vertexCount = 0
        self.faceCount = 0
        self.texCoordCount = 0
        self.normalCount = 0

        self.vertices = None
        self.texCoords = None
        self.normals = None
        self.faces = None

        self.segmentId = segmentId
        self.componentName = nameComp
        
        self.color = None
        
        self.bbox = []
        self.eigen_features = []
        self.curvature_hist = []
        self.contactSlots = []

    def update(self):
        self.vertexCount = len(self.vertices)
        self.faceCount = int(len(self.vertices) / 3)
        self.normalCount = len(self.vertices)
        
        self.faces = []
        for x in range(len(self.vertices)):
            if (x % 3 == 0):
                self.faces.append([x, x+1, x+2])
    
    def getComponents(self):
        print "Finding components..."
        # TODO: TURN COMPONENTS INTO WELL-FORMED SEGMENTS
        components = computeComponents(self.vertices, self.faces)
        
        result = []
        nameComp = 0
        for verts, faces in components:
            t = mSegment(self.segmentId, self.name, nameComp)
            nameComp += 1
            t.vertices = verts
            t.faces = faces
            result.append(t)
        
        return result
        
        
    def extractFeatures(self):
        print "Extracting features..."
        self.bbox, self.eigen_features = obb.computeOBB_2( self.vertices, self.faces )
        self.bbox = numpy.array(self.bbox)
        self.eigen_features = numpy.array(self.eigen_features)
        
        #Computing curvature histograms for all components
        po = CurvaturesDemo()
        #[[MIN_4, MIN_8, MIN_16], [MAX_4, MAX_8, MAX_16]]
        self.curvature_hist = po.compute_curvatures(self.vertices, self.faces)
        self.curvature_hist = numpy.array(self.curvature_hist)
        
        #Computing shape diameter histograms
        # parse external files 
        # Done offline in saveSDHist.py
        
        #Computing Light-Field descriptors and PCA them
        # CFR @LightFieldDesc.py
        
    def saveFeatures(self, directory):
        print "Saving features..."
        
        derp = directory + "../seg_" + str(self.segmentId) + "_comp_" + str(self.componentName) + ".off"
        self.writeOFFFile( derp, self.vertices, self.faces )
        
        #Saving .OFF file
        comp_dir = directory + "comp_" + str(self.componentName)
        if( not os.path.isdir(comp_dir) ):
            os.mkdir(comp_dir)
        
        self.writeOFFFile( comp_dir + "/mesh.off", self.vertices, self.faces )
    
    def writeOFFFile(self, offpath, vertices, faces):
        try:
            fi = open(offpath, 'w')
        except IOError:
            print "Error"
            
        fi.write("OFF\n")
        fi.write(str(len(vertices)) + " " + str(len(faces)) + " 0\n")
        
        for v in vertices:
            fi.write(str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")
            
        for f in faces:
            fi.write("3 " + str(f[0]) + " " + str(f[1]) + " " + str(f[2]) + "\n")
    
        fi.close()
            
            