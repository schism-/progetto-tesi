'''
Created on 20/feb/2013

@author: Christian
'''

import numpy

def princomp(A,numpc=0):
    # computing eigenvalues and eigenvectors of covariance matrix
    M = (A-numpy.mean(A.T,axis=1)).T # subtract the mean (along columns)
    [latent,coeff] = numpy.linalg.eig(numpy.cov(M))
    p = numpy.size(coeff,axis=1)
    idx = numpy.argsort(latent) # sorting the eigenvalues
    idx = idx[::-1]       # in ascending order
    
    # sorting eigenvectors according to the sorted eigenvalues
    coeff = coeff[:,idx]
    latent = latent[idx] # sorting eigenvalues
    
    if numpc < p or numpc >= 0:
        coeff = coeff[:,range(numpc)] # cutting some PCs
    
    score = numpy.dot(coeff.T,M) # projection of the data in the new space
    
    return coeff,score,latent

art_f = open("./a-10_q8_v1.8.art", "r")
art_dt = numpy.dtype((numpy.ubyte, (10,10,35)))
art_n_arr = numpy.fromfile(art_f, art_dt)
art_n_arr = art_n_arr[0] 

fd_f = open("./a-10_q8_v1.8.fd", "r")
fd_dt = numpy.dtype((numpy.ubyte, (10,10,10)))
fd_n_arr = numpy.fromfile(fd_f, fd_dt)
fd_n_arr = fd_n_arr[0] 

cir_f = open("./a-10_q8_v1.8.cir", "r")
cir_dt = numpy.dtype((numpy.ubyte, (10,10)))
cir_n_arr = numpy.fromfile(cir_f, cir_dt)
cir_n_arr = cir_n_arr[0]

ecc_f = open("./a-10_q8_v1.8.ecc", "r")
ecc_dt = numpy.dtype((numpy.ubyte, (10,10)))
ecc_n_arr = numpy.fromfile(ecc_f, ecc_dt)
ecc_n_arr = ecc_n_arr[0]

#100 observations x 47 features variables
main_dt = numpy.dtype((numpy.ubyte, (100,47)))
main_matrix = numpy.zeros((100,47), dtype=numpy.ubyte)
for x in range(10):
    for y in range(10):
        main_idx = 10 * y + x
        for art_idx in range(35):

            main_matrix[main_idx][art_idx] = art_n_arr[x][y][art_idx]
        for fd_idx in range(10):
            main_matrix[main_idx][35 + fd_idx] = fd_n_arr[x][y][fd_idx]
        
        main_matrix[main_idx][45] = cir_n_arr[x][y]
        main_matrix[main_idx][46] = ecc_n_arr[x][y]
            
full_pc = numpy.size(main_matrix, axis=1)

coeff, score, latent = princomp(main_matrix,full_pc)

print "Coeff: " + str(coeff)
print "Score: " + str(score)
print "Latent: " + str(latent)