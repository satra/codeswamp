from nipype.algorithms.modelgen import SpecifySparseModel
from nipype.interfaces.base import Bunch
from nibabel import Nifti1Image, Nifti1Header

import numpy as np

x,y,z,t = (64,64,32,30)


mask = np.zeros((x,y,z,t))
mask.shape = x,y,z,t
mask = mask.astype(np.int16)

roigrid = np.mgrid[10:20,10:20,10:15]

mask[roigrid[0].ravel(), roigrid[1].ravel(), roigrid[2].ravel(), :] = 1

maskimg = Nifti1Image(mask, np.eye(4))
maskimg.get_header().set_xyzt_units('mm','sec')
maskimg.to_filename('mask.nii')


s = SpecifySparseModel()
s.inputs.input_units = 'secs'
s.inputs.functional_runs = ['mask.nii']
s.inputs.time_repetition = 2.
s.inputs.time_acquisition = s.inputs.time_repetition
s.inputs.high_pass_filter_cutoff = 128.
s.inputs.model_hrf = True
info = [Bunch(conditions=['cond1'], onsets=[[2, 10, 21, 25]], durations=[[1]])]
s.inputs.subject_info = info
res = s.run()

hrf_data = np.array(res.outputs.session_info[0]['regress'][0]['val'])
hrf_data_plot = hrf_data + 0.2*(np.random.rand(len(hrf_data))-0.5) # not adding
# gaussian noise

activations = np.tile(70*hrf_data, ( len(roigrid[0].ravel()), 1)) + 70*(2*np.random.rand(500,1)-1)
act_data = 7000 + 5*np.random.randn(x,y,z,t)
act_data[roigrid[0].ravel(), roigrid[1].ravel(), roigrid[2].ravel(),:] += activations
act_data = act_data.astype(np.int16)
actimg = Nifti1Image(act_data, np.eye(4))
actimg.get_header().set_xyzt_units('mm','sec')
actimg.to_filename('functional.nii')
