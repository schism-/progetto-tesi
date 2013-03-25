'''
Created on 25/feb/2013

@author: Christian
'''

from utility.mmesh import *
from myMesh import *
from scipy.spatial import *
import numpy
import gc

mesh = mMesh(True)
loadModel(mesh, '../../res/chairs/json', '101')
 
 
 
#Computing OBB for all segmented components
segments_mesh = []
for s in mesh.segmentVertices:
    vertices = numpy.zeros ((len(s), 3), 'f')
    vIndex = 0
    for idx in s:
        vertices[vIndex, 0] = mesh.vertices[idx[0], 0]
        vertices[vIndex, 1] = mesh.vertices[idx[0], 1]
        vertices[vIndex, 2] = mesh.vertices[idx[0], 2]
        vIndex += 1
    segments_mesh.append(vertices)
    
A = segments_mesh[0]
B = segments_mesh[1]
print len(A)
print len(B)

#Y = distance.cdist(A, B, 'euclidean')
gc.collect()
d0 = numpy.subtract.outer(A[:,0], B[:,0])
gc.collect()
d1 = numpy.subtract.outer(A[:,1], B[:,1])
gc.collect()
numpy.hypot(d0, d1)

