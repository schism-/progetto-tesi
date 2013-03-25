'''
Created on 11/mar/2013

@author: Christian
'''

import vtk
from utility.mmesh import *
import random

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

vertices, faces = readofffile( '../res/chairs/shapes/103.off' )
print "Vertices: " + str(len(vertices))
print "Faces: " + str(len(faces)) + "("+ str(len(faces) * 3) +")"

segmentVertices = numpy.load('../res/chairs/json/103/103_sv.npy')

basePoints = vtk.vtkPoints()
for v in vertices:
    basePoints.InsertNextPoint(v)

rand = random.Random()
rand.seed(time())
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
                tris[i].InsertNextCell(poly.GetPointIds())
    i += 1

for k in range(len(segmentVertices)):
    polys[k].SetPoints(pts[k])
    polys[k].SetPolys(tris[k])
    polys[k].Update()

for k in range(len(segmentVertices)):
    print "%d: %d - %d" % (k, polys[k].GetNumberOfPoints(), polys[k].GetNumberOfPolys(), )

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

filteredMeshes = []
trees= []
print
for k in range(len(segmentVertices)):
    if len(segmentVertices[k]) > 0:
        clean = vtk.vtkCleanPolyData()
        clean.PointMergingOff()
        clean.AddInput(polys[k])
        clean.Update()
        filteredMeshes.append(clean.GetOutput())
        
        print "%d: %d - %d" % (k, clean.GetOutput().GetNumberOfPoints(), clean.GetOutput().GetNumberOfPolys(), )

        dataMapper = vtk.vtkPolyDataMapper()
        dataMapper.SetInput(clean.GetOutput())
        model = vtk.vtkActor()
        model.SetMapper(dataMapper)
        model.GetProperty().SetColor(rand.random(),0.2,rand.random())
        
        ren.AddActor(model)

print
print filteredMeshes

b = vtk.vtkBooleanOperationPolyDataFilter()
b.SetOperationToIntersection()
b.SetTolerance(0.1)
b.SetInput(0, filteredMeshes[2])
b.SetInput(1, filteredMeshes[1])
b.Update()

print b.GetOutput(1).GetPoints()
points = b.GetOutput(1).GetPoints()
vertices = vtk.vtkCellArray()

for x in range(points.GetNumberOfPoints()):
    vertices.InsertNextCell(1)
    vertices.InsertCellPoint(x)

points.Modified()
vertices.Modified()

data = vtk.vtkPolyData()
data.SetPoints(points)
data.SetVerts(vertices)
dataMapper = vtk.vtkPolyDataMapper()
dataMapper.SetInput(data)

model = vtk.vtkActor()
model.SetMapper(dataMapper)
model.GetProperty().SetColor(0.0, 1.0, 0.0)
model.GetProperty().SetPointSize(8.0)

ren.AddActor(model)

ren.SetBackground(0.1,0.2,0.4)
renWin.SetSize(500,500)
iren.Initialize()
iren.Start()
