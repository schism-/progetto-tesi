import vtk
from mmesh import *


class CurvaturesDemo():
    
    @staticmethod
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
     
    def CurvaturesDemo(self):
 
        pts = vtk.vtkPoints()
        tris = vtk.vtkCellArray()
        
        polys = vtk.vtkPolyData()
        
        vertices, faces = self.readofffile( '../../res/chairs/shapes/101.off' )
        print "Vertices: " + str(len(vertices))
        print "Faces: " + str(len(faces))
 
        for v in vertices:
            pts.InsertNextPoint(v)
        
        for f in faces:
            poly = vtk.vtkPolygon()
            x = 0
            for p in f:
                poly.GetPointIds().InsertId(x,p)
                x+=1
            tris.InsertNextCell(poly.GetPointIds())
            
        polys.SetPoints(pts)
        polys.SetPolys(tris)
        polys.Update()
        
        tri_2 = vtk.vtkTriangleFilter()
        tri_2.SetInput(polys)
 
        # The quadric has nasty discontinuities from the way the edges are generated
        # so let's pass it though a CleanPolyDataFilter and merge any points which
        # are coincident, or very close
        cleaner_2 = vtk.vtkCleanPolyData()
        cleaner_2.SetInputConnection(tri_2.GetOutputPort())
        cleaner_2.SetTolerance(0.005)
        
        # Now we have the sources, lets put them into a list.
        sources = list()
        sources.append(cleaner_2)
        sources.append(cleaner_2)
        sources.append(cleaner_2)
        sources.append(cleaner_2)
 
        # Colour transfer function.
        ctf = vtk.vtkColorTransferFunction()
        ctf.SetColorSpaceToDiverging()
        ctf.AddRGBPoint(0.0, 0.230, 0.299, 0.754)
        ctf.AddRGBPoint(1.0, 0.706, 0.016, 0.150)
        cc = list()
        for i in range(256):
            cc.append(ctf.GetColor(float(i) / 255.0)) 
 
        # Lookup table.
        lut = list()
        for idx in range(len(sources)):
            lut.append(vtk.vtkLookupTable())
            lut[idx].SetNumberOfColors(256)
            for i, item in enumerate(cc):
                lut[idx].SetTableValue(i, item[0], item[1], item[2], 1.0)
            if idx == 0:
                lut[idx].SetRange(-10, 10)
            if idx == 1:
                lut[idx].SetRange(-10, 10)
            if idx == 2:
                lut[idx].SetRange(-10, 10)
            if idx == 3:
                lut[idx].SetRange(0, 4)
            lut[idx].Build()
 
        curvatures = list()        
        curvatures.append(vtk.vtkCurvatures())
        curvatures.append(vtk.vtkCurvatures())
        curvatures.append(vtk.vtkCurvatures())
        curvatures.append(vtk.vtkCurvatures())
        
        curvatures[0].SetCurvatureTypeToMaximum()
        curvatures[1].SetCurvatureTypeToMinimum()
        curvatures[2].SetCurvatureTypeToGaussian()
        curvatures[3].SetCurvatureTypeToMean()
        
        renderers = list()
        mappers = list()
        actors = list()
        textmappers = list()
        textactors = list()
 
        # Create a common text property.
        textProperty = vtk.vtkTextProperty()
        textProperty.SetFontSize(10)
        textProperty.SetJustificationToCentered()
 
        names = ['Torus - Maximum Curvature', 'Torus - Minimum Curvature', 'Torus - Gaussian Curvature', 'Torus - Mean Curvature']
 
        # Link the pipeline together. 
        for idx, item in enumerate(sources):
            sources[idx].Update()
 
            curvatures[idx].SetInputConnection(sources[idx].GetOutputPort())
 
            mappers.append(vtk.vtkPolyDataMapper())
            mappers[idx].SetInputConnection(curvatures[idx].GetOutputPort())
            mappers[idx].SetLookupTable(lut[idx])
            mappers[idx].SetUseLookupTableScalarRange(1)
 
            actors.append(vtk.vtkActor())
            actors[idx].SetMapper(mappers[idx])
 
            textmappers.append(vtk.vtkTextMapper())
            textmappers[idx].SetInput(names[idx])
            textmappers[idx].SetTextProperty(textProperty)
 
            textactors.append(vtk.vtkActor2D())
            textactors[idx].SetMapper(textmappers[idx])
            textactors[idx].SetPosition(150, 16)
 
            renderers.append(vtk.vtkRenderer())

        '''
        xyPlotActor = vtk.vtkXYPlotActor()
        reader = vtk.vtkXMLImageDataReader()
        actor = vtk.vtkActor()
        histogram = vtk.vtkImageAccumulate()
        imageExtractComponents = vtk.vtkImageExtractComponents()
        barChartActor = vtk.vtkBarChartActor()
        style = vtk.vtkInteractorStyleImage()
        imageScale = 1
        renderer_his = vtk.vtkRenderer()
        '''
        gridDimensions = 2
 
        for idx in range(len(sources)):
            if idx < gridDimensions * gridDimensions:
                renderers.append(vtk.vtkRenderer)
 
        rendererSize = 300
 
        # Create the RenderWindow
        #
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(rendererSize * gridDimensions, rendererSize * gridDimensions)
 
        # Add and position the renders to the render window.
        viewport = list()
        for row in range(gridDimensions):
            for col in range(gridDimensions):
                idx = row * gridDimensions + col
 
                viewport[:] = []
                viewport.append(float(col) * rendererSize / (gridDimensions * rendererSize))
                viewport.append(float(gridDimensions - (row+1)) * rendererSize / (gridDimensions * rendererSize))
                viewport.append(float(col+1)*rendererSize / (gridDimensions * rendererSize))
                viewport.append(float(gridDimensions - row) * rendererSize / (gridDimensions * rendererSize))
 
                if idx > (len(sources) - 1):
                    continue
 
                renderers[idx].SetViewport(viewport)
                renderWindow.AddRenderer(renderers[idx])
 
                renderers[idx].AddActor(actors[idx])
                renderers[idx].AddActor(textactors[idx])
                renderers[idx].SetBackground(0.4,0.3,0.2)
 
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderWindow)
 
        renderWindow.Render()
 
        interactor.Start()
 
        c = vtk.vtkCurvatures()
        c = curvatures[0]
        print c.GetOutput().GetPointData().GetScalars()
 
    def compute_curvatures(self, vertices):
 
        pts = vtk.vtkPoints()
        tris = vtk.vtkCellArray()
        polys = vtk.vtkPolyData()
        
        for v in vertices:
            pts.InsertNextPoint(v[0], v[1], v[2])
        
        fIndex = 0
        for k in range(len(vertices)):
            if k % 3 == 0:
                poly = vtk.vtkPolygon()
                x = 0
                for i in range(3):
                    poly.GetPointIds().InsertId(x,k + x)
                    x+=1
                tris.InsertNextCell(poly.GetPointIds())
            
        polys.SetPoints(pts)
        polys.SetPolys(tris)
        polys.Update()
        
        print "Vertices: " + str(len(vertices))
        print "Faces: " + str(tris.GetNumberOfCells())
        
        tri_2 = vtk.vtkTriangleFilter()
        tri_2.SetInput(polys)
 
        # The quadric has nasty discontinuities from the way the edges are generated
        # so let's pass it though a CleanPolyDataFilter and merge any points which
        # are coincident, or very close
        cleaner_2 = vtk.vtkCleanPolyData()
        cleaner_2.SetInputConnection(tri_2.GetOutputPort())
        cleaner_2.SetTolerance(0.005)
        
        # Now we have the sources, lets put them into a list.
        sources = list()
        sources.append(cleaner_2)
        sources.append(cleaner_2)
        sources.append(cleaner_2)
        sources.append(cleaner_2)
 
        # Colour transfer function.
        ctf = vtk.vtkColorTransferFunction()
        ctf.SetColorSpaceToDiverging()
        ctf.AddRGBPoint(0.0, 0.230, 0.299, 0.754)
        ctf.AddRGBPoint(1.0, 0.706, 0.016, 0.150)
        cc = list()
        for i in range(256):
            cc.append(ctf.GetColor(float(i) / 255.0)) 
 
        # Lookup table.
        lut = list()
        for idx in range(len(sources)):
            lut.append(vtk.vtkLookupTable())
            lut[idx].SetNumberOfColors(256)
            for i, item in enumerate(cc):
                lut[idx].SetTableValue(i, item[0], item[1], item[2], 1.0)
            if idx == 0:
                lut[idx].SetRange(-10, 10)
            if idx == 1:
                lut[idx].SetRange(-10, 10)
            if idx == 2:
                lut[idx].SetRange(-10, 10)
            if idx == 3:
                lut[idx].SetRange(0, 4)
            lut[idx].Build()
 
        curvatures = list()        
        curvatures.append(vtk.vtkCurvatures())
        curvatures.append(vtk.vtkCurvatures())
        curvatures.append(vtk.vtkCurvatures())
        curvatures.append(vtk.vtkCurvatures())
        
        curvatures[0].SetCurvatureTypeToMaximum()
        curvatures[1].SetCurvatureTypeToMinimum()
        curvatures[2].SetCurvatureTypeToGaussian()
        curvatures[3].SetCurvatureTypeToMean()
        
        # Link the pipeline together. 
        for idx, item in enumerate(sources):
            sources[idx].Update()
            curvatures[idx].SetInputConnection(sources[idx].GetOutputPort())
            curvatures[idx].Update()
            
        c = vtk.vtkCurvatures()
        c = curvatures[0]
        curvMax = c.GetOutput().GetPointData().GetScalars()
        
        hist_4 = createHistogram(4, curvMax)
        hist_8 = createHistogram(8, curvMax)
        hist_16 = createHistogram(16, curvMax)
        
        return (hist_4, hist_8, hist_16)

