#! /usr/bin/env python

import os,sys
import numpy as np
import pylab as py

def main(argv):
    '''
        Playing with hierachical distance estimations in order to idendify 
        clustering of data points. The idea is that this can be used to identify
        cluster of stars in database.
        
        This is just a preview test.
    '''
    
    # Create random position and magnitude of stars
    SIZE1=1000
    SIZE2=100
    xpos1=np.random.random(SIZE1)*10
    ypos1=np.random.random(SIZE1)*10
    mag1 = np.random.random(len(xpos1))
    avgdist1 = np.zeros(len(xpos1))
    stddist1 = np.zeros(len(xpos1))
    
    xpos2=np.random.exponential(0.5,SIZE2)*(-1)**np.random.randint(0,2,SIZE2)+0.5
    ypos2=np.random.exponential(0.5,SIZE2)*(-1)**np.random.randint(0,2,SIZE2)+0.5
    mag2 = np.random.random(len(xpos2))
    avgdist2 = np.zeros(len(xpos2))
    stddist2 = np.zeros(len(xpos2))

    xpos = np.append(xpos1,xpos2)
    ypos = np.append(ypos1,ypos2)
    mag =  np.append(mag1,mag2) #np.random.random(len(xpos))
    avgdist = np.zeros(len(xpos))
    stddist = np.zeros(len(xpos))
    mran = np.linspace(0,1,5)

    py.figure(1)
    
    for i in range(len(mran)-1):
        mask = np.bitwise_and(mag>mran[i],mag<mran[i+1])
        py.plot(xpos[mask],ypos[mask],'.')

    for i in range(len(xpos)):
        #mdist = np.abs(mag[i] - mag)
        #mindx = mdist.argsort()[1:11]
        dist = np.sqrt( (xpos[i] - xpos)**2.0 +
                        (ypos[i] - ypos)**2.0)
        dindx = dist.argsort()[1:11]
        avgdist[i] = np.mean(dist[dindx])
        stddist[i] = np.std(dist[dindx])

    for i in range(len(xpos1)):
        #mdist = np.abs(mag1[i] - mag1)
        #mindx = mdist.argsort()[1:11]
        dist = np.sqrt( (xpos1[i] - xpos1)**2.0 +
                       (ypos1[i] - ypos1)**2.0)

        dindx = dist.argsort()[1:11]
        avgdist1[i] = np.mean(dist[dindx])
        stddist1[i] = np.std(dist[dindx])

    for i in range(len(xpos2)):
        #mdist = np.abs(mag2[i] - mag2)
        #mindx = mdist.argsort()[1:11]
        dist = np.sqrt( (xpos2[i] - xpos2)**2.0 +
                       (ypos2[i] - ypos2)**2.0)
        dindx=dist.argsort()[1:11]
        avgdist2[i] = np.mean(dist[dindx])
        stddist2[i] = np.std(dist[dindx])

    py.figure(2)
    py.hist(avgdist,bins=10)
    py.hist(avgdist1,bins=10)
    py.hist(avgdist2,bins=10)

    py.show()

if __name__ == '__main__':

    main(sys.argv)

