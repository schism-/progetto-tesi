'''
Created on 08/mar/2013

@author: Christian
'''

import os

def writeofffile(offpath, vertices, faces):
    try:
        fi = open(offpath, 'w')
    except IOError:
        print "Error"
        
    fi.write("OFF\n")
    fi.write(str(len(vertices)) + " " + str(len(faces)) + " 0\n")
    
    for v in vertices:
        fi.write(str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")
        
    for f in faces:
        fi.write("3 " + str(f[0]) + " " + str(f[1]) + " " + str(f[2]) + "\n")

    fi.close()
    
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

if __name__ == "__main__":
    name_list = ['1', '2', '3', '4', '42']
    for name in name_list:
        vertices, faces = readofffile("./../res/tele-aliens/shapes/"+ name +".off")
        
        #Computing centroid for model
        x_sum, y_sum, z_sum = 0.0, 0.0, 0.0
        
        for v in vertices:
            x_sum += v[0]
            y_sum += v[1]
            z_sum += v[2]
            
        centroid = [ x_sum / len(vertices), y_sum / len(vertices), z_sum / len(vertices) ]
        
        for v in vertices:
            v[0] -= centroid[0]
            v[1] -= centroid[1]
            v[2] -= centroid[2]
            
        writeofffile("./../res/tele-aliens/shapes/"+ name +"_m.off", vertices, faces)