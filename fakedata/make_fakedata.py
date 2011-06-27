from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from nibabel import Nifti1Image, Nifti1Header
from nipype.algorithms.modelgen import spm_hrf
import pylab

 
def montage(X, colormap=pylab.cm.gist_gray):    
    from numpy import array,flipud,shape,zeros,rot90,ceil,floor,sqrt
    from scipy import io,reshape,size
    m, n, count = shape(X)    
    mm = int(ceil(sqrt(count)))
    nn = mm
    M = zeros((mm * m, nn * n))
    image_id = 0
    for j in range(mm):
        for k in range(nn):
            if image_id >= count: 
                break
            sliceM, sliceN = j * m, k * n
            M[sliceN:sliceN + n, sliceM:sliceM + m] = X[:, :, image_id]
            image_id += 1
    pylab.imshow(flipud(rot90(M)), cmap=colormap)
    pylab.axis('off')             
    return M

TR = 2.
offset = 30
trial_timing = np.array([2, 4, 8, 4, 2, 2, 8])
trial_amp = np.array([0, 0, 1, 0, 0, 0, 0, 0])

dr = np.array([[1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0],
      [0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1],
      [0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
      [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1],
      [0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0],
      [0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
      [1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1],
      [0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0]])

num_runs, num_trials = dr.shape

x,y,z = (64,64,32)

mask = np.zeros((x,y,z))
mask.shape = x,y,z,1
reference = np.zeros((x,y,z))
reference.shape = x,y,z,1

roigrid = np.mgrid[10:20,10:20,10:15]
refgrid = np.mgrid[40:50,40:50,20:25]

mask[roigrid[0].ravel(), roigrid[1].ravel(), roigrid[2].ravel()] = 1
reference[refgrid[0].ravel(), refgrid[1].ravel(), refgrid[2].ravel()] = 1

mask = mask.astype(np.int16)
reference = reference.astype(np.int16)

maskimg = Nifti1Image(mask, np.eye(4))
maskimg.get_header().set_xyzt_units('mm','sec')
refimg = Nifti1Image(reference, np.eye(4))
refimg.get_header().set_xyzt_units('mm','sec')

maskimg.to_filename('roi.nii')
refimg.to_filename('reference.nii')


for i in range(num_runs):
    if i in [0,7]:
        tt = trial_timing[[0,1,2,3,6]]
        level = (2*dr[i]-1)*0.2*(i+1)
    else:
        level = 0.2*i*dr[i] + 0.2*i*(dr[i]-1) + 0.2*(np.cumsum(dr[i])*dr[i] + np.cumsum(1-dr[i])*(dr[i]-1))/6
        tt = trial_timing
    n_points = (offset + num_trials*np.sum(tt))/TR
    print n_points
    trial = np.zeros(np.sum(tt)/TR)
    trial[range((np.cumsum(tt)/TR)[1].astype(int), (np.cumsum(tt)/TR)[2].astype(int))] = 1
    run_data = np.dot(trial[:,None], level[:,None].T)
    data = np.concatenate((np.zeros(offset/TR), run_data.T.ravel()))
    hrf_data = np.convolve(data, spm_hrf(TR))[0:len(data)]
    hrf_data_plot = hrf_data + 0.2*(np.random.rand(len(hrf_data))-0.5) # not adding gaussian noise
    plt.subplot(num_runs, 1, i+1)
    plt.plot(100 + data)
    plt.plot(100 + hrf_data_plot, 'r')
    plt.ylim(100+np.array([-1.7, 1.7]))
    
    activations = np.tile(70*hrf_data, ( len(roigrid[0].ravel()), 1)) + 70*(2*np.random.rand(500,1)-1)
    act_data = 7000 + 5*np.random.randn(x,y,z,n_points)
    act_data[roigrid[0].ravel(), roigrid[1].ravel(), roigrid[2].ravel(),:] += activations
    act_data = act_data.astype(np.int16)
    actimg = Nifti1Image(act_data, np.eye(4))
    actimg.get_header().set_xyzt_units('mm','sec')
    actimg.to_filename('run%d.nii'%i)
plt.savefig('fakedata.png')

