'''
Created on 19/mar/2013

@author: Christian
'''

import vtk
import numpy
from utility.mmesh import *
import random

def polydataToArray(poly):
    print "Converting..."
    print "Vert count: %d" % (poly.GetNumberOfPoints())
    print "Face count: %d" % (poly.GetNumberOfPolys())
    verts = numpy.zeros ((poly.GetNumberOfPoints(), 3), 'f')
    faces = numpy.zeros ((poly.GetNumberOfPolys(), 3), 'i')

    vertsArray = poly.GetPoints()
    facesArray = poly.GetPolys()
    facesArray.InitTraversal()

    for pIdx in range(poly.GetNumberOfPoints()):
        p = vertsArray.GetPoint(pIdx)
        verts[pIdx] = p
     
    for fIdx in range(poly.GetNumberOfPolys()):
        v = vtk.vtkIdList()
        facesArray.GetNextCell(v)
        faces[fIdx] = v.GetId(0), v.GetId(1), v.GetId(2)
        
    return verts, faces

def arrayToPolydata(verts, faces):
    pts = vtk.vtkPoints()
    tris = vtk.vtkCellArray()

    for v in verts:
        pts.InsertNextPoint( [v[0], v[1], v[2]] )
    for f in faces:
        poly = vtk.vtkPolygon()
        poly.GetPointIds().InsertId(0,f[0])
        poly.GetPointIds().InsertId(1,f[1])
        poly.GetPointIds().InsertId(2,f[2])
        tris.InsertNextCell(poly.GetPointIds())
        
    return pts, tris

def computeComponents(vertices, faces):
    pts, tris = arrayToPolydata(vertices, faces)
    polys = vtk.vtkPolyData()
    polys.SetPoints(pts)
    polys.SetPolys(tris)
    polys.Update()
    
    cleanFilter = vtk.vtkCleanPolyData()
    #cleanFilter.PointMergingOff()
    cleanFilter.ConvertStripsToPolysOff()
    cleanFilter.ConvertPolysToLinesOff()
    cleanFilter.ConvertLinesToPointsOff()
    cleanFilter.SetInput(polys)
    cleanFilter.Update()
    
    connFilter = vtk.vtkPolyDataConnectivityFilter()
    connFilter.ScalarConnectivityOff()
    connFilter.SetExtractionModeToAllRegions()
    connFilter.SetInput(cleanFilter.GetOutput())
    connFilter.Update()
    
    nregions = connFilter.GetNumberOfExtractedRegions()
    print "Regions extracted: %d" % (nregions)
    
    components = []
    for i in range(nregions):
        connFilter = vtk.vtkPolyDataConnectivityFilter()
        connFilter.ScalarConnectivityOff()
        connFilter.SetExtractionModeToSpecifiedRegions()
        connFilter.AddSpecifiedRegion(i)
        connFilter.SetInput(cleanFilter.GetOutput())
        connFilter.Update()
    
        cFilter = vtk.vtkCleanPolyData()
#        cFilter.ConvertStripsToPolysOff()
#        cFilter.ConvertPolysToLinesOff()
#        cFilter.ConvertLinesToPointsOff()
        cFilter.SetInput(connFilter.GetOutput())
        cFilter.Update()
    
        v,f = polydataToArray(cFilter.GetOutput())
        components.append([v,f])
        
    return components

def computeComponentsWithGUI(vertices, faces):
    #Rendering
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    pts, tris = arrayToPolydata(vertices, faces)
    polys = vtk.vtkPolyData()
    polys.SetPoints(pts)
    polys.SetPolys(tris)
    polys.Update()
    
    dataMapper = vtk.vtkPolyDataMapper()
    dataMapper.SetInput(polys)
    model = vtk.vtkActor()
    model.SetMapper(dataMapper)
    model.GetProperty().SetColor(0.0, 1.0, 0.0)
    model.GetProperty().SetPointSize(8.0)
    ren.AddActor(model)
    
    cleanFilter = vtk.vtkCleanPolyData()
    #cleanFilter.PointMergingOff()
    cleanFilter.ConvertStripsToPolysOff()
    cleanFilter.ConvertPolysToLinesOff()
    cleanFilter.ConvertLinesToPointsOff()
    cleanFilter.SetInput(polys)
    cleanFilter.Update()
    
    connFilter = vtk.vtkPolyDataConnectivityFilter()
    connFilter.ScalarConnectivityOff()
    connFilter.SetExtractionModeToAllRegions()
    connFilter.SetInput(cleanFilter.GetOutput())
    connFilter.Update()
    
    nregions = connFilter.GetNumberOfExtractedRegions()
    print "Regions extracted: %d" % (nregions)
    
    components = []
    for i in range(nregions):
        connFilter = vtk.vtkPolyDataConnectivityFilter()
        connFilter.ScalarConnectivityOff()
        connFilter.SetExtractionModeToSpecifiedRegions()
        connFilter.AddSpecifiedRegion(i)
        connFilter.SetInput(cleanFilter.GetOutput())
        connFilter.Update()
    
        cFilter = vtk.vtkCleanPolyData()
        cFilter.ConvertStripsToPolysOff()
        cFilter.ConvertPolysToLinesOff()
        cFilter.ConvertLinesToPointsOff()
        cFilter.SetInput(connFilter.GetOutput())
        cFilter.Update()
    
        v,f = polydataToArray(cFilter.GetOutput())
        components.append([v,f])
        print [v,f]
        extractedMapper = vtk.vtkPolyDataMapper()
        extractedMapper.SetInputConnection(connFilter.GetOutputPort())
        extractedMapper.Update()
     
        extractedActor = vtk.vtkActor()
        extractedActor.GetProperty().SetColor( random.random(), 0.0, random.random() )
        extractedActor.SetMapper(extractedMapper)
        
        ren.AddActor(extractedActor)
        
    ren.SetBackground(0.1,0.2,0.4)
    renWin.SetSize(500,500)
    iren.Initialize()
    iren.Start()
    
    return components
    
if __name__ == "__main__":
    m = mMesh(True)
    m.loadOFFModel("../res/tele-aliens/shapes/42.off", "../res/tele-aliens/gt/42.seg")
    seg = m.segments[1]
    cList = seg.getComponents()
    print "Final components: %d" % (len(cList))