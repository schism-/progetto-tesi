import math
import os
import random
import numpy
from time import time

from OpenGL.GL.ARB.vertex_buffer_object import *
from numpy.ma.core import sqrt

from OBB import obb
from curvature import *
from ContactSlots import *
from utility.msegment import *

g_fVBOSupported = False;    # ARB_vertex_buffer_object supported?

color_map = [
             [1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 1.0, 0.0],
             [1.0, 0.0, 1.0],
             [0.0, 1.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.2, 0.2, 0.2],
             [1.0, 1.0, 0.4],
             [0.4, 1.0, 1.0]
             ]

class mMesh:
    def __init__(self, vbo):

        global g_fVBOSupported
        g_fVBOSupported = vbo
        
        self.name = ''
        
        self.vertexCount = 0
        self.faceCount = 0
        self.texCoordCount = 0
        self.normalCount = 0

        self.vertices = None
        self.verticesAsString = None
        self.seqVertices = []
        
        self.texCoords = None
        self.texCoordsAsString = None

        self.normals = None
        self.faces = None
        self.textureId = None
        self.colors = None
        
        self.segments = {}              #Array of mSegment
        self.components = {}
        self.adjacency_matrix = {}
        
        self.VBOVertices = None
        self.VBOTexCoords = None
        self.VBONormals = None
        self.VBOColors = None

    def loadModel(self, path, segpath):
        path_parts = path.split('.')
        ext = path_parts[-1]
        if ( (ext == 'obj' ) or (ext == 'OBJ') ):
            print "Loading an OBJ model"
            self.loadOBJModel(path)
        elif ( (ext == 'off' ) or (ext == 'OFF') ):
            print "Loading an OFF model"
            self.loadOFFModel(path, segpath)
        else:
            print "Loading a JSON model"
            self.loadJSONModel(path, segpath)
            
    def loadJSONModel(self, path, name):
        self.vertices = numpy.load(path + "/" + name + "/" + name + '_v.npy')
        self.normals = numpy.load(path + "/" + name + "/" + name + '_n.npy')
        self.colors = numpy.load(path + "/" + name + "/" + name + '_c.npy')
        self.segmentVertices = numpy.load(path + "/" + name + "/" + name + '_sv.npy')
        self.bboxes = numpy.load(path + "/" + name + "/" + name + '_bb.npy')
        self.curvature_hist = numpy.load(path + "/" + name + "/" + name + '_ch.npy')
        self.eigen_features = numpy.load(path + "/" + name + "/" + name + '_ef.npy')
        
    def readOFFFile(self, offpath):
        try:
            f = open(offpath)
        except IOError:
            print "The file does not exist, exiting gracefully"
            exit()
        
        if f.readline().strip() != "OFF":
            print "The file is not of reconized type"
            exit()
        
        numVerts, numFaces, devnull = map(int,f.readline().strip().split())
        
        off = map(lambda s: s.strip().split(), f.readlines()) # getting a clean array
        
        if len(off) != numVerts+numFaces:
            print "The file seems to be malformed"
            exit()
        
        vertices = map(lambda x: map(float,x), off[:numVerts])
        faces = map(lambda x: map(int,x[1:]), off[numVerts:])
        
        return (vertices, faces)
    
    def computeNormal(self, temp):
        edge1 = [   temp[0][0] - temp[1][0], 
                    temp[0][1] - temp[1][1], 
                    temp[0][2] - temp[1][2] ]
                    
        edge2 = [   temp[0][0] - temp[2][0], 
                    temp[0][1] - temp[2][1], 
                    temp[0][2] - temp[2][2] ]
                    
        normal = [ edge1[1] * edge2[2] - edge1[2] * edge2[1], 
                   edge1[2] * edge2[0] - edge1[0] * edge2[2], 
                   edge1[0] * edge2[1] - edge1[1] * edge2[0] ]
                    
        length = math.sqrt( normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2] )
        normal = [ normal[0] / length, normal[1] / length, normal[2] / length ]
        
        return normal
        
    def loadOFFModel(self, path, segpath=''):
        
        self.__init__(True)
        
        path_parts = path.split('/')
        self.name = (path_parts[-1].split('.'))[-2]
        
        self.vertices, self.faces = self.readOFFFile(path)
                
        self.vertexCount = len(self.vertices)
        self.faceCount = len(self.faces)
        self.texCoordCount = len(self.vertices)
        self.normalCount = len(self.vertices)
        
        self.normals = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.texCoords = numpy.zeros ((self.faceCount * 3, 2), 'f')
        
        print "Vertices detected: " + str(self.vertexCount) + " --> " + str(len(self.vertices))
        print "Faces detected: " + str(self.faceCount * 3)
        
        segments = open(segpath, 'r')
        max_segments = 0
        segment_map = numpy.zeros ((self.faceCount, 1), 'i')        #Maps every face to its correct segment
        segment_index = 0
        segment_count = {} #Number of faces for every segment
        for line in segments:
            if int(line) > max_segments:
                max_segments = int(line)
            if (not (int(line) in segment_count)):
                segment_count[int(line)] = 1
            else:
                segment_count[int(line)] += 1
            segment_map[segment_index] = int(line)
            segment_index += 1

        #Instantiate segments
        segmentVertices = {}
        for segmentId in segment_count.keys():
            #segmentVertices[segmentId] = numpy.zeros ((segment_count[segmentId] * 3, 3), 'f')  #Data storage for segment's vertices
            self.segments[segmentId] = mSegment(segmentId, self.name)
            self.segments[segmentId].vertices = numpy.zeros ((segment_count[segmentId] * 3, 3), 'f')  #Data storage for segment's vertices
        
        print "Segment counts:"
        sum = 0
        for segmentId in segment_count.keys():
            print "%d : %d" % (segmentId, len(self.segments[segmentId].vertices))
            sum += len(self.segments[segmentId].vertices)
        print "Segment sum: %d" % (sum)
        
        fIndex = 0
        vIndex = 0
        nIndex = 0
        sIndex = {}
        for k in segment_count.keys():
            sIndex[k] = 0
        
        #Initializing data for seq arrays 
        self.seqVertices = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.colors = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.normals = numpy.zeros ((self.faceCount * 3, 3), 'f')
        
        print "Seq vertices: %i" % (len(self.seqVertices))
        
        for f in self.faces:
            #Create a sequential array of vertices (for rendering)
            temp = []
            for v in f:
                self.seqVertices[vIndex, 0] = self.vertices[v][0]
                self.seqVertices[vIndex, 1] = self.vertices[v][1]
                self.seqVertices[vIndex, 2] = self.vertices[v][2]
                
                self.colors[vIndex, 0] = color_map[ segment_map[fIndex] - 1 ][0]
                self.colors[vIndex, 1] = color_map[ segment_map[fIndex] - 1 ][1]
                self.colors[vIndex, 2] = color_map[ segment_map[fIndex] - 1 ][2]
                
                temp.append( self.vertices[v] )
                
                segmentId = segment_map[fIndex]
                try:
                    if self.segments[int(segmentId)].color == None:
                        self.segments[int(segmentId)].color = color_map[ segment_map[fIndex] - 1 ]
                    self.segments[int(segmentId)].vertices[ sIndex[int(segmentId)], 0 ] = self.seqVertices[vIndex, 0]
                    self.segments[int(segmentId)].vertices[ sIndex[int(segmentId)], 1 ] = self.seqVertices[vIndex, 1]
                    self.segments[int(segmentId)].vertices[ sIndex[int(segmentId)], 2 ] = self.seqVertices[vIndex, 2]
                except IndexError:
                    print "Error: list index out of range for SEGMENT_VERTICES"
                    print "1st index: " + str(int(segmentId))
                    print "Len: " + str(len(self.segments[int(segmentId)].vertices))
                    print "2nd index: " + str(sIndex[int(segmentId)])
                    #exit(0)
                    
                sIndex[int(segmentId)] += 1
                vIndex += 1
            
            normal = self.computeNormal(temp)

            for _ in range(3):
                self.normals[nIndex, 0] = normal[0]
                self.normals[nIndex, 1] = normal[1]
                self.normals[nIndex, 2] = normal[2]
                nIndex += 1
             
            fIndex +=1
        print "Normals: %d" % (len(self.normals))
        
        #Generating data from segments
        for segmentId in segment_count.keys():
            self.segments[int(segmentId)].update()
            #Slicing segments in components
            self.components[int(segmentId)] = self.segments[int(segmentId)].getComponents()
            
            for c in self.components[int(segmentId)]:
                c.extractFeatures()
            
        #Defining contact slots
        self.adjacency_matrix, contact_slots = computeContactPoints(self)
        for s_k, s_v in contact_slots.items():
            for c_k, c_v in s_v.items():
                self.components[s_k][c_k].contactSlots = contact_slots[s_k][c_k]
        
        directory = '/'.join(path_parts[:-2]) + "/data/" 
        if( not os.path.isdir(directory) ):
                os.mkdir(directory)
        directory += self.name + "/"
        if( not os.path.isdir(directory) ):
                os.mkdir(directory)
                
        print "Saving directory: %s" % (directory)
        for segmentId in segment_count.keys():
            seg_dir = directory + "seg_" + str(segmentId) + "/"
            if( not os.path.isdir(seg_dir) ):
                os.mkdir(seg_dir)
            for c in self.components[int(segmentId)]:
                c.saveFeatures(seg_dir)
                    
        print "Done"

        
    def buildVBOs (self):
        global g_fVBOSupported
        
        ''' Generate And Bind The Vertex Buffer '''
        if (g_fVBOSupported):
            self.VBOVertices = int(glGenBuffersARB( 1))                    # Get A Valid Name
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOVertices )       # Bind The Buffer
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.seqVertices, GL_STATIC_DRAW_ARB )

            # Generate And Bind The Texture Coordinate Buffer
            #self.VBOTexCoords = int(glGenBuffersARB( 1))
            #glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOTexCoords )
            # Load The Data
            #glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.texCoords, GL_STATIC_DRAW_ARB )

            self.VBONormals = int(glGenBuffersARB( 1))
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBONormals )
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.normals, GL_STATIC_DRAW_ARB )

            self.VBOColors = int(glGenBuffersARB( 1))
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOColors )
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.colors, GL_STATIC_DRAW_ARB )

            #Our Copy Of The Data Is No Longer Necessary, It Is Safe In The Graphics Card
            #self.vertices = None
            #self.texCoords = None

if __name__ == "__main__":
    m = mMesh(True)
    
    m.loadOFFModel("../../res/chairs/shapes/1.off", "../../res/chairs/gt/1.seg")
    
    