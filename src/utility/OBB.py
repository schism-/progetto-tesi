'''
Created on 11/feb/2013

@author: Christian
'''

import sys
import numpy

class obb(object):
    
    @staticmethod
    def computeOBB(points):
        vertices = points
        
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
        
        return p
    
    @staticmethod
    def computeOBB_2_o(points):
        vertices = points
        
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

        A_t = 0.0
        mu = numpy.zeros((1,3), 'f')
        for i in range(len(vertices)):
            if i % 3 == 0:
                p = vertices[i]
                q = vertices[i + 1]
                r = vertices[i + 2]
                
                c = (p + q + r) / 3.0
                
                A_i = numpy.cross((q - p), (r - p))
                A_i = numpy.linalg.norm(A_i) / 2.0
                
                mu += c * A_i
                A_t += A_i
        
                E_xx += ( 9.0 * c[0] * c[0] + p[0] * p[0] + q[0] * q[0] + r[0] * r[0] ) * (A_i/12.0)
                E_xy += ( 9.0 * c[0] * c[1] + p[0] * p[1] + q[0] * q[1] + r[0] * r[1] ) * (A_i/12.0)
                E_xz += ( 9.0 * c[0] * c[2] + p[0] * p[2] + q[0] * q[2] + r[0] * r[2] ) * (A_i/12.0)
                
                E_yx += ( 9.0 * c[0] * c[1] + p[0] * p[1] + q[0] * q[1] + r[0] * r[1] ) * (A_i/12.0)
                E_yy += ( 9.0 * c[1] * c[1] + p[1] * p[1] + q[1] * q[1] + r[1] * r[1] ) * (A_i/12.0)
                E_yz += ( 9.0 * c[1] * c[2] + p[1] * p[2] + q[1] * q[2] + r[1] * r[2] ) * (A_i/12.0)
                
                E_zx += ( 9.0 * c[0] * c[2] + p[0] * p[2] + q[0] * q[2] + r[0] * r[2] ) * (A_i/12.0)
                E_zy += ( 9.0 * c[1] * c[2] + p[1] * p[2] + q[1] * q[2] + r[1] * r[2] ) * (A_i/12.0)
                E_zz += ( 9.0 * c[2] * c[2] + p[2] * p[2] + q[2] * q[2] + r[2] * r[2] ) * (A_i/12.0)
        
        mu /= A_t
        E_xx /= A_t
        E_xy /= A_t
        E_xz /= A_t
        
        E_yx /= A_t
        E_yy /= A_t
        E_yz /= A_t
        
        E_zx /= A_t
        E_zy /= A_t
        E_zz /= A_t
        
        E_xx -= mu[0,0] * mu[0,0] 
        E_xy -= mu[0,0] * mu[0,1] 
        E_xz -= mu[0,0] * mu[0,2]
        
        E_yx -= mu[0,1] * mu[0,0]
        E_yy -= mu[0,1] * mu[0,1] 
        E_yz -= mu[0,1] * mu[0,2]
         
        E_zx -= mu[0,2] * mu[0,0]
        E_zy -= mu[0,2] * mu[0,1]
        E_zz -= mu[0,2] * mu[0,2]
        
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
        
        covariance_matrix[0][0] = E_xx
        covariance_matrix[0][1] = E_xy
        covariance_matrix[0][2] = E_xz
        covariance_matrix[1][0] = E_yx
        covariance_matrix[1][1] = E_yy
        covariance_matrix[1][2] = E_yz
        covariance_matrix[2][0] = E_zx
        covariance_matrix[2][1] = E_zy
        covariance_matrix[2][2] = E_zz
        
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
        
        return p
    
    @staticmethod
    def computeOBB_2(points, faces):
        vertices = points
        
        A_i = 0.0
        A_m = 0.0        
        
        mu = numpy.zeros((1,3), 'f')
        mu_i = numpy.zeros((1,3), 'f')
        
        covariance_matrix = numpy.zeros((3, 3), 'f')
        
        E_xx = 0.0
        E_xy = 0.0
        E_xz = 0.0
        
        E_yy = 0.0
        E_yz = 0.0
        
        E_zz = 0.0
        
        for f in faces:
            p = vertices[f[0]]
            q = vertices[f[1]]
            r = vertices[f[2]]
            
            mu_i = (p + q + r) / 3.0
            
            temp = numpy.cross((q - p), (r - p)) 
            A_i = numpy.linalg.norm(temp)
            A_i /= 2.0
            
            mu += mu_i * A_i
            A_m += A_i
    
            E_xx += ( 9.0 * mu_i[0] * mu_i[0] + p[0] * p[0] + q[0] * q[0] + r[0] * r[0] ) * (A_i/12.0)
            E_xy += ( 9.0 * mu_i[0] * mu_i[1] + p[0] * p[1] + q[0] * q[1] + r[0] * r[1] ) * (A_i/12.0)
            E_xz += ( 9.0 * mu_i[0] * mu_i[2] + p[0] * p[2] + q[0] * q[2] + r[0] * r[2] ) * (A_i/12.0)
            
            
            E_yy += ( 9.0 * mu_i[1] * mu_i[1] + p[1] * p[1] + q[1] * q[1] + r[1] * r[1] ) * (A_i/12.0)
            E_yz += ( 9.0 * mu_i[1] * mu_i[2] + p[1] * p[2] + q[1] * q[2] + r[1] * r[2] ) * (A_i/12.0)
            
            E_zz += ( 9.0 * mu_i[2] * mu_i[2] + p[2] * p[2] + q[2] * q[2] + r[2] * r[2] ) * (A_i/12.0)
        
        mu /= A_m
        E_xx /= A_m
        E_xy /= A_m
        E_xz /= A_m
        
        E_yy /= A_m
        E_yz /= A_m

        E_zz /= A_m
        
        E_xx -= mu[0,0] * mu[0,0] 
        E_xy -= mu[0,0] * mu[0,1] 
        E_xz -= mu[0,0] * mu[0,2]
        
        E_yy -= mu[0,1] * mu[0,1] 
        E_yz -= mu[0,1] * mu[0,2]
         
        E_zz -= mu[0,2] * mu[0,2]
        
