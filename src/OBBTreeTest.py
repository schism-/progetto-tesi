'''
Created on 11/mar/2013

@author: Christian
'''

import vtk
from utility.mmesh import *
import random

class vtkOBBTree2(vtk.vtkOBBTree):
    def test(self):
        return self.vtkOBBTree__Tree
    
    
def readofffile(offpath):
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

vertices, faces = readofffile( '../res/chairs/shapes/18.off' )
print "Vertices: " + str(len(vertices))
print "Faces: " + str(len(faces)) + "("+ str(len(faces) * 3) +")"


segmentVertices = numpy.load('../res/chairs/json/18/18_sv.npy')

basePoints = vtk.vtkPoints()
for v in vertices:
    basePoints.InsertNextPoint(v)


pts     = []
tris    = []
polys   = []
for k in range(len(segmentVertices)):
    pts.append(vtk.vtkPoints())
    tris.append(vtk.vtkCellArray())
    polys.append(vtk.vtkPolyData())

for f in faces:
    for vIdx in f:
        for i in range(len(segmentVertices)):
            if(len(segmentVertices[i]) > 0):
                pts[i].InsertNextPoint( basePoints.GetPoint(vIdx))

#for v in vertices:
#    for i in range(1, len(segmentVertices)):
#        pts[i].InsertNextPoint(v)



i = 0
for v in segmentVertices:
    print "Len of %d is %d" % (i, len(v))
    if len(v) > 0:
        for f in range(len(v)):
            if (f % 3 == 0):
                poly = vtk.vtkPolygon()
                poly.GetPointIds().InsertId(0,v[f])
                poly.GetPointIds().InsertId(1,v[f + 1])
                poly.GetPointIds().InsertId(2,v[f + 2])
                #print "(%d, %d, %d)" % (v[f], v[f+1], v[f+2])
                #exit(0)
                tris[i].InsertNextCell(poly.GetPointIds())
    i += 1

for k in range(len(segmentVertices)):
    polys[k].SetPoints(pts[k])
    polys[k].SetPolys(tris[k])
    polys[k].Update()

for k in range(len(segmentVertices)):
    print "%d: %d - %d" % (k, polys[k].GetNumberOfPoints(), polys[k].GetNumberOfPolys(), )

#exit(0)

#filtering

filteredMeshes = []
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

trees= []

for k in range(len(segmentVertices)):
    if len(segmentVertices[k]) > 0:
        print "start segment %d" % (k)
        tri_2 = vtk.vtkTriangleFilter()
        tri_2.SetInput(polys[k])
        tri_2.Update()
        print "filtered segment %d" % (k)
        
        cleaner_2 = vtk.vtkCleanPolyData()
        cleaner_2.SetInputConnection(tri_2.GetOutputPort())
        cleaner_2.SetTolerance(0.005)
        cleaner_2.Update()
        print "cleaned segment %d" % (k)
        
        dataMapper = vtk.vtkPolyDataMapper()
        dataMapper.SetInput(cleaner_2.GetOutput())
        model = vtk.vtkActor()
        model.SetMapper(dataMapper)
        model.GetProperty().SetColor(random.random(),random.random(),random.random())
        print "data mapped segment %d" % (k)
        
        obb = vtk.vtkKdTree()
        obb.SetDataSet(cleaner_2.GetOutput())
        obb.AutomaticOff()
        obb.SetMaxLevel(30)
        obb.SetMinCells(10)
        obb.BuildLocator()
        poly = vtk.vtkPolyData()
        
        obb.GenerateRepresentation(20, poly)
        
        #obb.PrintTree()
        
        octreeMapper = vtk.vtkPolyDataMapper()
        octreeMapper.SetInputConnection(poly.GetProducerPort())
     
        octreeActor = vtk.vtkActor()
        octreeActor.SetMapper(octreeMapper)
        octreeActor.GetProperty().SetInterpolationToFlat()
#        octreeActor.GetProperty().SetAmbient(1)
#        octreeActor.GetProperty().SetDiffuse(0)
        octreeActor.GetProperty().SetRepresentationToWireframe()
        
        '''
        boxes = vtk.vtkSpatialRepresentationFilter()
        boxes.SetInput(cleaner_2.GetOutput())
        boxes.SetSpatialRepresentation(obb)
        boxMapper = vtk.vtkPolyDataMapper()
        boxMapper.SetInput(boxes.GetOutput())
        
#        obb.SetDataSet(cleaner_2.GetOutput())
#        obb.BuildLocator()
#        trees.append(obb)

        boxActor = vtk.vtkActor()
        boxActor.SetMapper(boxMapper)
        boxActor.GetProperty().SetAmbient(1)
        boxActor.GetProperty().SetDiffuse(0)
        boxActor.GetProperty().SetRepresentationToWireframe()
        print "obbtree segment %d" % (k)
        '''
        # Add the actors to the renderer, set the background and size
        #
        ren.AddActor(model)
        ren.AddActor(octreeActor)
        
        #break
    
    
#print trees
#print dir(trees[0])
    
ren.SetBackground(0.1,0.2,0.4)

renWin.SetSize(500,500)
#ren.GetActiveCamera().Zoom(-3.0)

iren.Initialize()

iren.Start()


print "Done!"


