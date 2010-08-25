#!/usr/bin/env python
import os
import numpy as np
from nipype.externals.pynifti import load
from glob import glob

if __name__ == "__main__":
    basedir = '/mindhive/nklab/projects/ellison/fMRI/neuroanat'
    dtidir = os.path.join(basedir,'dti')
    subjdirs = glob(os.path.join(dtidir,'ellKid*','dtrecon'))
    subjdirs.extend(glob(os.path.join(dtidir,'ek*','dtrecon')))
    subjdirs = sorted(subjdirs)
    index = []
    for sd in subjdirs:
        sid = sd.split('/')[-2]
        dtiimg = glob(os.path.join(sd,'dwi-ec.nii'))
        subjdir = os.path.join(dtidir,sid,'tvrecon')
        gradient_table = '/software/Freesurfer/current/diffusion/mgh-dti-seqpack/gradient_mgh_dti30.gdt'
        if len(dtiimg)==1 and (not (os.path.exists(subjdir) or len(gradient_table)==0)):
            queuename = 'satra'
            if len(dtiimg)>0:
                index.append(sid)
                anglethresh = 35
                reconprefix = os.path.join(subjdir,'%s'%sid)
                trackdir    = os.path.join(subjdir,'dtk_%d'%anglethresh)
                mask_file   = ''.join((reconprefix,'_dwi.nii.gz'))
                temp_track  = os.path.join(trackdir,'track_tmp.trk')
                out_track   = os.path.join(trackdir,''.join((sid,'_%d.trk'%anglethresh)))
                reconcmd = '/software/dtk0.5/dti_recon %s %s -gm %s '\
                    '-b 700 -b0 5 -oc -p 3 -sn 1 '\
                    '-ot nii.gz'%(dtiimg[0],
                                  reconprefix,
                                  gradient_table)
                trackcmd = '/software/dtk0.5/dti_tracker %s %s -at %d '\
                    '-m %s --fact -it nii.gz'%(reconprefix,
                                               temp_track,
                                               anglethresh,
                                               mask_file)
                filtcmd  = '/software/dtk0.5/spline_filter %s 1 %s'%(temp_track,
                                                    out_track)
                dtrcmd   = ';'.join((reconcmd,trackcmd,filtcmd))
                outcmd = 'ezsub.py -n sg-%s -q %s -c \"%s\"'%(sid,queuename,dtrcmd)
                print outcmd
                os.makedirs(trackdir)
                os.system(outcmd)
        else:
            print "%s exists. remove to rerun"%subjdir
    print "submitted %d subjects"%len(index)
    print index

"""
dti_recon "/mindhive/nklab/projects/ellison/fMRI/neuroanat/nifti/ellKid001/265000-26-1.nii.gz" "/tmp/dti_35" -gm "/tmp/dtk_tmp/matrices/gradient.txt" -b 700 -b0 5 -oc  -p 3 -sn 1 -ot nii.gz

2.
dti_tracker "/tmp/dti_35" "/tmp/dtk_tmp/track_tmp.trk" -at 35   -m "/tmp/dti_35_dwi.nii.gz" --fact -it nii.gz

3.
spline_filter "/tmp/dtk_tmp/track_tmp.trk" 1 "/tmp/dti_35.trk"
"""