def createHistogram(bin_num, array):
    K_max_max = array.GetDataTypeMin()
    K_max_min = array.GetDataTypeMax()
    tuples = array.GetNumberOfTuples()
    for x in range(tuples):
        if(array.GetValue(x) > K_max_max):
            K_max_max = array.GetValue(x)
        if(array.GetValue(x) < K_max_min):
            K_max_min = array.GetValue(x)

    range_h = K_max_max - K_max_min
    step_h = range_h / float(bin_num)
    boundaries_h = [[], ] * bin_num
    hist_h_values = [0, ] * bin_num
    for x in range(bin_num):
        boundaries_h[x] = [ K_max_min + x * step_h, K_max_min + (x + 1) * step_h ]

    print "Boundaries_" + str(bin_num) + ": " + str(boundaries_h)
    for x in range(tuples):
        val = array.GetValue(x)
        for i in range(bin_num):
            if ( val > boundaries_h[i][0] and val < boundaries_h[i][1] ):
                hist_h_values[i] += 1
    print "Boundaries_" + str(bin_num) + ": " + str(hist_h_values)
    
    return (boundaries_h, hist_h_values)
       
if __name__ == "__main__":
    
    m = mMesh(True)
    m.loadJSONModel('../../res/chairs/json', '101')
    
    segments_obb = []
    for s in m.segmentVertices:
        vertices = numpy.zeros ((len(s), 3), 'f')
        
        vIndex = 0
        for idx in s:
            vertices[vIndex, 0] = m.vertices[idx[0], 0]
            vertices[vIndex, 1] = m.vertices[idx[0], 1]
            vertices[vIndex, 2] = m.vertices[idx[0], 2]
            vIndex += 1
        
        segments_obb.append(vertices)
    
    po = CurvaturesDemo()
    for seg in segments_obb:
        po.compute_curvatures(seg)
        print "---"