'''
Created on 11/mar/2013

@author: Christian
'''

import vtk
import numpy
from utility.mmesh import *
import random
import collections

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

def polydataToArray(poly):
    verts = numpy.zeros ((poly.GetNumberOfPoints(), 3), 'f')

    vertsArray = poly

    for pIdx in range(poly.GetNumberOfPoints()):
        p = vertsArray.GetPoint(pIdx)
        verts[pIdx] = p
        
    return verts

def computeContactPoints(mesh):
    print "Computing contact points..."
    
    segments = mesh.segments
    components = mesh.components
    
    adjacency_info_2 = collections.defaultdict(dict)
    contact_slots_2 = collections.defaultdict(dict)
    for seg in components.keys():
        contact_slots_2[seg] = collections.defaultdict(list)
        adjacency_info_2[seg] = collections.defaultdict(int)
        
    polys   = {}
    for seg in components.keys():
        for c in components[seg]:
            if not c.segmentId in polys:
                polys[c.segmentId] = []
            pts, tris = arrayToPolydata(c.vertices, c.faces)
            poly = vtk.vtkPolyData()
            poly.SetPoints(pts)
            poly.SetPolys(tris)
            poly.Update()
            polys[c.segmentId].append(poly)
        
    s_keys = polys.keys()
    vertices = vtk.vtkCellArray()
    points = vtk.vtkPoints()
    for x in range(len(s_keys) - 1):
        for y in range(x+1, len(s_keys)):
            for id_x, c_x in enumerate(polys[s_keys[x]]):
                for id_y, c_y in enumerate(polys[s_keys[y]]):
                    b = vtk.vtkBooleanOperationPolyDataFilter()
                    b.SetOperationToIntersection()
                    b.SetTolerance(0.1)
                    b.SetInput(0, c_x)
                    b.SetInput(1, c_y)
                    b.Update()
            
                    p = b.GetOutput(1).GetPoints()
                    if (p.GetNumberOfPoints() > 0):
                        print "Found %d contact points between segment #%d-%d and segment #%d-%d" % (p.GetNumberOfPoints(), s_keys[x], id_x, s_keys[y], id_y)
                        for k in range(p.GetNumberOfPoints()):
                            id = points.InsertNextPoint(p.GetPoint(k))
                            vertices.InsertNextCell(1)
                            vertices.InsertCellPoint(id)
                        
                        res_points = numpy.array(polydataToArray(p))
                        
                        d_x = dict()
                        d_x['points'] = res_points
                        d_x['seg'] = s_keys[y]
                        d_x['comp'] = id_y
                        contact_slots_2[s_keys[x]][id_x].append(d_x)
                        d_y = dict()
                        d_y['points'] = res_points
                        d_y['seg'] = s_keys[x]
                        d_y['comp'] = id_x
                        contact_slots_2[s_keys[y]][id_y].append(d_y)

                        adjacency_info_2[s_keys[x]][s_keys[y]] += 1
                        adjacency_info_2[s_keys[y]][s_keys[x]] += 1
            
                    points.Modified()
                    vertices.Modified()
    
    print "Adjacency info"
    for k in s_keys:
        s = "\t %d | " % k
        for k_2 in s_keys:
            s += " %d |" % (adjacency_info_2[k][k_2])
        print s
    
    for s_k, s_v in contact_slots_2.items():
        print "Segment %d" % s_k
        for c_k, c_v in s_v.items():
            print "\t Component %d" % c_k
            for data in c_v:
                print "\t\t Seg: %d Comp: %d Points: %d" % (data['seg'], data['comp'], len(data['points']))
                
    return adjacency_info_2, contact_slots_2

