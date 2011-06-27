from glob import glob
import os
import shutil
from time import strptime, strftime

from PIL import Image
from PIL.ExifTags import TAGS
 
def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

src_dir = '/Users/satra/Documents/india2010'
out_dir = '/Users/satra/Desktop/SORTED'

#for filename in  glob(os.path.join(src_dir,'*.jpg')):
#    dateinfo = get_exif(filename)['DateTime']
for filename in  glob(os.path.join(src_dir,'*.JPG')):
    dateinfo = get_exif(filename)['DateTimeOriginal']
    folder = strftime('%y%m%d',strptime(dateinfo,'%Y:%m:%d %H:%M:%S'))
    timeinfo = strftime('%H%M%S',strptime(dateinfo,'%Y:%m:%d %H:%M:%S'))
    outfolder = os.path.join(out_dir,folder)
    _, fname = os.path.split(filename)
    newfname = os.path.join(outfolder,'%sT%s_%s'%(folder,timeinfo,fname))
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    shutil.move(filename, newfname)
    print 'copying:', newfname

'''
for filename in  glob(os.path.join(out_dir, '*', '*.JPG')):
    dateinfo = get_exif(filename)['DateTimeOriginal']
    timeinfo = strftime('%H%M%S',strptime(dateinfo,'%Y:%m:%d %H:%M:%S'))
    path, fname =  os.path.split(filename)
    outfname = fname.replace('_', 'T%s_'%timeinfo)
    newfname = os.path.join(path, outfname)
    shutil.move(filename, newfname)
    print 'copying:', filename, newfname
'''
