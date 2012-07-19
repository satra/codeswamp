# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Cleaning up MPRAGEs collected with prescan normalize
# 
# Import image loading functions
# ------------------------------

# <codecell>

from nibabel import load, Nifti1Image

# <markdowncell>

# Load in the uncorrected image

# <codecell>

img = load('006-MEMPRAGE_4e_p2_1mm_iso.nii.gz')
data = img.get_data()

# <markdowncell>

# Compute and overlay histograms on the image data

# <codecell>

hgrams = np.zeros((data.shape[0], 128))
for i in range(data.shape[0]):
    foo = data[i, :, :]
    x, bins = histogram(foo[foo>100], 128)
    hgrams[i,:] = log(x)
clf()
imshow(data[:,128,:].T, cmap=cm.gray)
imshow(hgrams.T, interpolation='nearest')
imshow(data[:,128,:].T, alpha=0)

# <markdowncell>

# Compute histograms to show that there is not really much intensity distribution difference between the off slices.

# <codecell>

h1,_ = histogram(data[80,:,128:].ravel(),128)
h2,_ = histogram(data[105,:,128:].ravel(),128)
plot(vstack((h1,h2)).T)

# <markdowncell>

# The correction algorithm
# ------------------------
# 
# Compute an intensity profile cutting across sagittal slices and determine a scaling factor for each slice. You can vary the 0.85 to determine a best correction.

# <codecell>

wmout = np.zeros((10, 176))
correction_factor = 0.85
axial_slices = range(115, 125)
axial_profile_slices = range(150, 190)
for idx, sl in enumerate(axial_slices):
    wm = np.max(data[:, sl, axial_profile_slices], axis=1).astype('float')
    wm = correction_factor*(wm/np.max(wm))-0.5
    wm = 1-wm*(wm>0)
    wmout[idx,:] = wm
wm = np.median(wmout, axis=0)
plot(wm)

# <markdowncell>

# Apply scaling factor to each slice.

# <codecell>

data2 = np.zeros(data.shape)
for i in range(data.shape[0]):
    data2[i,:,:] = wm[i]*data[i, :, :]
imshow(data2[:, 128, :].T, cmap=cm.gray)

# <markdowncell>

# Display intensity profile after correction

# <codecell>

wm = np.max(data2[:, 119, 150:190], axis=1).astype('float')
wm = (wm/np.max(wm))
#wm = 1-wm*(wm>0)
plot(wm)

# <markdowncell>

# Write out corrected image.

# <codecell>

outimg = Nifti1Image(data2, img.get_affine(), img.get_header())
outimg.to_filename('corrected.nii.gz')