def computeContactPointsWithGUI(mesh):
    print "Computing contact points..."
    
    rand = random.Random()
    rand.seed(time())
    
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    segments = mesh.segments
    components = mesh.components
    
    adjacency_info = numpy.zeros (( len(components.keys()) , len(components.keys()) ), 'd') 
    contact_slots = {}
    adjacency_info_2 = collections.defaultdict(dict)
    contact_slots_2 = collections.defaultdict(dict)
    for seg in components.keys():
        contact_slots[seg] = [None, ] * len(components[seg])
        contact_slots_2[seg] = collections.defaultdict(list)
        adjacency_info_2[seg] = collections.defaultdict(int)
        
    polys   = {}
    for seg in components.keys():
        for c in components[seg]:
            if not c.segmentId in polys:
                polys[c.segmentId] = []
            pts, tris = arrayToPolydata(c.vertices, c.faces)
            poly = vtk.vtkPolyData()
            poly.SetPoints(pts)
            poly.SetPolys(tris)
            poly.Update()
            polys[c.segmentId].append(poly)
        
    legend = vtk.vtkLegendBoxActor()
    legend.SetNumberOfEntries( len(segments.keys()) )
    legendSphereSource = vtk.vtkSphereSource()
    legendSphere = legendSphereSource.GetOutput()
    leg = 0
    for segIdx in segments.keys():
        segColor = [rand.random(),0.2,rand.random()] 
        for c in polys[segIdx]:
            dataMapper = vtk.vtkPolyDataMapper()
            dataMapper.SetInput(c)
            model = vtk.vtkActor()
            model.SetMapper(dataMapper)
            model.GetProperty().SetColor(segColor)
            ren.AddActor(model)
            print "%d: V%d - P%d" % (segIdx, c.GetNumberOfPoints(), c.GetNumberOfPolys() )
        
        legend.SetEntry(leg, legendSphere, "Segment #" + str(segIdx), segColor)
        leg += 1
        
        
    s_keys = polys.keys()
    vertices = vtk.vtkCellArray()
    points = vtk.vtkPoints()
    for x in range(len(s_keys) - 1):
        for y in range(x+1, len(s_keys)):
            for id_x, c_x in enumerate(polys[s_keys[x]]):
                for id_y, c_y in enumerate(polys[s_keys[y]]):
                    b = vtk.vtkBooleanOperationPolyDataFilter()
                    b.SetOperationToIntersection()
                    b.SetTolerance(0.1)
                    b.SetInput(0, c_x)
                    b.SetInput(1, c_y)
                    b.Update()
            
                    p = b.GetOutput(1).GetPoints()
                    if (p.GetNumberOfPoints() > 0):
                        print "Found %d contact points between segment #%d-%d and segment #%d-%d" % (p.GetNumberOfPoints(), s_keys[x], id_x, s_keys[y], id_y)
                        for k in range(p.GetNumberOfPoints()):
                            id = points.InsertNextPoint(p.GetPoint(k))
                            vertices.InsertNextCell(1)
                            vertices.InsertCellPoint(id)
                        
                        res_points = numpy.array(polydataToArray(p))
                        contact_slots[s_keys[x]][id_x] = res_points
                        contact_slots[s_keys[y]][id_y] = res_points
                        
                        d_x = dict()
                        d_x['points'] = res_points
                        d_x['seg'] = s_keys[y]
                        d_x['comp'] = id_y
                        contact_slots_2[s_keys[x]][id_x].append(d_x)
                        
                        d_y = dict()
                        d_y['points'] = res_points
                        d_y['seg'] = s_keys[x]
                        d_y['comp'] = id_x
                        contact_slots_2[s_keys[y]][id_y].append(d_y)
                        
                        adjacency_info[x,y] += 1
                        adjacency_info[y,x] += 1
                        
                        adjacency_info_2[s_keys[x]][s_keys[y]] += 1
                        adjacency_info_2[s_keys[y]][s_keys[x]] += 1
            
                    points.Modified()
                    vertices.Modified()
    
    print "Adjacency info"
    for k in s_keys:
        s = "\t %d | " % k
        for k_2 in s_keys:
            s += " %d |" % (adjacency_info_2[k][k_2])
        print s
    
    for s_k, s_v in contact_slots_2.items():
        print "Segment %d" % s_k
        for c_k, c_v in s_v.items():
            print "\t Component %d" % c_k
            for data in c_v:
                print "\t\t Seg: %d Comp: %d Points: %d" % (data['seg'], data['comp'], len(data['points']))
                
    
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
    
    ren.AddActor(legend)
    
    ren.SetBackground(0.1,0.2,0.4)
    renWin.SetSize(500,500)
    iren.Initialize()
    iren.Start()

if __name__ == "__main__":
    m = mMesh(True)
    m.loadOFFModel("../res/tele-aliens/shapes/42.off", "../res/tele-aliens/gt/42.seg")
    
    computeContactPoints(m)