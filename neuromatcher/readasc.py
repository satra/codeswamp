
from glob import glob
import os
import re
import subprocess

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.mlab import PCA
import numpy as np

# choose one of the following
#pattern = ';.*R[^o]' # skip Root labels
pattern = ';.*R' # use Root + R labels

# set to True if you want a normed histogram (pdf sums to 1)
normed=True


def read_ASCbp(fname):
    """ Read labeled nodes from ASC file
    """
    if not os.path.exists(fname):
        raise Exception('File %s not found in current directory'%fname)
    xyz = []
    names = []
    for line in open(fname,'rt'):
        if re.search(pattern, line):
            xyz.append([float(val) for val in line.split(')')[0].split()[1:4]])
            names.append(line.split()[-1])
    xyz = np.array(xyz)
    names = np.array(names)
    return xyz, names

def plot3(xyz):
    """Scatter plot on a 3d axis

    Example
    -------

    plt.gcf().add_subplot(111, projection='3d')
    plot3(xyz)
    
    """
    ax = plt.gca()
    ax.scatter(xyz[:,0],xyz[:,1],xyz[:,2],c='r',marker='x')
    ax.set_xlim3d(np.min(xyz,axis=0)[0], np.max(xyz,axis=0)[0])
    ax.set_ylim3d(np.min(xyz,axis=0)[1], np.max(xyz,axis=0)[1])
    ax.set_zlim3d(np.min(xyz,axis=0)[2], np.max(xyz,axis=0)[2])


# get all ASC files in the directory
ascfiles = glob('*.ASC')

data = []
fingerprints = np.zeros((128,len(ascfiles)))
for idx, fname in enumerate(ascfiles):
    data.append(dict(name=fname))
    data[idx]['xyz'],data[idx]['nodenames'] = read_ASCbp(fname)
    xyzpc = PCA(data[idx]['xyz'])
    data[idx]['xyzpc'] = xyzpc.Y
    plt.gcf().add_subplot(3,len(ascfiles),idx+1, projection='3d')
    plt.title(fname)
    plot3(data[idx]['xyzpc'])
    plt.subplot(3,len(ascfiles),len(ascfiles)+idx+1)
    n,bins,_ = plt.hist(data[idx]['xyzpc'][:,0],bins=128, range=[-4,4],color=np.random.rand(1,3),normed=normed)
    fingerprints[:,idx] = n
    plt.subplot(3,1,3)
    plt.hist(data[idx]['xyzpc'][:,0],bins=128,color=np.random.rand(1,3),alpha=0.5,normed=normed)

plt.figure()
plt.imshow(np.corrcoef(fingerprints.transpose()), interpolation='nearest')
plt.colorbar()
