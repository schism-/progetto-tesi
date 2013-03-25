'''
Created on 25/mar/2013

@author: Christian
'''

from os import walk
import numpy

def createHistogram(bin_num, array):
    arr_max = max(array)
    arr_min = min(array)
    
    range_h = arr_max - arr_min
    step_h = range_h / float(bin_num)
    boundaries_h = [[], ] * bin_num
    hist_h_values = [0, ] * bin_num
    for x in range(bin_num):
        boundaries_h[x] = [ arr_min + x * step_h, arr_min + (x + 1) * step_h ]

    #print "Boundaries_" + str(bin_num) + ": " + str(boundaries_h)
    for x in array:
        for i in range(bin_num):
            if ( x > boundaries_h[i][0] and x < boundaries_h[i][1] ):
                hist_h_values[i] += 1
    #print "Boundaries_" + str(bin_num) + ": " + str(hist_h_values)
    
    return (boundaries_h, hist_h_values)

if __name__ == "__main__":
    directory = "../res/chairs/data/1/"
    
    #Check dei sdf files
    f = []
    for (dirpath, dirname, filenames) in walk(directory):
        f.extend(filenames)
        break
    
    for file in f:
        filename_parts = file.split('.') 
        if filename_parts[-2] == 'sdf':
            
            sdf = open(directory + file)
            sdf_values = []
            for line in sdf:
                sdf_values.append(float(line))
            
            _, hist_4 = createHistogram(4, sdf_values)
            _, hist_8 = createHistogram(8, sdf_values)
            _, hist_16 = createHistogram(16, sdf_values)

            hist_4 = numpy.array(hist_4)
            hist_8 = numpy.array(hist_8)
            hist_16 = numpy.array(hist_16)
            
            path = filename_parts[0].split('_')
            path = directory + "_".join([path[0], path[1]]) + "/" + "_".join([path[2], path[3]]) + "/"
            
            numpy.save(path + "sd_hist4", hist_4)
            numpy.save(path + "sd_hist8", hist_8)
            numpy.save(path + "sd_hist16", hist_16)
                
        
        elif filename_parts[-2] == 'log':
            pass
        
    print "done!"