#        print "E_x: " + str(mu[0,0])
#        print "E_y: " + str(mu[0,1])
#        print "E_z: " + str(mu[0,2])
#        print "E_xx: " + str(E_xx)
#        print "E_xy: " + str(E_xy)
#        print "E_xz: " + str(E_xz)
#        print "E_yx: " + str(E_xy)
#        print "E_yy: " + str(E_yy)
#        print "E_yz: " + str(E_yz)
#        print "E_zx: " + str(E_xz)
#        print "E_zy: " + str(E_yz)
#        print "E_zz: " + str(E_zz)
        
        covariance_matrix[0][0] = E_xx
        covariance_matrix[0][1] = E_xy
        covariance_matrix[0][2] = E_xz
        covariance_matrix[1][0] = E_xy
        covariance_matrix[1][1] = E_yy
        covariance_matrix[1][2] = E_yz
        covariance_matrix[2][0] = E_xz
        covariance_matrix[2][1] = E_yz
        covariance_matrix[2][2] = E_zz
        
#        print "Covariance Matrix"
        covariance_matrix = numpy.matrix(covariance_matrix, 'f')
#        print covariance_matrix
        
        w, v = numpy.linalg.eig(covariance_matrix)
        
#        print "Eigenvalues: \n" + str(w)
#        print "Eigenvectors: \n" + str(v)
        
        #Computing needed features from eigenvalues
        eigen_features = []
        s1 = float(w[0])
        s2 = float(w[1])
        s3 = float(w[2])
        s_tot = float(s1 + s2 + s3)
        
        eigen_features.append( s1 / s_tot )
        eigen_features.append( s2 / s_tot )
        eigen_features.append( s3 / s_tot )
        eigen_features.append( (s1 + s2) / s_tot )
        eigen_features.append( (s1 + s3) / s_tot )
        eigen_features.append( (s2 + s3) / s_tot )
        eigen_features.append( s1 / s2 )
        eigen_features.append( s1 / s3 )
        eigen_features.append( s2 / s3 )
        eigen_features.append( s1 / s2 + s1 / s3 )
        eigen_features.append( s1 / s2 + s2 / s3 )
        eigen_features.append( s1 / s3 + s2 / s3 )
        
