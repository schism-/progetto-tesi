import numpy
from time import time

from OpenGL.GL.ARB.vertex_buffer_object import *

g_fVBOSupported = False;    # ARB_vertex_buffer_object supported?

class mMesh:
    def __init__(self, vbo):

        global g_fVBOSupported
        g_fVBOSupported = vbo
        
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

        self.VBOVertices = None
        self.VBOTexCoords = None
        self.VBONormals = None

    def loadOBJModel(self, path):

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
            self.VBOVertices = int(glGenBuffersARB( 1));                    # Get A Valid Name
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOVertices );       # Bind The Buffer
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.vertices, GL_STATIC_DRAW_ARB );

            # Generate And Bind The Texture Coordinate Buffer
            self.VBOTexCoords = int(glGenBuffersARB( 1));
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBOTexCoords );
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.texCoords, GL_STATIC_DRAW_ARB );

            self.VBONormals = int(glGenBuffersARB( 1));
            glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.VBONormals );
            # Load The Data
            glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.normals, GL_STATIC_DRAW_ARB );

            #Our Copy Of The Data Is No Longer Necessary, It Is Safe In The Graphics Card
            #self.vertices = None
            #self.texCoords = None
