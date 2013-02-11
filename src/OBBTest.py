'''
Created on 08/feb/2013

@author: Christian
'''

import sys
import numpy

vertices = numpy.load("../res/chairs/json/102_v.npy")
'''
vertices = [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0]
            ]
'''
covariance_matrix = numpy.zeros((3, 3), 'f')

E_x = 0.0
E_y = 0.0
E_z = 0.0

E_xx = 0.0
E_xy = 0.0
E_xz = 0.0

E_yx = 0.0
E_yy = 0.0
E_yz = 0.0

E_zx = 0.0
E_zy = 0.0
E_zz = 0.0

vertex_count = len(vertices)
print "Vertices: " + str(vertex_count)
for i in range(len(vertices)):
    E_x += vertices[i][0]
    E_y += vertices[i][1]
    E_z += vertices[i][2]
    
    E_xx += vertices[i][0] * vertices[i][0]
    E_xy += vertices[i][0] * vertices[i][1]
    E_xz += vertices[i][0] * vertices[i][2]
    
    E_yx += vertices[i][1] * vertices[i][0]
    E_yy += vertices[i][1] * vertices[i][1]
    E_yz += vertices[i][1] * vertices[i][2]
    
    E_zx += vertices[i][2] * vertices[i][0]
    E_zy += vertices[i][2] * vertices[i][1]
    E_zz += vertices[i][2] * vertices[i][2]
    
E_x /= vertex_count
E_y /= vertex_count
E_z /= vertex_count

E_xx /= vertex_count
E_xy /= vertex_count
E_xz /= vertex_count

E_yx /= vertex_count
E_yy /= vertex_count
E_yz /= vertex_count

E_zx /= vertex_count
E_zy /= vertex_count
E_zz /= vertex_count

print "E_x: " + str(E_x)
print "E_y: " + str(E_y)
print "E_z: " + str(E_z)
print "E_xx: " + str(E_xx)
print "E_xy: " + str(E_xy)
print "E_xz: " + str(E_xz)
print "E_yx: " + str(E_yx)
print "E_yy: " + str(E_yy)
print "E_yz: " + str(E_yz)
print "E_zx: " + str(E_zx)
print "E_zy: " + str(E_zy)
print "E_zz: " + str(E_zz)

covariance_matrix[0][0] = E_xx - (E_x * E_x)
covariance_matrix[0][1] = E_xy - (E_x * E_y)
covariance_matrix[0][2] = E_xz - (E_x * E_z)
covariance_matrix[1][0] = E_yx - (E_y * E_x)
covariance_matrix[1][1] = E_yy - (E_y * E_y)
covariance_matrix[1][2] = E_yz - (E_y * E_z)
covariance_matrix[2][0] = E_zx - (E_z * E_x)
covariance_matrix[2][1] = E_zy - (E_z * E_y)
covariance_matrix[2][2] = E_zz - (E_z * E_z)

print "Covariance Matrix"
covariance_matrix = numpy.matrix(covariance_matrix, 'f')
print covariance_matrix

w, v = numpy.linalg.eig(covariance_matrix)

print "Eigenvalues: \n" + str(w)
print "Eigenvectors: \n" + str(v)

r = numpy.multiply( 1.0 / numpy.linalg.norm(v[0]) , v[0] )
u = numpy.multiply( 1.0 / numpy.linalg.norm(v[1]) , v[1] )
f = numpy.multiply( 1.0 / numpy.linalg.norm(v[2]) , v[2] )
print "r: " + str(r)
print "u: " + str(u)
print "f: " + str(f)

transformation_matrix = numpy.zeros((4, 4), 'f')

r = numpy.array(r)[0]
u = numpy.array(u)[0]
f = numpy.array(f)[0]

transformation_matrix[0][0] = r[0]
transformation_matrix[0][1] = u[0]
transformation_matrix[0][2] = f[0]
transformation_matrix[0][3] = 0.0

transformation_matrix[1][0] = r[1]
transformation_matrix[1][1] = u[1]
transformation_matrix[1][2] = f[1]
transformation_matrix[1][3] = 0.0

transformation_matrix[2][0] = r[2]
transformation_matrix[2][1] = u[2]
transformation_matrix[2][2] = f[2] 
transformation_matrix[2][3] = 0.0

transformation_matrix[3][0] = 0.0
transformation_matrix[3][1] = 0.0
transformation_matrix[3][2] = 0.0
transformation_matrix[3][3] = 1.0

transformation_matrix = numpy.matrix(transformation_matrix)

print "Transformation Matrix: \n" + str(transformation_matrix)

transformed_points = []
p_min = [sys.maxint, sys.maxint, sys.maxint]
p_max = [-1.0 * sys.maxint, -1.0 * sys.maxint, -1.0 * sys.maxint]

for i in range(len(vertices)):
    temp = [0.0, 0.0, 0.0]
    temp[0] = numpy.dot( r, vertices[i] )
    temp[1] = numpy.dot( u, vertices[i] )
    temp[2] = numpy.dot( f, vertices[i] )
    
    if temp[0] > p_max[0]:
        p_max[0] = temp[0]
    if temp[1] > p_max[1]:
        p_max[1] = temp[1]
    if temp[2] > p_max[2]:
        p_max[2] = temp[2]
        
    if temp[0] < p_min[0]:
        p_min[0] = temp[0]
    if temp[1] < p_min[1]:
        p_min[1] = temp[1]
    if temp[2] < p_min[2]:
        p_min[2] = temp[2]
    
    #transformed_points.append(temp)

p_max = numpy.array(p_max)
p_min = numpy.array(p_min)

print "p_max: " + str(p_max)
print "p_min: " + str(p_min)

delta = (p_max - p_min) / 2.0
p_cen = (p_max + p_min) / 2.0

print "delta: " + str(delta)
print "p_cen: " + str(p_cen)

print "derp: \n" + str(transformation_matrix[0:3,0:3])

t = p_cen * transformation_matrix[0:3,0:3]

t = numpy.array(t)[0]
print "t: " + str(t)

transformation_matrix[0,3] = t[0]
transformation_matrix[1,3] = t[1]
transformation_matrix[2,3] = t[2]
transformation_matrix[3,3] = 1.0

print "Transformation Matrix (end): \n" + str(transformation_matrix)
print "Transformation Matrix (end): \n" + str(transformation_matrix.tolist())

p = [0.0,] * 8

p[0] = (p_cen - r * delta[0] - u * delta[1] - f * delta[2]).tolist()
p[1] = (p_cen + r * delta[0] - u * delta[1] - f * delta[2]).tolist()
p[2] = (p_cen + r * delta[0] - u * delta[1] + f * delta[2]).tolist()
p[3] = (p_cen - r * delta[0] - u * delta[1] + f * delta[2]).tolist()
p[4] = (p_cen - r * delta[0] + u * delta[1] - f * delta[2]).tolist()
p[5] = (p_cen + r * delta[0] + u * delta[1] - f * delta[2]).tolist()
p[6] = (p_cen + r * delta[0] + u * delta[1] + f * delta[2]).tolist()
p[7] = (p_cen - r * delta[0] + u * delta[1] + f * delta[2]).tolist()

print "POINTS: " + str(p)

print "done!"