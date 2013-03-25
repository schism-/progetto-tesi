import math
import os
import random
import numpy
from time import time

from OpenGL.GL.ARB.vertex_buffer_object import *
from numpy.ma.core import sqrt

from OBB import obb
from curvature import *

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

        self.texCoords = None
        self.texCoordsAsString = None

        self.normals = None

        self.faces = None

        self.textureId = None

        self.colors = None

        self.segmentVertices = []
        
        self.bboxes = []
        self.eigen_features = []
        
        self.curvature_hist = []

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
        
        
    def loadOFFModel(self, path, segpath=''):
        
        self.__init__(True)
        
#        vertCount = 0
#        texCoordCount = 0
#        faceCount = 0
#        normalCount = 0
#        tempVertices = None
#        tempNormals = None
#        tempTexCoords = None
        
        model = open(path, 'r')
        
        model.readline()                   #Shave off the OFF string
        header = model.readline()
        vertCount, faceCount, normalCount = header.split(' ')
        
        self.vertexCount = int (vertCount)
        self.faceCount = int (faceCount)
        self.texCoordCount = int (vertCount)
        self.normalCount = int (normalCount)

        tempVertices = numpy.zeros((self.vertexCount, 3), 'f')
        tempTexCoords = numpy.zeros ((self.texCoordCount, 2), 'f')
        
        self.vertices = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.normals = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.texCoords = numpy.zeros ((self.faceCount * 3, 2), 'f')
        
        print "Vertices detected: " + str(self.vertexCount) + " --> " + str(len(self.vertices))
        print "Faces detected: " + str(self.faceCount)
        
        
        segments = open(segpath, 'r')
        max_segments = 0
        segment_map = numpy.zeros ((self.faceCount, 1), 'i') #Maps every face to its correct segment
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
        
        
        self.segmentVertices = [0, ] * (max_segments + 1)
        for x in range(max_segments + 1):
            if x in segment_count:
                self.segmentVertices[x] = numpy.zeros ((segment_count[x] * 3, 1), 'i')  #Data storage for segment's vertices
            else:
                self.segmentVertices[x] = []

        print "Segment counts: " + str(segment_count)
        '''
        color_map = []
        random.seed(int(time()))
        for x in range(max_segments):
            color_map.append( ( random.random(), random.random(), random.random() ) )
        '''
        self.colors = numpy.zeros ((self.faceCount * 3, 3), 'f')
        
        #Retrieving temp vertices
        start = time()
        vIndex = 0
        tIndex = 0
        for line in model:
            data = line.strip().split(' ')
            if (len(data) == 3):
                
                tempVertices[vIndex, 0] = float(data[0])
                tempVertices[vIndex, 1] = float(data[1])
                tempVertices[vIndex, 2] = float(data[2])
                
                tempTexCoords[tIndex, 0] = 0.0
                tempTexCoords[tIndex, 1] = 1.0
                
                vIndex += 1
                tIndex += 1
        print "Temp Vertices: " + str(len(tempVertices))
        print "Sample: " + str(tempVertices[:5])
        print "Temp Vertices loaded in " + str(time() - start)
        
        #Populating vertex and face arrays
        start = time()
        model = open(path, 'r')
        vIndex = 0
        nIndex = 0
        fIndex = 0
        #sIndex = [0,] * len(segment_count.keys())
        
        sIndex = {}
        for k in segment_count.keys():
            sIndex[k] = 0
        
        print sIndex
        
        for line in model:
            data = line.split(' ')
            if (len(data) == 4):
                #Face
                if (data[0] == '3'):
                    #Triangle
                    temp = []
                    for d in data[1:]:
                        self.vertices[vIndex, 0] = tempVertices[d, 0]
                        self.vertices[vIndex, 1] = tempVertices[d, 1]
                        self.vertices[vIndex, 2] = tempVertices[d, 2]
                        
                        self.colors[vIndex, 0] = color_map[ segment_map[fIndex] - 1 ][0]
                        self.colors[vIndex, 1] = color_map[ segment_map[fIndex] - 1 ][1]
                        self.colors[vIndex, 2] = color_map[ segment_map[fIndex] - 1 ][2]
                        
                        #Creating vertex arrays for single segments
                        #print segment_map[fIndex]
                        #print sIndex[int(segment_map[fIndex])]
                        #print
                        self.segmentVertices[ segment_map[fIndex] ][ sIndex[int(segment_map[fIndex])] ] = vIndex
                        
                        vIndex += 1
                        
                        temp.append( [tempVertices[d,0],tempVertices[d,1],tempVertices[d,2]] )
                        
                        sIndex[int(segment_map[fIndex])] += 1
                        
                        
                    fIndex += 1
                    
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
                    
                    for _ in range(3):
                        self.normals[nIndex, 0] = normal[0]
                        self.normals[nIndex, 1] = normal[1]
                        self.normals[nIndex, 2] = normal[2]
                        nIndex += 1
                    
                elif (data[0] == '4'):
                    #Quad
                    print "QUAD DETECTED!"
                    pass
        print "Vertex,Color and Normal Array loaded in " + str(time() - start)
        
        #Computing OBB for all segmented components
        segments_mesh = []
        for s in self.segmentVertices:
            if len(s) > 0:
                vertices = numpy.zeros ((len(s), 3), 'f')
                vIndex = 0
                for idx in s:
                    vertices[vIndex, 0] = self.vertices[idx[0], 0]
                    vertices[vIndex, 1] = self.vertices[idx[0], 1]
                    vertices[vIndex, 2] = self.vertices[idx[0], 2]
                    vIndex += 1
                segments_mesh.append(vertices)
            
        for s_v in segments_mesh:
            self.bboxes.append(obb.computeOBB_2(s_v)[0])
            self.eigen_features.append(obb.computeOBB_2(s_v)[1])
        
        self.bboxes = numpy.array(self.bboxes)
        self.eigen_features = numpy.array(self.eigen_features)
        
        #Computing curvature histograms for all components
        po = CurvaturesDemo()
        for s_v in segments_mesh:
            self.curvature_hist.append(po.compute_curvatures(s_v))
        self.curvature_hist = numpy.array(self.curvature_hist)
        
        #Identifying contact point between components
        
        #Saving all the data collected
        path_parts = path.split('/')
        directory = '/'.join(path_parts[:-2])
        directory += "/json"
        print "dir: " + directory
        filename = (path_parts[-1].split('.'))[-2]
        print "filename: " + filename 
        
        if( not os.path.isdir(directory) ):
            os.mkdir(directory)
        
        if( not os.path.isdir(directory + "/" + filename) ):
            os.mkdir(directory + "/" + filename)
            
        numpy.save(directory + "/" + filename + "/" + filename + "_v", self.vertices)
        numpy.save(directory + "/" + filename + "/" + filename + "_n", self.normals)
        numpy.save(directory + "/" + filename + "/" + filename + "_c", self.colors)
        numpy.save(directory + "/" + filename + "/" + filename + "_sv", self.segmentVertices)
        numpy.save(directory + "/" + filename + "/" + filename + "_bb", self.bboxes)
        numpy.save(directory + "/" + filename + "/" + filename + "_ch", self.curvature_hist)
        numpy.save(directory + "/" + filename + "/" + filename + "_ef", self.eigen_features)
        
        self.verticesAsString = self.vertices.tostring()
        
    def loadOBJModel(self, path, segpath=''):
        
        self.__init__(True)
        
        print 'Opening Model...'
        model = open(path, 'r')

        start = time()
        vertCount = 0
        texCoordCount = 0
        faceCount = 0
        normalCount = 0
        
        for line in model:
            if line[0:2] == 'v ':
                vertCount += 1
            elif line[0] == 'f':
                faceCount += 1
            elif line[0:2] == 'vt':
                texCoordCount += 1
            elif line[0:2] == 'vn':
                normalCount += 1
        print '\tVertices counted in %f' % (time() - start)
        print '\t %d vertices detected' % (vertCount)
        print '\t %d faces detected' % (faceCount)
        print '\t %d tex coords detected' % (texCoordCount)
        print '\t %d normals detected' % (normalCount)
        
        self.vertexCount = int (vertCount)
        self.faceCount = int (faceCount)
        self.texCoordCount = int (texCoordCount)
        self.normalCount = int (normalCount)

        start = time()
        tempVertices = numpy.zeros ((self.vertexCount, 3), 'f')
        tempNormals = numpy.zeros ((self.normalCount, 3), 'f')
        tempTexCoords = numpy.zeros ((self.texCoordCount, 2), 'f')
        
        self.vertices = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.normals = numpy.zeros ((self.faceCount * 3, 3), 'f')
        self.texCoords = numpy.zeros ((self.faceCount * 3, 2), 'f')

        print "\tFinal counts"
        print "\t Vertices = %d - Normals = %d - Tex Coords = %d" % ( len(self.vertices), len(self.normals), len(self.texCoords) )
        print '\tVectors initialized in %f' % (time() - start)

        vIndex = 0
        tIndex = 0
        nIndex = 0

        start = time()
        #Retriving set of vertices in the mesh
        model = open(path, 'r')
        for line in model:
            if line[0:2] == 'v ':
                coords = line[2:].strip().split(' ')
                #print '(%s, %s, %s)' % (coords[0], coords[1], coords[2])
                tempVertices[vIndex, 0] = float(coords[0])
                tempVertices[vIndex, 1] = float(coords[1])
                tempVertices[vIndex, 2] = float(coords[2])
                vIndex += 1
                
            if line[0:2] == 'vt':
                #Tex Coords
                tempTexCoords[tIndex, 0] = 1.0
                tempTexCoords[tIndex, 1] =  0.0
                tIndex += 1
                
            if line[0:2] == 'vn':
                coords = line[3:].strip().split(' ')
                tempNormals[nIndex, 0] = float(coords[0])
                tempNormals[nIndex, 1] = float(coords[1])
                tempNormals[nIndex, 2] = float(coords[2])
                nIndex += 1
                
        print '\t+Data retrieved in %f' % (time() - start)
        print 'V = %d --- N = %d' % (len(tempVertices), len(tempNormals)) 
        
        start = time()
        vIndex = 0
        tIndex = 0
        nIndex = 0
        model = open(path, 'r')

        zeroBased = False
        offset = 1
        if (zeroBased):
            offset = 0    

        trianglesC = 0
        quadC = 0
        polyC = 0
        
        for line in model:
            if line[0] == 'f':
                verticesData = line[2:].strip().split(' ')

                if len(verticesData) == 3:
                    trianglesC += 1
                    #Triangle
                    for data in verticesData:
                        vertexInfo = data.split('/')
                        for vi in vertexInfo:
                            if (vi < 0):
                                vi *= -1
                                
                        if (len(vertexInfo) == 2):
                            #Vertex index/Vertex Tex index
                            self.vertices[vIndex, 0] = tempVertices[int(vertexInfo[0]) - offset, 0]
                            self.vertices[vIndex, 1] = tempVertices[int(vertexInfo[0]) - offset, 1]
                            self.vertices[vIndex, 2] = tempVertices[int(vertexInfo[0]) - offset, 2]
                        
                            self.texCoords[tIndex, 0] = tempTexCoords[int(vertexInfo[1]) - offset, 0]
                            self.texCoords[tIndex, 1] = tempTexCoords[int(vertexInfo[1]) - offset, 1]
                            
                        elif (len(vertexInfo) == 3):
                            #Vertex index/Normal Index/Vertex Tex index
                            self.vertices[vIndex, 0] = tempVertices[int(vertexInfo[0]) - offset, 0]
                            self.vertices[vIndex, 1] = tempVertices[int(vertexInfo[0]) - offset, 1]
                            self.vertices[vIndex, 2] = tempVertices[int(vertexInfo[0]) - offset, 2]
                            if(vertexInfo[1] != ''):
                                self.texCoords[tIndex, 0] = tempTexCoords[int(vertexInfo[1]) - offset, 0]
                                self.texCoords[tIndex, 1] = tempTexCoords[int(vertexInfo[1]) - offset, 1]
                            
                            self.normals[nIndex, 0] = tempNormals[int(vertexInfo[2]) - offset, 0]
                            self.normals[nIndex, 1] = tempNormals[int(vertexInfo[2]) - offset, 1]
                            self.normals[nIndex, 2] = tempNormals[int(vertexInfo[2]) - offset, 2]
                            nIndex += 1
                        
                        vIndex += 1
                        tIndex += 1
                        
                elif len(verticesData) == 4:
                    #Quad
                    quadC += 1
                                      
                    for x in [1,2,3]:
                        vertexInfo = verticesData[x].split('/')
                        for vi in vertexInfo:
                            if (vi < 0):
                                vi *= -1
                                
                        if (len(vertexInfo) == 2):
                            #Vertex index/Vertex Tex index
                            self.vertices[vIndex, 0] = tempVertices[int(vertexInfo[0]) - offset, 0]
                            self.vertices[vIndex, 1] = tempVertices[int(vertexInfo[0]) - offset, 1]
                            self.vertices[vIndex, 2] = tempVertices[int(vertexInfo[0]) - offset, 2]
                        
                            self.texCoords[tIndex, 0] = tempTexCoords[int(vertexInfo[1]) - offset, 0]
                            self.texCoords[tIndex, 1] = tempTexCoords[int(vertexInfo[1]) - offset, 1]
                        elif (len(vertexInfo) == 3):
                            #Vertex index/Normal Index/Vertex Tex index
                            self.vertices[vIndex, 0] = tempVertices[int(vertexInfo[0]) - offset, 0]
                            self.vertices[vIndex, 1] = tempVertices[int(vertexInfo[0]) - offset, 1]
                            self.vertices[vIndex, 2] = tempVertices[int(vertexInfo[0]) - offset, 2]
                        
                            self.texCoords[tIndex, 0] = tempTexCoords[int(vertexInfo[1]) - offset, 0]
                            self.texCoords[tIndex, 1] = tempTexCoords[int(vertexInfo[1]) - offset, 1]
                            
                            self.normals[nIndex, 0] = tempNormals[int(vertexInfo[2]) - offset, 0]
                            self.normals[nIndex, 1] = tempNormals[int(vertexInfo[2]) - offset, 1]
                            self.normals[nIndex, 2] = tempNormals[int(vertexInfo[2]) - offset, 2]
                            nIndex += 1

                    vIndex += 1
                    tIndex += 1
                    
                    '''
                    for x in [0,2,3]:
                        vertexInfo = verticesData[x].split('/')
                        for vi in vertexInfo:
                            if (vi < 0):
                                vi *= -1
                                
                        if (len(vertexInfo) == 2):
                            #Vertex index/Vertex Tex index
                            self.vertices[vIndex, 0] = tempVertices[int(vertexInfo[0]) - offset, 0]
                            self.vertices[vIndex, 1] = tempVertices[int(vertexInfo[0]) - offset, 1]
                            self.vertices[vIndex, 2] = tempVertices[int(vertexInfo[0]) - offset, 2]
                        
                            self.texCoords[tIndex, 0] = tempTexCoords[int(vertexInfo[1]) - offset, 0]
                            self.texCoords[tIndex, 1] = tempTexCoords[int(vertexInfo[1]) - offset, 1]
                        elif (len(vertexInfo) == 3):
                            #Vertex index/Normal Index/Vertex Tex index
                            self.vertices[vIndex, 0] = tempVertices[int(vertexInfo[0]) - offset, 0]
                            self.vertices[vIndex, 1] = tempVertices[int(vertexInfo[0]) - offset, 1]
                            self.vertices[vIndex, 2] = tempVertices[int(vertexInfo[0]) - offset, 2]
                        
                            self.texCoords[tIndex, 0] = tempTexCoords[int(vertexInfo[1]) - offset, 0]
                            self.texCoords[tIndex, 1] = tempTexCoords[int(vertexInfo[1]) - offset, 1]
                            
                            self.normals[nIndex, 0] = tempNormals[int(vertexInfo[2]) - offset, 0]
                            self.normals[nIndex, 1] = tempNormals[int(vertexInfo[2]) - offset, 1]
                            self.normals[nIndex, 2] = tempNormals[int(vertexInfo[2]) - offset, 2]

                    vIndex += 1
                    tIndex += 1
                    nIndex += 1
                    '''
                else:
                    #Poly
                    polyC += 1
                
        self.verticesAsString = self.vertices.tostring()
        self.texCoordsAsString = self.texCoords.tostring()
        print "Triangles loaded: %d " % trianglesC
        print "Quad loaded: %d " % quadC
        print "Poly loaded: %d " % polyC
        print '\t+Faces and normals loaded in %f' % (time() - start)
        #print self.verticesAsString


    def buildVBOs (self):
        global g_fVBOSupported
        
        ''' Generate And Bind The Vertex Buffer '''
        if (g_fVBOSupported):
            self.VBOVertices = int(glGenBuffersARB( 1))                    # Get A Valid Name
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOVertices )       # Bind The Buffer
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.vertices, GL_STATIC_DRAW_ARB )

            # Generate And Bind The Texture Coordinate Buffer
            self.VBOTexCoords = int(glGenBuffersARB( 1))
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOTexCoords )
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.texCoords, GL_STATIC_DRAW_ARB )

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