#        print "Eigen features: \n" + str(eigen_features)
        
        r = numpy.array([0.0, 0.0, 0.0], 'f')
        u = numpy.array([0.0, 0.0, 0.0], 'f')
        f = numpy.array([0.0, 0.0, 0.0], 'f')
        
#        print "Eigenvectors0: \n" + str(v[0])
#        print "Eigenvectors1: \n" + str(v[1])
#        print "Eigenvectors2: \n" + str(v[2])
        
#        print "R: \n" + str(r)
#        print "U: \n" + str(u)
#        print "F: \n" + str(f)
        
        r[0] = v[0,0]
        r[1] = v[1,0]
        r[2] = v[2,0]
        
        u[0] = v[0,1]
        u[1] = v[1,1]
        u[2] = v[2,1]
        
        f[0] = v[0,2]
        f[1] = v[1,2]
        f[2] = v[2,2]
        
        r /= numpy.linalg.norm(r)
        u /= numpy.linalg.norm(u)
        f /= numpy.linalg.norm(f)
        
#        print "r: " + str(r)
#        print "u: " + str(u)
#        print "f: " + str(f)
        
        transformation_matrix = numpy.zeros((3, 3), 'f')
        
        transformation_matrix[0,0] = r[0]
        transformation_matrix[0,1] = u[0]
        transformation_matrix[0,2] = f[0]
        
        transformation_matrix[1,0] = r[1]
        transformation_matrix[1,1] = u[1]
        transformation_matrix[1,2] = f[1]
        
        transformation_matrix[2,0] = r[2]
        transformation_matrix[2,1] = u[2]
        transformation_matrix[2,2] = f[2] 
        
#        print "Transformation Matrix: \n" + str(transformation_matrix)
        
        p_min = [1e10, 1e10, 1e10]
        p_max = [-1e10, -1e10, -1e10]
        
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
       
        p_max = numpy.array(p_max)
        p_min = numpy.array(p_min)
        
#        print "p_max: " + str(p_max)
#        print "p_min: " + str(p_min)
        
        delta = (p_max - p_min) / 2.0
        p_cen = (p_max + p_min) / 2.0
        
        translation = [0.0, 0.0, 0.0]
        translation[0] = numpy.dot( transformation_matrix[0], p_cen )
        translation[1] = numpy.dot( transformation_matrix[1], p_cen )
        translation[2] = numpy.dot( transformation_matrix[2], p_cen )
        translation = numpy.array(translation)
        
        p = [0.0,] * 8
        p[0] = (translation - r * delta[0] - u * delta[1] - f * delta[2]).tolist()
        p[1] = (translation + r * delta[0] - u * delta[1] - f * delta[2]).tolist()
        p[2] = (translation + r * delta[0] - u * delta[1] + f * delta[2]).tolist()
        p[3] = (translation - r * delta[0] - u * delta[1] + f * delta[2]).tolist()
        p[4] = (translation - r * delta[0] + u * delta[1] - f * delta[2]).tolist()
        p[5] = (translation + r * delta[0] + u * delta[1] - f * delta[2]).tolist()
        p[6] = (translation + r * delta[0] + u * delta[1] + f * delta[2]).tolist()
        p[7] = (translation - r * delta[0] + u * delta[1] + f * delta[2]).tolist()
        
#        print "POINTS: " + str(p)
#        print "done!"
        
        return [p, eigen_features]